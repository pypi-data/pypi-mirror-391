"""Low level UDP client implementation for pymarstek."""

from __future__ import annotations

import asyncio
from contextlib import suppress
import ipaddress
import json
import logging
import socket
from typing import Any

try:
    import psutil  # type: ignore[import-not-found]
except Exception:  # noqa: BLE001 - optional dependency
    psutil = None  # type: ignore[assignment]

from .command_builder import discover
from .const import DEFAULT_UDP_PORT, DISCOVERY_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class MarstekUDPClient:
    """UDP client for communicating with Marstek devices."""

    def __init__(self, port: int = DEFAULT_UDP_PORT) -> None:
        self._port = port
        self._socket: socket.socket | None = None
        self._pending_requests: dict[int, asyncio.Future] = {}
        self._response_cache: dict[int, dict[str, Any]] = {}
        self._listen_task: asyncio.Task | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

        self._discovery_cache: list[dict[str, Any]] | None = None
        self._cache_timestamp: float = 0
        self._cache_duration: float = 30.0

        self._local_send_ip: str = "0.0.0.0"
        self._polling_paused: dict[str, bool] = {}
        self._polling_lock: asyncio.Lock = asyncio.Lock()

    async def async_setup(self) -> None:
        """Prepare the UDP socket."""
        if self._socket is not None:
            return

        self._loop = asyncio.get_running_loop()

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setblocking(False)
        sock.bind(("0.0.0.0", self._port))
        self._socket = sock
        _LOGGER.debug("UDP client bound to %s:%s", sock.getsockname()[0], sock.getsockname()[1])

    async def async_cleanup(self) -> None:
        """Close the UDP socket."""
        if self._listen_task and not self._listen_task.done():
            self._listen_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._listen_task
        if self._socket:
            self._socket.close()
            self._socket = None

    def _get_broadcast_addresses(self) -> list[str]:
        addresses = {"255.255.255.255"}
        if psutil is not None:
            try:
                for addrs in psutil.net_if_addrs().values():
                    for addr in addrs:
                        if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                            if getattr(addr, "broadcast", None):
                                addresses.add(addr.broadcast)
                            elif getattr(addr, "netmask", None):
                                try:
                                    network = ipaddress.IPv4Network(
                                        f"{addr.address}/{addr.netmask}", strict=False
                                    )
                                    addresses.add(str(network.broadcast_address))
                                except (ValueError, OSError):
                                    continue
            except OSError as err:
                _LOGGER.warning("Failed to obtain network interfaces: %s", err)
            try:
                local_ips = {
                    addr.address
                    for addrs in psutil.net_if_addrs().values()
                    for addr in addrs
                    if addr.family == socket.AF_INET
                }
                addresses -= local_ips
            except OSError:
                pass
        return list(addresses)

    def _is_cache_valid(self) -> bool:
        if self._discovery_cache is None:
            return False
        loop = self._loop or asyncio.get_running_loop()
        return (loop.time() - self._cache_timestamp) < self._cache_duration

    def clear_discovery_cache(self) -> None:
        self._discovery_cache = None
        self._cache_timestamp = 0

    async def _send_udp_message(self, message: str, target_ip: str, target_port: int) -> None:
        if not self._socket:
            await self.async_setup()
        assert self._socket is not None
        data = message.encode("utf-8")
        self._socket.sendto(data, (target_ip, target_port))
        _LOGGER.debug("Send: %s:%d | %s", target_ip, target_port, message)

    async def send_request(
        self,
        message: str,
        target_ip: str,
        target_port: int,
        timeout: float = 5.0,
        *,
        quiet_on_timeout: bool = False,
    ) -> dict[str, Any]:
        if not self._socket:
            await self.async_setup()
        assert self._socket is not None

        try:
            message_obj = json.loads(message)
            request_id = message_obj["id"]
        except (json.JSONDecodeError, KeyError) as exc:
            raise ValueError("Invalid message: missing id") from exc

        future: asyncio.Future = asyncio.Future()
        self._pending_requests[request_id] = future

        try:
            if not self._listen_task or self._listen_task.done():
                loop = self._loop or asyncio.get_running_loop()
                self._listen_task = loop.create_task(self._listen_for_responses())

            await self._send_udp_message(message, target_ip, target_port)
            return await asyncio.wait_for(future, timeout=timeout)
        except TimeoutError as err:
            if not quiet_on_timeout:
                _LOGGER.warning("Request timeout: %s:%d", target_ip, target_port)
            raise TimeoutError(f"Request timeout to {target_ip}:{target_port}") from err
        finally:
            self._pending_requests.pop(request_id, None)

    async def _listen_for_responses(self) -> None:
        assert self._socket is not None
        loop = self._loop or asyncio.get_running_loop()
        while True:
            try:
                data, addr = await loop.sock_recvfrom(self._socket, 4096)
                response_text = data.decode("utf-8")
                try:
                    response = json.loads(response_text)
                except json.JSONDecodeError:
                    response = {"raw": response_text}
                request_id = response.get("id") if isinstance(response, dict) else None
                _LOGGER.debug("Recv: %s:%d | %s", addr[0], addr[1], response)
                if request_id:
                    self._response_cache[request_id] = {
                        "response": response,
                        "addr": addr,
                        "timestamp": loop.time(),
                    }
                    future = self._pending_requests.pop(request_id, None)
                    if future and not future.done():
                        future.set_result(response)
            except asyncio.CancelledError:
                break
            except OSError as err:
                _LOGGER.error("Error receiving UDP response: %s", err)
                await asyncio.sleep(1)

    async def send_broadcast_request(self, message: str, timeout: float = DISCOVERY_TIMEOUT) -> list[dict[str, Any]]:
        if not self._socket:
            await self.async_setup()
        assert self._socket is not None

        try:
            message_obj = json.loads(message)
            request_id = message_obj["id"]
        except (json.JSONDecodeError, KeyError) as exc:
            _LOGGER.error("Invalid message for broadcast: %s", exc)
            return []

        responses: list[dict[str, Any]] = []
        loop = self._loop or asyncio.get_running_loop()
        start_time = loop.time()

        future: asyncio.Future = asyncio.Future()
        self._pending_requests[request_id] = future

        try:
            if not self._listen_task or self._listen_task.done():
                self._listen_task = loop.create_task(self._listen_for_responses())

            for address in self._get_broadcast_addresses():
                await self._send_udp_message(message, address, self._port)

            while (loop.time() - start_time) < timeout:
                cached = self._response_cache.pop(request_id, None)
                if cached:
                    responses.append(cached["response"])
                await asyncio.sleep(0.1)
        finally:
            self._pending_requests.pop(request_id, None)
        return responses

    async def discover_devices(self, use_cache: bool = True) -> list[dict[str, Any]]:
        if use_cache and self._is_cache_valid():
            assert self._discovery_cache is not None
            return self._discovery_cache.copy()

        devices: list[dict[str, Any]] = []
        seen_devices: set[str] = set()

        try:
            responses = await self.send_broadcast_request(discover())
        except OSError as err:
            _LOGGER.error("Device discovery failed: %s", err)
            responses = []

        loop = self._loop or asyncio.get_running_loop()

        for response in responses:
            result = response.get("result") if isinstance(response, dict) else None
            if not isinstance(result, dict):
                continue

            device_id = (
                result.get("ip")
                or result.get("ble_mac")
                or result.get("wifi_mac")
                or f"device_{int(loop.time())}_{hash(str(result)) % 10000}"
            )
            if device_id in seen_devices:
                continue
            seen_devices.add(device_id)

            devices.append(
                {
                    "id": result.get("id", 0),
                    "device_type": result.get("device", "Unknown"),
                    "version": result.get("ver", 0),
                    "wifi_name": result.get("wifi_name", ""),
                    "ip": result.get("ip", ""),
                    "wifi_mac": result.get("wifi_mac", ""),
                    "ble_mac": result.get("ble_mac", ""),
                    "mac": result.get("wifi_mac") or result.get("ble_mac", ""),
                    "model": result.get("device", "Unknown"),
                    "firmware": str(result.get("ver", 0)),
                }
            )

        self._discovery_cache = devices.copy()
        self._cache_timestamp = loop.time()
        return devices

    async def pause_polling(self, device_ip: str) -> None:
        async with self._polling_lock:
            self._polling_paused[device_ip] = True

    async def resume_polling(self, device_ip: str) -> None:
        async with self._polling_lock:
            self._polling_paused[device_ip] = False

    def is_polling_paused(self, device_ip: str) -> bool:
        return self._polling_paused.get(device_ip, False)

    async def send_request_with_polling_control(
        self,
        message: str,
        target_ip: str,
        target_port: int,
        timeout: float = 5.0,
    ) -> dict[str, Any]:
        await self.pause_polling(target_ip)
        try:
            return await self.send_request(
                message, target_ip, target_port, timeout, quiet_on_timeout=True
            )
        finally:
            await self.resume_polling(target_ip)

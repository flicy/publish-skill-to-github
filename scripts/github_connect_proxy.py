#!/usr/bin/env python3
"""Tiny local CONNECT proxy for GitHub DNS/IP timeout workarounds.

Use only when api.github.com works but github.com resolves to a slow or blocked
address during gh auth login or git push. It does not inspect TLS traffic; it
only forwards CONNECT tunnels and tries alternate GitHub frontend IPs.
"""

from __future__ import annotations

import select
import socket
import threading

LISTEN = ("127.0.0.1", 18080)
OVERRIDE = {
    "github.com": [
        "140.82.112.4",
        "140.82.113.3",
        "140.82.113.4",
        "140.82.114.3",
        "140.82.114.4",
        "140.82.121.4",
    ],
}


def connect_target(host: str, port: int) -> tuple[socket.socket, str]:
    targets = OVERRIDE.get(host, [host])
    last_error: Exception | None = None
    for target in targets:
        try:
            return socket.create_connection((target, port), timeout=8), target
        except Exception as exc:  # noqa: BLE001 - best-effort fallback list
            last_error = exc
    assert last_error is not None
    raise last_error


def relay(left: socket.socket, right: socket.socket) -> None:
    sockets = [left, right]
    try:
        while True:
            readable, _, _ = select.select(sockets, [], [], 120)
            if not readable:
                break
            for sock in readable:
                data = sock.recv(65536)
                if not data:
                    return
                (right if sock is left else left).sendall(data)
    finally:
        for sock in sockets:
            try:
                sock.close()
            except OSError:
                pass


def handle(client: socket.socket) -> None:
    try:
        buffer = b""
        while b"\r\n\r\n" not in buffer and len(buffer) < 65536:
            chunk = client.recv(4096)
            if not chunk:
                client.close()
                return
            buffer += chunk

        request_line = buffer.decode("iso-8859-1", "replace").split("\r\n", 1)[0]
        parts = request_line.split()
        if len(parts) < 3 or parts[0].upper() != "CONNECT":
            client.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
            client.close()
            return

        host, port_text = parts[1].rsplit(":", 1)
        upstream, used = connect_target(host, int(port_text))
        print(f"CONNECT {host}:{port_text} via {used}", flush=True)
        client.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
        relay(client, upstream)
    except Exception as exc:  # noqa: BLE001 - proxy should fail closed
        print(f"ERR {exc}", flush=True)
        try:
            client.sendall(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
        except OSError:
            pass
        try:
            client.close()
        except OSError:
            pass


def main() -> None:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(LISTEN)
    server.listen(50)
    print(f"proxy listening on {LISTEN[0]}:{LISTEN[1]}", flush=True)
    try:
        while True:
            client, _ = server.accept()
            threading.Thread(target=handle, args=(client,), daemon=True).start()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

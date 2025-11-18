# -*- coding: utf-8 -*-
"""
microMCP: Eine leichtgewichtige, FastMCP-kompatible Model Context Protocol (MCP)
Server-Bibliothek für MicroPython, die nur Standard-Firmware-Bibliotheken verwendet.
"""

import usocket as socket
import json
import _thread
import utime as time
import sys
import uhashlib
import ubinascii

# Der magische String für den WebSocket-Handshake (RFC 6455)
WS_MAGIC_STRING = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


class MicroMCPServer:
    """
    Implementiert den MCP-Server-Kern mit einer FastMCP-ähnlichen Decorator-API
    und einem integrierten minimalen WebSocket-Server.
    """

    def __init__(self, name: str, host: str = '0.0.0.0', port: int = 8080):
        self._name = name
        self._host = host
        self._port = port
        self._tools = []  # Gesammelte Tool-Schemata (für Discovery)
        self._methods = {}  # Registrierte Python-Funktionen (Callbacks)
        self._resources = {}  # Muster für registrierte Ressourcen
        self._server_socket = None
        print(f"MicroMCP '{self._name}' initialisiert auf ws://{host}:{port}")

    # --- Decorator-Funktionen (Benutzer-API) ---

    def tool(self, func):
        """Decorator für MCP-Tool-Funktionen."""

        # Erstellt das OpenAPI-ähnliche Schema
        function_spec = {
            "name": func.__name__,
            "description": func.__doc__ or "Keine Beschreibung verfügbar.",
            # MicroPython unterstützt keine einfache Typ-Inspektion wie CPython.
            # Wir verlassen uns darauf, dass der Client die Parameter kennt
            # oder wir definieren sie manuell (hier vereinfacht).
            "parameters": {"type": "object", "properties": {}, "required": []},
        }

        self._register_tool_or_resource(function_spec, func, is_tool=True)
        return func

    def resource(self, uri_pattern: str):
        """Decorator für MCP-Resource-Funktionen."""

        def decorator(func):
            function_spec = {
                "name": uri_pattern,  # Verwende URI als Name für die RPC-Methode
                "description": func.__doc__ or "Statische oder dynamische Ressource.",
                "uri_pattern": uri_pattern
            }
            self._register_tool_or_resource(function_spec, func, is_tool=False)
            return func

        return decorator

    # --- Interne Registrierung ---

    def _register_tool_or_resource(self, spec: dict, func_to_call, is_tool: bool):
        """Interne Registrierungslogik."""
        name = spec["name"]

        if is_tool:
            full_schema = {
                "openapi": "3.0.0",
                "info": {"title": f"{self._name} Tool", "version": "1.0.0"},
                "system_info": "ESP32, MicroPython, " + sys.version.split(' ')[0],
                "tools": [spec]
            }
            self._tools.append(full_schema)
            # Tool wird unter seinem Funktionsnamen registriert
            self._methods[name] = func_to_call
        else:
            # Ressource wird unter ihrem URI-Muster registriert
            self._resources[spec['uri_pattern']] = func_to_call
            # Registriere auch als aufrufbare RPC-Methode
            self._methods[name] = func_to_call

        print(f"Registriert: {'Tool' if is_tool else 'Resource'} '{name}'")

    # --- JSON-RPC Protokoll-Logik ---

    def _create_rpc_response(self, result=None, error=None, rpc_id=None) -> bytes:
        """Erzeugt eine JSON-RPC-Antwort als UTF-8 Bytes."""
        response = {"jsonrpc": "2.0", "id": rpc_id}
        if error:
            response["error"] = error
        else:
            response["result"] = result
        # Wir geben direkt Bytes zurück, bereit für das WS-Framing
        return json.dumps(response).encode('utf-8')

    def _handle_rpc_request(self, request_json: dict) -> bytes:
        """Verarbeitet einen einzelnen JSON-RPC-Request."""
        rpc_id = request_json.get("id")
        method = request_json.get("method")
        params = request_json.get("params", {})

        if method == "mcp_get_tools":
            # 1. Tool Discovery
            return self._create_rpc_response(result=self._tools, rpc_id=rpc_id)

        if method in self._methods:
            # 2. Tool- oder Resource-Ausführung
            try:
                tool_func = self._methods[method]
                # Ruft die registrierte Funktion mit den Parametern auf
                result_data = tool_func(**params)
                return self._create_rpc_response(result=result_data, rpc_id=rpc_id)
            except Exception as e:
                error = {"code": -32000, "message": f"Tool-Ausführungsfehler: {e}"}
                return self._create_rpc_response(error=error, rpc_id=rpc_id)
        else:
            error = {"code": -32601, "message": f"Methode/Resource nicht gefunden: {method}"}
            return self._create_rpc_response(error=error, rpc_id=rpc_id)

    # --- Minimaler WebSocket Server (Nur Standard-Bibliotheken) ---

    def _parse_http_headers(self, request_str: str) -> dict:
        """Parst HTTP-Header in ein Dictionary."""
        headers = {}
        lines = request_str.split('\r\n')
        for line in lines[1:]:  # Überspringe die GET-Zeile
            if ': ' in line:
                key, value = line.split(': ', 1)
                headers[key.lower()] = value
        return headers

    def _perform_ws_handshake(self, client_socket) -> bool:
        """Führt den WebSocket-Server-Handshake durch."""
        try:
            request_data = client_socket.recv(1024)
            if not request_data:
                return False

            request_str = request_data.decode('utf-8')
            headers = self._parse_http_headers(request_str)

            if 'sec-websocket-key' not in headers:
                print("WS Handshake Error: Kein Sec-WebSocket-Key.")
                return False

            ws_key = headers['sec-websocket-key']

            # Berechne den Akzeptanz-Schlüssel
            accept_key_raw = ws_key + WS_MAGIC_STRING
            accept_hash = uhashlib.sha1(accept_key_raw.encode('utf-8')).digest()
            accept_key_b64 = ubinascii.b2a_base64(accept_hash).strip()  # strip() entfernt \n

            # Sende die Handshake-Antwort (HTTP 101)
            response = (
                "HTTP/1.1 101 Switching Protocols\r\n"
                "Upgrade: websocket\r\n"
                "Connection: Upgrade\r\n"
                f"Sec-WebSocket-Accept: {accept_key_b64.decode('utf-8')}\r\n"
                "\r\n"
            )
            client_socket.send(response.encode('utf-8'))
            return True
        except Exception as e:
            print(f"WS Handshake Fehler: {e}")
            return False

    def _read_ws_frame(self, client_socket) -> bytes:
        """Liest einen einzelnen WebSocket-Frame (vereinfacht)."""
        # 1. Ersten 2 Bytes lesen (FIN, RSV, Opcode, Mask, Payload Len)
        header = client_socket.recv(2)
        if not header:
            return None  # Verbindung geschlossen

        fin = header[0] & 0x80
        opcode = header[0] & 0x0F

        if opcode == 0x8:  # Close Frame
            return None

        if opcode != 0x1:  # Nur Text Frames (JSON)
            print(f"Warnung: Nicht unterstützter Opcode {opcode}")
            return None  # Ignoriere (oder schließe)

        mask = header[1] & 0x80
        payload_len_short = header[1] & 0x7F

        # 2. Payload-Länge bestimmen
        if payload_len_short == 126:
            payload_len_bytes = client_socket.recv(2)
            payload_len = int.from_bytes(payload_len_bytes, 'big')
        elif payload_len_short == 127:
            # Zu groß für ESP32, Verbindung abbrechen
            print("Fehler: WS Payload zu groß (>=64k)")
            return None
        else:
            payload_len = payload_len_short

        # 3. Maskierungs-Schlüssel lesen
        if mask:
            masking_key = client_socket.recv(4)
        else:
            print("Fehler: Client-Frame nicht maskiert.")
            return None

        # 4. Daten lesen und demaskieren
        masked_data = client_socket.recv(payload_len)
        data = bytearray(payload_len)
        for i in range(payload_len):
            data[i] = masked_data[i] ^ masking_key[i % 4]

        return bytes(data)

    def _write_ws_frame(self, client_socket, data: bytes) -> bool:
        """Schreibt einen einzelnen WebSocket-Frame (Text, unmaskiert)."""
        try:
            frame_header = bytearray(2)
            frame_header[0] = 0x81  # FIN=1, Opcode=1 (Text)

            payload_len = len(data)

            if payload_len <= 125:
                frame_header[1] = payload_len  # Mask=0
                client_socket.send(frame_header)
            elif payload_len <= 65535:
                frame_header[1] = 126  # Mask=0
                frame_header.extend(payload_len.to_bytes(2, 'big'))
                client_socket.send(frame_header)
            else:
                # Zu groß für diese Implementierung
                print(f"Fehler: Antwort-Payload zu groß zum Senden ({payload_len} Bytes)")
                return False

            client_socket.send(data)
            return True
        except Exception as e:
            print(f"WS Sende-Fehler: {e}")
            return False

    def _handle_connection(self, client_socket, client_addr):
        """Verwaltet eine einzelne WebSocket-Verbindung."""
        print(f"Neue Verbindung von {client_addr}")

        if not self._perform_ws_handshake(client_socket):
            client_socket.close()
            print("WS Handshake fehlgeschlagen.")
            return

        print(f"WS Verbindung etabliert mit {client_addr}")

        while True:
            try:
                # 1. Auf RPC-Request warten
                payload_bytes = self._read_ws_frame(client_socket)

                if payload_bytes is None:
                    # Saubere Trennung oder Fehler
                    break

                # 2. RPC-Request verarbeiten
                try:
                    request_json = json.loads(payload_bytes.decode('utf-8'))
                except ValueError:
                    response_bytes = self._create_rpc_response(
                        error={"code": -32700, "message": "Parse error"},
                        rpc_id=None
                    )
                else:
                    response_bytes = self._handle_rpc_request(request_json)

                # 3. RPC-Antwort senden
                self._write_ws_frame(client_socket, response_bytes)

            except Exception as e:
                print(f"Fehler in WS-Schleife: {e}")
                break  # Bei Fehler Verbindung beenden

        client_socket.close()
        print(f"Verbindung zu {client_addr} geschlossen.")

    # --- Server-Startfunktionen ---

    def run(self):
        """Startet den blockierenden MCP-Server."""
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        addr = socket.getaddrinfo(self._host, self._port)[0][-1]
        self._server_socket.bind(addr)
        self._server_socket.listen(2)

        print(f"MicroMCP '{self._name}' lauscht auf {addr}")

        while True:
            try:
                client_socket, client_addr = self._server_socket.accept()
                # Starte einen neuen Thread für jeden Client
                _thread.start_new_thread(self._handle_connection, (client_socket, client_addr))
            except OSError as e:
                print(f"Socket Accept Fehler: {e}")
                time.sleep(1)

    def run_threaded(self) -> bool:
        """Startet den MCP-Server in einem separaten Thread."""
        try:
            _thread.start_new_thread(self.run, ())
            print("MicroMCP-Server in separatem Thread gestartet.")
            return True
        except Exception as e:
            print(f"Fehler beim Starten des MCP-Threads: {e}")
            return False

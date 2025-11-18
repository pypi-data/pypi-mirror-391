# microMCP
Eine extrem leichtgewichtige, FastMCP-kompatible Model Context Protocol (MCP) Server-Bibliothek
für MicroPython (z.B. ESP32).  
Das Hauptmerkmal ist, dass es keine externen Abhängigkeiten benötigt 
(keine manuelle Installation von WebSocket-Bibliotheken erforderlich). 
Es implementiert einen minimalen WebSocket-Server und die JSON-RPC-Logik unter Verwendung 
von `usocket`, `uhashlib` und `ubinascii` direkt aus der MicroPython-Standard-Firmware. 

## Features 
- FastMCP-ähnliche Decorator-API (@mcp.tool, @mcp.resource).
- Integrierter, minimaler WebSocket-Server (keine Abhängigkeiten). 
- Implementiert JSON-RPC 2.0 für die MCP-Kommunikation.
- Extrem schlank für den Einsatz auf ESP32. 

## Installation
Du kannst die Bibliothek direkt auf deinem MicroPython-Board über mip (den modernen upip-Nachfolger) installieren, 
sobald sie auf PyPI veröffentlicht ist:
```python
import mip
mip.install("micromcp")
```
Oder manuell: Kopiere einfach das Verzeichnis micromcp/ in das lib/-Verzeichnis auf deinem Gerät.  

Beispiel-Verwendung (z.B. main.py auf ESP32)
```python
import network
import utime
from micromcp import MicroMCPServer

# --- 1. WLAN verbinden (Voraussetzung) ---
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print('Verbinde mit WLAN...')
    wlan.connect('DEINE_SSID', 'DEIN_PASSWORT')
    while not wlan.isconnected():
        utime.sleep(1)
print('Netzwerk-Konfiguration:', wlan.ifconfig())

# --- 2. microMCP Server instanziieren ---
# Der Host 0.0.0.0 bindet an die IP des ESP32
mcp = MicroMCPServer(name="ESP32_Wohnzimmer", host='0.0.0.0', port=8080)

# --- 3. Tools und Ressourcen definieren ---

@mcp.tool
def get_system_uptime() -> dict:
    """Gibt die System-Laufzeit in Millisekunden zurück."""
    return {"uptime_ms": utime.ticks_ms()}

@mcp.tool
def add(a: int, b: int) -> int:
    """Addiert zwei Zahlen (FastMCP Kompatibilitätstest)."""
    return a + b

@mcp.resource("config://version")
def get_version():
    """Gibt die Firmware-Version zurück."""
    return {"version": "1.0.0-beta"}

# --- 4. Server in einem Thread starten ---
if __name__ == "__main__":
    mcp.run_threaded()
    
    # Haupt-Thread kann andere Dinge tun (z.B. LED blinken lassen)
    print("MCP Server läuft im Hintergrund...")
    while True:
        utime.sleep(10)
```


## Kompatibilität

Getestet für die Verbindung mit einem Standard fastmcp Python-Client.
```python
# client.py (auf deinem Laptop)
import asyncio
from fastmcp import Client

async def main():
    # Stelle sicher, dass die IP-Adresse korrekt ist
    async with Client("ws://192.168.0.88:8080") as client:
        tools = await client.list_tools()
        print(f"Verfügbare Tools: {tools}")
        
        result = await client.call_tool("add", {"a": 5, "b": 3})
        print(f"Ergebnis von add(5, 3): {result.content}")

        result_uptime = await client.call_tool("get_system_uptime", {})
        print(f"ESP32 Uptime: {result_uptime.content}")

if __name__ == "__main__":
    asyncio.run(main())

```

## Beispiel Anwendung  

```python
"""
Beispiel-Implementierung für den microMCP Server auf einem ESP32.
Diese Datei wird auf dem ESP32 ausgeführt.
"""
import network
import utime
import machine # Für LED/Sensor-Beispiel

try:
    from micromcp import MicroMCPServer
except ImportError:
    print("Fehler: 'micromcp' Bibliothek nicht gefunden.")
    print("Bitte installiere sie mit 'mip.install(\"micromcp\")' oder kopiere sie nach /lib.")
    sys.exit(1)


# --- 1. WLAN verbinden (Voraussetzung) ---
# Ersetze dies durch deine WLAN-Konfiguration
WIFI_SSID = "DEINE_SSID"
WIFI_PASSWORD = "DEIN_PASSWORT"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print(f"Verbinde mit WLAN '{WIFI_SSID}'...")
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    # Warte auf Verbindung
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('.')
        utime.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('WLAN-Verbindung fehlgeschlagen')
else:
    print('Netzwerk-Konfiguration:', wlan.ifconfig())


# --- 2. microMCP Server instanziieren ---
# Der Host 0.0.0.0 bindet an die IP des ESP32
mcp = MicroMCPServer(name="ESP32_Wohnzimmer", host='0.0.0.0', port=8080)

# --- 3. Tools und Ressourcen definieren ---

# Beispiel: Onboard-LED (Pin 2 bei vielen DevKits)
led = machine.Pin(2, machine.Pin.OUT)

@mcp.tool
def set_led(status: bool) -> dict:
    """Schaltet die Onboard-LED des ESP32 ein (true) oder aus (false)."""
    if status:
        led.on()
        print("LED eingeschaltet")
    else:
        led.off()
        print("LED ausgeschaltet")
    return {"led_status": "on" if status else "off"}

@mcp.tool
def get_system_uptime() -> dict:
    """Gibt die System-Laufzeit in Millisekunden zurück."""
    return {"uptime_ms": utime.ticks_ms()}

@mcp.tool
def add(a: int, b: int) -> int:
    """Addiert zwei Zahlen (FastMCP Kompatibilitätstest)."""
    return a + b

@mcp.resource("config://version")
def get_version():
    """Gibt die Firmware-Version zurück."""
    return {"version": "1.0.0-beta", "micropython": sys.version}

# --- 4. Server in einem Thread starten ---
if __name__ == "__main__":
    mcp.run_threaded()
    
    # Haupt-Thread kann andere Dinge tun (z.B. LED blinken lassen)
    print("MCP Server läuft im Hintergrund...")
    print(f"Verfügbar unter: ws://{wlan.ifconfig()[0]}:8080")
    
    while True:
        # Hier könnte deine Haupt-Sensorlogik laufen
        utime.sleep(10)
```
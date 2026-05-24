"""
Module 1 Assignment — Task 2.1
CoAP Sensor Resource Server

Complete all TODO sections. The resource classes must match the
URIs and behaviours listed in the assignment spec.

Run with:  python -m src.coap.server
"""

import asyncio
import json
import logging
import random
from datetime import datetime, timezone

import aiocoap
import aiocoap.resource as resource
from aiocoap import Code, Message

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s")
log = logging.getLogger(__name__)

# ── Sensor simulation helpers ─────────────────────────────────────────────────

SENSOR_CONFIG = {
    "temperature": {"unit": "C",    "base": 70.0, "noise": 3.0},
    "vibration":   {"unit": "mm/s", "base": 1.2,  "noise": 0.3},
    "power":       {"unit": "kW",   "base": 45.0, "noise": 5.0},
}

def _sim(sensor: str) -> dict:
    cfg = SENSOR_CONFIG[sensor]
    return {
        "value": round(cfg["base"] + random.gauss(0, cfg["noise"]), 3),
        "unit":  cfg["unit"],
        "ts":    datetime.now(timezone.utc).isoformat(),
    }

def _json(data: dict) -> bytes:
    return json.dumps(data).encode()


# ── Observable Sensor Resource ────────────────────────────────────────────────

class SensorResource(resource.ObservableResource):
    """
    An observable CoAP resource that represents a single sensor on a line.

    TODO 1: Implement this class.
    Requirements:
      - Accept line and sensor_type in __init__
      - Store the current reading (initially simulated)
      - Start an asyncio background task (_update_loop) that:
          * Simulates a new reading every 5 seconds
          * Calls self.updated_state() to notify observers
      - Implement render_get:
          * Return a 2.05 Content response
          * Content-Format: 50 (application/json)
          * Payload: JSON-encoded current reading
    """

    def __init__(self, line: str, sensor_type: str):
        super().__init__()
        self.line        = line
        self.sensor_type = sensor_type
        self._reading    = _sim(sensor_type)
        asyncio.ensure_future(self._update_loop())

    async def _update_loop(self) -> None:
        while True:
            await asyncio.sleep(5)
            self._reading = _sim(self.sensor_type)
            self.updated_state()

    async def render_get(self, request: Message) -> Message:
        return Message(code=Code.CONTENT, payload=_json(self._reading), content_format=50)


# ── Actuator Resource ─────────────────────────────────────────────────────────

class ActuatorResource(resource.Resource):
    """
    A CoAP resource representing a controllable fan actuator.

    TODO 4: Implement this class.
    Requirements:
      - Track state: "OFF" initially
      - render_get: return current state as JSON {"state": "ON"|"OFF"}
      - render_put: accept {"state": "ON"} or {"state": "OFF"}
          * Update internal state
          * Return 2.04 Changed on success
          * Return 4.00 Bad Request if payload is malformed or state is invalid
    """

    def __init__(self):
        super().__init__()
        self._state = "OFF"

    async def render_get(self, request: Message) -> Message:
        return Message(code=Code.CONTENT, payload=_json({"state":self._state}), content_format=50)

    async def render_put(self, request: Message) -> Message:
        try:
            data = json.loads(request.payload)
            state = data["state"]

        except (json.JSONDecodeError, KeyError, TypeError):
            return Message(code=Code.BAD_REQUEST)

        if state in ("ON", "OFF"):
            self._state = state
            return Message(code = Code.CHANGED, payload = _json({"state": self._state}), content_format=50)
        else:
            return Message(code = Code.BAD_REQUEST)


# ── Block-wise Manifest Resource ──────────────────────────────────────────────

class ManifestResource(resource.Resource):
    """
    A large resource that triggers CoAP Block2 transfer.

    TODO 7: Implement this class.
    Requirements:
      - render_get must return a payload of AT LEAST 3072 bytes (3 KB)
      - Content-Format: 50 (application/json)
      - The payload should be a realistic-looking firmware manifest
        (list of sensor firmware versions, checksums, update URLs, etc.)
      - aiocoap handles Block2 fragmentation automatically if the payload
        exceeds the negotiated block size — you just need to return the full payload
    """

    async def render_get(self, request: Message) -> Message:
        manifest = {
            "manifest_version": "1.0",
            "generated": datetime.now(timezone.utc).isoformat(),
            "firmware": [
                {
                    "sensor_id": f"sensor-{i:03d}",
                    "version": f"2.{i}.0",
                    "checksum": f"sha256:{'a' * 64}",
                    "url": f"coap://localhost:5683/firmware/sensor-{i:03d}.bin",
                    "size_bytes": 1024 * (i + 1),
                }
                for i in range(50)
            ],
        }
        payload = _json(manifest)
        assert len(payload) >= 3072, f"manifest too small: {len(payload)} bytes"
        return Message(code=Code.CONTENT, payload=payload, content_format=50)


# ── Resource Tree & Server Setup ──────────────────────────────────────────────

async def build_server() -> aiocoap.Context:
    root = resource.Site()

    root.add_resource(['factory', 'line1', 'temperature'], 
        SensorResource('line1', 'temperature'))
    root.add_resource(['factory', 'line1', 'vibration'],   
        SensorResource('line1', 'vibration'))
    root.add_resource(['factory', 'line1', 'power'],        
        SensorResource('line1', 'power'))
    root.add_resource(['factory', 'line2', 'temperature'], 
        SensorResource('line2', 'temperature'))
    root.add_resource(['actuator', 'line1', 'fan'],         
        ActuatorResource())
    root.add_resource(['factory', 'manifest'],              
        ManifestResource())

    root.add_resource(['.well-known', 'core'], 
        resource.WKCResource(root.get_resources_as_linkheader))
                    
    context = await aiocoap.Context.create_server_context(root)
    return context


async def main() -> None:
    context = await build_server()
    log.info("CoAP server running on coap://localhost:5683")
    log.info("Resources: /factory/line{1,2}/{temperature,vibration,power}, /actuator/line1/fan, /factory/manifest")
    await asyncio.get_event_loop().create_future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())

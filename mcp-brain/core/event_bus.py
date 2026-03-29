import asyncio
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("event_bus")

class EventBus:
    def __init__(self):
        self.subscribers = {}
        self.event_log = []

    def subscribe(self, event_name, callback):
        if event_name not in self.subscribers:
            self.subscribers[event_name] = []
        self.subscribers[event_name].append(callback)

    async def emit(self, event_name, payload):
        event = {"event_name": event_name, "payload": payload, "timestamp": datetime.utcnow().isoformat()}
        self.event_log.append(event)
        logger.info(f"Event: {event_name} - {payload}")
        if event_name in self.subscribers:
            for callback in self.subscribers[event_name]:
                if asyncio.iscoroutinefunction(callback):
                    await callback(payload)
                else:
                    callback(payload)

    def get_events(self):
        return self.event_log

event_bus = EventBus()

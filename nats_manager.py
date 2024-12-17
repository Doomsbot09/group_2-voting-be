import asyncio
from nats.aio.client import Client as NATS

class NATSManager:
    def __init__(self):
        self.nc = NATS()

    async def connect(self, servers="nats://127.0.0.1:4222"):
        await self.nc.connect(servers=servers)

    async def close(self):
        await self.nc.close()

    async def flush(self):
        await self.nc.flush()

    async def publish(self, subject: str, message: str):
        await self.nc.publish(subject, message.encode('utf-8'))

    async def subscribe(self, subject: str, callback):
        await self.nc.subscribe(subject, cb=callback)

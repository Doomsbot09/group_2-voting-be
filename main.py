from fastapi import FastAPI, HTTPException
from nats_manager import NATSManager
from pydantic import BaseModel, Field

import asyncio

app = FastAPI()
nats_manager = NATSManager()

class PublishMessage(BaseModel):
    subject: str = Field(..., description = "NATS subject to publish the message to")
    message: str = Field(..., description = "Message to publish on the given subject")

@app.on_event("startup")
async def startup():
    # Connect to the NATS server during startup
    await nats_manager.connect()

@app.on_event("shutdown")
async def shutdown():
    # Close the NATS connection during shutdown
    await nats_manager.close()

@app.post("/publish/")
async def publish_message(payload: PublishMessage):
    try:
        await nats_manager.publish(payload.subject, payload.message)
        await nats_manager.flush()
        return {"status": "Message published", "subject": payload.subject}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/subscribe/{subject}")
async def subscribe_subject(subject: str):
    try:
        async def message_handler(msg):
            print(f"Received a message on '{msg.subject}': {msg.data.decode()}")

        # Subscribe to the subject
        await nats_manager.subscribe(subject, message_handler)
        return {"status": f"Subscribed to {subject}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

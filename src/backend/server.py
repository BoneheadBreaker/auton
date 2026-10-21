from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins change to specific frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET POST etc)
    allow_headers=["*"],
)

message_database = ["TEMP", "This is just testing", "I should add a real file for message history"]

class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

ConManager = ConnectionManager()

@app.get("/messages")
def get_message_history():
    return message_database

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await ConManager.connect(websocket)
    await ConManager.broadcast(f"Client #{client_id} joined the chat!")
    try:
        while True:
            # Fix: Corrected spelling to 'receive_text'
            data = await websocket.receive_text()
            await ConManager.broadcast(f"#{client_id}: {data}")
    # Fix: Catching the correct exported exception
    except WebSocketDisconnect:
        ConManager.disconnect(websocket)
        await ConManager.broadcast(f"System: Client #{client_id} left the chat.")
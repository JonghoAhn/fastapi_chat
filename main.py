from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List

app = FastAPI()

# Static files configuration
app.mount("/public", StaticFiles(directory="public"), name="public")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def get():
    with open('public/index.html', 'r') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = f"{username}: {data}"
            await manager.broadcast(message)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        manager.disconnect(websocket)
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import uuid
from typing import Dict, List
import cv2
import numpy as np
import base64
from services.emotion_detector import EmotionDetector

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.emotion_detector = EmotionDetector()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/emotion-detection")
async def websocket_emotion_detection(websocket: WebSocket):
    """
    WebSocket endpoint for real-time emotion detection
    """
    await manager.connect(websocket)
    session_id = str(uuid.uuid4())
    
    try:
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "session_id": session_id,
            "message": "Connected to emotion detection service"
        }))
        
        while True:
            # Receive data from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "video_frame":
                # Process base64 encoded image
                image_data = message["image"].split(",")[1]  # Remove data:image/jpeg;base64,
                image_bytes = base64.b64decode(image_data)
                
                # Convert to numpy array
                nparr = np.frombuffer(image_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    # Detect emotion
                    result = manager.emotion_detector.detect_emotion_realtime(frame)
                    
                    # Send result back to client
                    response = {
                        "type": "emotion_detected",
                        "session_id": session_id,
                        "emotion": result.get("emotion", "neutral"),
                        "confidence": result.get("confidence", 0.0),
                        "all_emotions": result.get("all_emotions", {}),
                        "timestamp": message.get("timestamp")
                    }
                    
                    await websocket.send_text(json.dumps(response))
                else:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Could not process video frame"
                    }))
            
            elif message["type"] == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": message.get("timestamp")
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"Client {session_id} disconnected from emotion detection")
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"Error in emotion detection: {str(e)}"
        }))
        manager.disconnect(websocket)

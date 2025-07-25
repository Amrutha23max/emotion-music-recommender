from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import cv2
import numpy as np
from PIL import Image
import io
import uuid
from datetime import datetime

from database.database import get_db
from database.models import EmotionSession
from services.emotion_detector import EmotionDetector

router = APIRouter()
emotion_detector = EmotionDetector()

@router.post("/detect-from-image")
async def detect_emotion_from_image(
    file: UploadFile = File(...),
    session_id: str = None,
    db: Session = Depends(get_db)
):
    """
    Detect emotion from uploaded image
    """
    try:
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Read and process image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        image_array = np.array(image)
        
        # Convert RGB to BGR for OpenCV
        if len(image_array.shape) == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        # Detect emotion
        emotion_result = emotion_detector.detect_emotion(image_array)
        
        if not emotion_result:
            raise HTTPException(status_code=400, detail="No face detected in image")
        
        # Save to database
        emotion_session = EmotionSession(
            session_id=session_id,
            emotion_detected=emotion_result["emotion"],
            confidence_score=emotion_result["confidence"],
            timestamp=datetime.utcnow()
        )
        db.add(emotion_session)
        db.commit()
        
        return {
            "session_id": session_id,
            "emotion": emotion_result["emotion"],
            "confidence": emotion_result["confidence"],
            "all_emotions": emotion_result.get("all_emotions", {}),
            "face_detected": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@router.get("/session/{session_id}")
async def get_emotion_session(session_id: str, db: Session = Depends(get_db)):
    """
    Get emotion session data
    """
    sessions = db.query(EmotionSession).filter(
        EmotionSession.session_id == session_id
    ).all()
    
    if not sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "emotions": [
            {
                "emotion": session.emotion_detected,
                "confidence": session.confidence_score,
                "timestamp": session.timestamp
            }
            for session in sessions
        ]
    }

@router.get("/emotions")
async def get_supported_emotions():
    """
    Get list of supported emotions
    """
    return {
        "emotions": emotion_detector.get_supported_emotions(),
        "model_info": emotion_detector.get_model_info()
    }

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from database.database import get_db
from database.models import MusicRecommendation, MusicFeatures
from services.music_recommender import MusicRecommender
from services.spotify_service import SpotifyService

router = APIRouter()
music_recommender = MusicRecommender()
spotify_service = SpotifyService()

@router.post("/recommend")
async def get_music_recommendations(
    emotion: str,
    session_id: str,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get music recommendations based on detected emotion
    """
    try:
        # Get recommendations from our ML model
        recommendations = music_recommender.recommend_by_emotion(
            emotion=emotion,
            limit=limit
        )
        
        # Enhance with Spotify data if available
        enhanced_recommendations = []
        for rec in recommendations:
            spotify_data = await spotify_service.get_track_info(rec.get("track_id"))
            if spotify_data:
                rec.update(spotify_data)
            enhanced_recommendations.append(rec)
            
            # Save recommendation to database
            music_rec = MusicRecommendation(
                session_id=session_id,
                track_id=rec.get("track_id", ""),
                track_name=rec.get("track_name", ""),
                artist_name=rec.get("artist_name", ""),
                emotion=emotion,
                recommendation_score=rec.get("score", 0.0),
                timestamp=datetime.utcnow()
            )
            db.add(music_rec)
        
        db.commit()
        
        return {
            "session_id": session_id,
            "emotion": emotion,
            "recommendations": enhanced_recommendations,
            "total_count": len(enhanced_recommendations)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")

@router.post("/feedback")
async def submit_feedback(
    session_id: str,
    track_id: str,
    feedback: str,  # "like", "dislike", "neutral"
    db: Session = Depends(get_db)
):
    """
    Submit user feedback for a recommendation
    """
    try:
        # Update recommendation with feedback
        recommendation = db.query(MusicRecommendation).filter(
            MusicRecommendation.session_id == session_id,
            MusicRecommendation.track_id == track_id
        ).first()
        
        if not recommendation:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        recommendation.user_feedback = feedback
        db.commit()
        
        # Update ML model with feedback (for future improvements)
        music_recommender.update_with_feedback(
            emotion=recommendation.emotion,
            track_id=track_id,
            feedback=feedback
        )
        
        return {
            "message": "Feedback submitted successfully",
            "session_id": session_id,
            "track_id": track_id,
            "feedback": feedback
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting feedback: {str(e)}")

@router.get("/search")
async def search_music(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Search for music tracks
    """
    try:
        results = await spotify_service.search_tracks(query, limit)
        return {
            "query": query,
            "results": results,
            "total_count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching music: {str(e)}")

@router.get("/emotions/{emotion}/stats")
async def get_emotion_music_stats(
    emotion: str,
    db: Session = Depends(get_db)
):
    """
    Get statistics for music recommendations by emotion
    """
    try:
        recommendations = db.query(MusicRecommendation).filter(
            MusicRecommendation.emotion == emotion
        ).all()
        
        if not recommendations:
            return {
                "emotion": emotion,
                "total_recommendations": 0,
                "top_tracks": [],
                "feedback_stats": {}
            }
        
        # Calculate statistics
        total_recommendations = len(recommendations)
        
        # Top tracks by recommendation count
        track_counts = {}
        feedback_stats = {"like": 0, "dislike": 0, "neutral": 0, "no_feedback": 0}
        
        for rec in recommendations:
            track_key = f"{rec.track_name} - {rec.artist_name}"
            track_counts[track_key] = track_counts.get(track_key, 0) + 1
            
            if rec.user_feedback:
                feedback_stats[rec.user_feedback] = feedback_stats.get(rec.user_feedback, 0) + 1
            else:
                feedback_stats["no_feedback"] += 1
        
        top_tracks = sorted(track_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "emotion": emotion,
            "total_recommendations": total_recommendations,
            "top_tracks": [{"track": track, "count": count} for track, count in top_tracks],
            "feedback_stats": feedback_stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@router.get("/playlist/generate")
async def generate_emotion_playlist(
    emotions: str = Query(..., description="Comma-separated list of emotions"),
    duration_minutes: int = Query(30, ge=10, le=180),
    db: Session = Depends(get_db)
):
    """
    Generate a playlist based on multiple emotions
    """
    try:
        emotion_list = [e.strip() for e in emotions.split(",")]
        playlist = music_recommender.generate_playlist(
            emotions=emotion_list,
            duration_minutes=duration_minutes
        )
        
        return {
            "emotions": emotion_list,
            "duration_minutes": duration_minutes,
            "playlist": playlist,
            "total_tracks": len(playlist)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating playlist: {str(e)}")

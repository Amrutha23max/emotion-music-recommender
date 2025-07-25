from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.sql import func
from database.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    spotify_id = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class EmotionSession(Base):
    __tablename__ = "emotion_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    session_id = Column(String, index=True)
    emotion_detected = Column(String)
    confidence_score = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    image_path = Column(String, nullable=True)

class MusicRecommendation(Base):
    __tablename__ = "music_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    track_id = Column(String)
    track_name = Column(String)
    artist_name = Column(String)
    emotion = Column(String)
    recommendation_score = Column(Float)
    user_feedback = Column(String, nullable=True)  # like, dislike, neutral
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class MusicFeatures(Base):
    __tablename__ = "music_features"
    
    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(String, unique=True, index=True)
    track_name = Column(String)
    artist_name = Column(String)
    danceability = Column(Float)
    energy = Column(Float)
    valence = Column(Float)
    tempo = Column(Float)
    acousticness = Column(Float)
    instrumentalness = Column(Float)
    speechiness = Column(Float)
    emotion_tags = Column(Text)  # JSON string of emotion tags

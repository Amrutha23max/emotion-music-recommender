import numpy as np
import pandas as pd
from typing import List, Dict, Optional
import json
import random

class MusicRecommender:
    """
    Music recommendation system based on emotions
    """
    
    def __init__(self):
        # Emotion to music feature mapping
        self.emotion_music_map = {
            'happy': {
                'valence': [0.7, 1.0],
                'energy': [0.6, 1.0],
                'danceability': [0.5, 1.0],
                'tempo': [120, 180]
            },
            'sad': {
                'valence': [0.0, 0.4],
                'energy': [0.0, 0.5],
                'danceability': [0.0, 0.4],
                'tempo': [60, 100]
            },
            'angry': {
                'valence': [0.2, 0.6],
                'energy': [0.7, 1.0],
                'danceability': [0.4, 0.8],
                'tempo': [130, 200]
            },
            'neutral': {
                'valence': [0.4, 0.7],
                'energy': [0.4, 0.7],
                'danceability': [0.3, 0.7],
                'tempo': [90, 130]
            },
            'surprise': {
                'valence': [0.5, 0.8],
                'energy': [0.6, 0.9],
                'danceability': [0.4, 0.8],
                'tempo': [110, 150]
            },
            'fear': {
                'valence': [0.1, 0.4],
                'energy': [0.3, 0.7],
                'danceability': [0.2, 0.5],
                'tempo': [80, 120]
            },
            'disgust': {
                'valence': [0.1, 0.3],
                'energy': [0.2, 0.6],
                'danceability': [0.1, 0.4],
                'tempo': [70, 110]
            }
        }
        
        # Sample music database (in production, this would be from Spotify API)
        self.sample_tracks = self._create_sample_tracks()
        
    def _create_sample_tracks(self) -> List[Dict]:
        """
        Create sample tracks for development
        In production, this would fetch from Spotify API
        """
        return [
            {
                'track_id': 'happy_001',
                'track_name': 'Happy Vibes',
                'artist_name': 'Sunny Day Band',
                'valence': 0.9,
                'energy': 0.8,
                'danceability': 0.7,
                'tempo': 128,
                'genre': 'pop'
            },
            {
                'track_id': 'sad_001',
                'track_name': 'Melancholy Blues',
                'artist_name': 'Rainy Weather',
                'valence': 0.2,
                'energy': 0.3,
                'danceability': 0.2,
                'tempo': 70,
                'genre': 'blues'
            },
            {
                'track_id': 'angry_001',
                'track_name': 'Fire Storm',
                'artist_name': 'Thunder Strike',
                'valence': 0.4,
                'energy': 0.9,
                'danceability': 0.6,
                'tempo': 160,
                'genre': 'rock'
            },
            {
                'track_id': 'neutral_001',
                'track_name': 'Peaceful Journey',
                'artist_name': 'Calm Waters',
                'valence': 0.5,
                'energy': 0.5,
                'danceability': 0.4,
                'tempo': 100,
                'genre': 'ambient'
            },
            {
                'track_id': 'surprise_001',
                'track_name': 'Unexpected Turn',
                'artist_name': 'Plot Twist',
                'valence': 0.7,
                'energy': 0.8,
                'danceability': 0.6,
                'tempo': 140,
                'genre': 'electronic'
            }
        ]
    
    def recommend_by_emotion(self, emotion: str, limit: int = 10) -> List[Dict]:
        """
        Recommend music based on detected emotion
        """
        if emotion not in self.emotion_music_map:
            emotion = 'neutral'
        
        emotion_features = self.emotion_music_map[emotion]
        recommendations = []
        
        for track in self.sample_tracks:
            score = self._calculate_similarity_score(track, emotion_features)
            if score > 0.3:  # Threshold for relevance
                recommendation = track.copy()
                recommendation['score'] = score
                recommendation['recommended_for'] = emotion
                recommendations.append(recommendation)
        
        # Sort by score and return top results
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        # If we don't have enough recommendations, add some random ones
        if len(recommendations) < limit:
            remaining_tracks = [t for t in self.sample_tracks 
                             if t['track_id'] not in [r['track_id'] for r in recommendations]]
            for track in remaining_tracks[:limit - len(recommendations)]:
                recommendation = track.copy()
                recommendation['score'] = 0.5  # Default score
                recommendation['recommended_for'] = emotion
                recommendations.append(recommendation)
        
        return recommendations[:limit]
    
    def _calculate_similarity_score(self, track: Dict, emotion_features: Dict) -> float:
        """
        Calculate how well a track matches the emotion features
        """
        score = 0.0
        total_weight = 0.0
        
        feature_weights = {
            'valence': 0.3,
            'energy': 0.25,
            'danceability': 0.2,
            'tempo': 0.25
        }
        
        for feature, weight in feature_weights.items():
            if feature in track and feature in emotion_features:
                track_value = track[feature]
                emotion_range = emotion_features[feature]
                
                if feature == 'tempo':
                    # Normalize tempo to 0-1 scale
                    track_value = min(track_value / 200.0, 1.0)
                    emotion_range = [r / 200.0 for r in emotion_range]
                
                # Check if track value is within emotion range
                if emotion_range[0] <= track_value <= emotion_range[1]:
                    # Perfect match
                    feature_score = 1.0
                else:
                    # Calculate distance from range
                    distance = min(
                        abs(track_value - emotion_range[0]),
                        abs(track_value - emotion_range[1])
                    )
                    feature_score = max(0, 1.0 - distance)
                
                score += feature_score * weight
                total_weight += weight
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def update_with_feedback(self, emotion: str, track_id: str, feedback: str):
        """
        Update recommendation algorithm based on user feedback
        This would be used for ML model training in production
        """
        # For now, just log the feedback
        print(f"Feedback received: {emotion} -> {track_id} -> {feedback}")
        
        # In production, this would:
        # 1. Store feedback in database
        # 2. Retrain recommendation model
        # 3. Update emotion-music mappings
        pass
    
    def generate_playlist(self, emotions: List[str], duration_minutes: int = 30) -> List[Dict]:
        """
        Generate a playlist based on multiple emotions
        """
        target_tracks = duration_minutes // 3  # Assume 3 minutes per track
        tracks_per_emotion = max(1, target_tracks // len(emotions))
        
        playlist = []
        for emotion in emotions:
            emotion_tracks = self.recommend_by_emotion(emotion, tracks_per_emotion)
            playlist.extend(emotion_tracks)
        
        # Remove duplicates
        seen_track_ids = set()
        unique_playlist = []
        for track in playlist:
            if track['track_id'] not in seen_track_ids:
                unique_playlist.append(track)
                seen_track_ids.add(track['track_id'])
        
        # Shuffle for variety
        random.shuffle(unique_playlist)
        
        return unique_playlist[:target_tracks]
    
    def get_emotion_stats(self) -> Dict:
        """
        Get statistics about emotion-music mappings
        """
        return {
            'supported_emotions': list(self.emotion_music_map.keys()),
            'total_tracks': len(self.sample_tracks),
            'emotion_features': self.emotion_music_map
        }

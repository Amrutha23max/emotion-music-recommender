import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class SpotifyService:
    """
    Service for interacting with Spotify Web API
    """
    
    def __init__(self):
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if self.client_id and self.client_secret:
            try:
                client_credentials_manager = SpotifyClientCredentials(
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )
                self.spotify = spotipy.Spotify(
                    client_credentials_manager=client_credentials_manager
                )
                self.enabled = True
            except Exception as e:
                print(f"Failed to initialize Spotify client: {e}")
                self.spotify = None
                self.enabled = False
        else:
            print("Spotify credentials not found. Running in demo mode.")
            self.spotify = None
            self.enabled = False
    
    async def get_track_info(self, track_id: str) -> Optional[Dict]:
        """
        Get detailed information about a track
        """
        if not self.enabled:
            return self._get_demo_track_info(track_id)
        
        try:
            track = self.spotify.track(track_id)
            audio_features = self.spotify.audio_features([track_id])[0]
            
            return {
                'track_id': track['id'],
                'track_name': track['name'],
                'artist_name': ', '.join([artist['name'] for artist in track['artists']]),
                'album_name': track['album']['name'],
                'duration_ms': track['duration_ms'],
                'preview_url': track['preview_url'],
                'external_url': track['external_urls']['spotify'],
                'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
                'audio_features': {
                    'danceability': audio_features['danceability'],
                    'energy': audio_features['energy'],
                    'valence': audio_features['valence'],
                    'tempo': audio_features['tempo'],
                    'acousticness': audio_features['acousticness'],
                    'instrumentalness': audio_features['instrumentalness'],
                    'speechiness': audio_features['speechiness']
                } if audio_features else None
            }
        except Exception as e:
            print(f"Error fetching track info: {e}")
            return None
    
    async def search_tracks(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for tracks on Spotify
        """
        if not self.enabled:
            return self._get_demo_search_results(query, limit)
        
        try:
            results = self.spotify.search(q=query, type='track', limit=limit)
            tracks = []
            
            for track in results['tracks']['items']:
                track_info = {
                    'track_id': track['id'],
                    'track_name': track['name'],
                    'artist_name': ', '.join([artist['name'] for artist in track['artists']]),
                    'album_name': track['album']['name'],
                    'duration_ms': track['duration_ms'],
                    'preview_url': track['preview_url'],
                    'external_url': track['external_urls']['spotify'],
                    'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'popularity': track['popularity']
                }
                tracks.append(track_info)
            
            return tracks
        except Exception as e:
            print(f"Error searching tracks: {e}")
            return []
    
    async def get_recommendations(self, seed_genres: List[str] = None, 
                                target_features: Dict = None, limit: int = 10) -> List[Dict]:
        """
        Get music recommendations from Spotify
        """
        if not self.enabled:
            return self._get_demo_recommendations(limit)
        
        try:
            # Use default values if not provided
            if not seed_genres:
                seed_genres = ['pop', 'rock', 'jazz']
            
            kwargs = {
                'seed_genres': seed_genres[:5],  # Spotify allows max 5 seeds
                'limit': limit
            }
            
            # Add target features if provided
            if target_features:
                for feature, value in target_features.items():
                    if feature in ['danceability', 'energy', 'valence', 'tempo']:
                        kwargs[f'target_{feature}'] = value
            
            results = self.spotify.recommendations(**kwargs)
            tracks = []
            
            for track in results['tracks']:
                track_info = {
                    'track_id': track['id'],
                    'track_name': track['name'],
                    'artist_name': ', '.join([artist['name'] for artist in track['artists']]),
                    'album_name': track['album']['name'],
                    'duration_ms': track['duration_ms'],
                    'preview_url': track['preview_url'],
                    'external_url': track['external_urls']['spotify'],
                    'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'popularity': track['popularity']
                }
                tracks.append(track_info)
            
            return tracks
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []
    
    def _get_demo_track_info(self, track_id: str) -> Dict:
        """
        Return demo track info when Spotify API is not available
        """
        demo_tracks = {
            'happy_001': {
                'track_id': 'happy_001',
                'track_name': 'Happy Vibes',
                'artist_name': 'Sunny Day Band',
                'album_name': 'Bright Days',
                'duration_ms': 210000,
                'preview_url': None,
                'external_url': 'https://open.spotify.com/track/demo',
                'image_url': 'https://via.placeholder.com/300x300?text=Happy+Vibes',
                'audio_features': {
                    'danceability': 0.7,
                    'energy': 0.8,
                    'valence': 0.9,
                    'tempo': 128,
                    'acousticness': 0.2,
                    'instrumentalness': 0.1,
                    'speechiness': 0.05
                }
            },
            'sad_001': {
                'track_id': 'sad_001',
                'track_name': 'Melancholy Blues',
                'artist_name': 'Rainy Weather',
                'album_name': 'Gray Skies',
                'duration_ms': 180000,
                'preview_url': None,
                'external_url': 'https://open.spotify.com/track/demo',
                'image_url': 'https://via.placeholder.com/300x300?text=Melancholy+Blues',
                'audio_features': {
                    'danceability': 0.2,
                    'energy': 0.3,
                    'valence': 0.2,
                    'tempo': 70,
                    'acousticness': 0.7,
                    'instrumentalness': 0.3,
                    'speechiness': 0.03
                }
            }
        }
        
        return demo_tracks.get(track_id, {
            'track_id': track_id,
            'track_name': 'Demo Track',
            'artist_name': 'Demo Artist',
            'album_name': 'Demo Album',
            'duration_ms': 200000,
            'preview_url': None,
            'external_url': 'https://open.spotify.com/track/demo',
            'image_url': 'https://via.placeholder.com/300x300?text=Demo+Track',
            'audio_features': {
                'danceability': 0.5,
                'energy': 0.5,
                'valence': 0.5,
                'tempo': 120,
                'acousticness': 0.5,
                'instrumentalness': 0.2,
                'speechiness': 0.05
            }
        })
    
    def _get_demo_search_results(self, query: str, limit: int) -> List[Dict]:
        """
        Return demo search results when Spotify API is not available
        """
        demo_results = [
            {
                'track_id': f'demo_{i}',
                'track_name': f'Demo Song {i}',
                'artist_name': f'Demo Artist {i}',
                'album_name': f'Demo Album {i}',
                'duration_ms': 200000 + (i * 10000),
                'preview_url': None,
                'external_url': 'https://open.spotify.com/track/demo',
                'image_url': f'https://via.placeholder.com/300x300?text=Demo+Song+{i}',
                'popularity': 50 + (i * 5)
            }
            for i in range(1, limit + 1)
        ]
        
        return demo_results
    
    def _get_demo_recommendations(self, limit: int) -> List[Dict]:
        """
        Return demo recommendations when Spotify API is not available
        """
        return self._get_demo_search_results("recommendations", limit)
    
    def is_enabled(self) -> bool:
        """
        Check if Spotify service is enabled
        """
        return self.enabled

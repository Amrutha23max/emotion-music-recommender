import cv2
import numpy as np
import tensorflow as tf
from typing import Dict, List, Optional
import os

class EmotionDetector:
    """
    Emotion detection using computer vision and deep learning
    """
    
    def __init__(self, model_path: str = None):
        self.emotions = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Load pre-trained model or use placeholder
        if model_path and os.path.exists(model_path):
            self.model = tf.keras.models.load_model(model_path)
        else:
            # Create a simple placeholder model for development
            self.model = self._create_placeholder_model()
        
        self.model_loaded = True
    
    def _create_placeholder_model(self):
        """
        Create a placeholder model for development/testing
        Replace this with actual trained model later
        """
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(48, 48, 1)),
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(len(self.emotions), activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def detect_faces(self, image: np.ndarray) -> List[tuple]:
        """
        Detect faces in image using OpenCV
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(30, 30)
        )
        return faces
    
    def preprocess_face(self, face_image: np.ndarray) -> np.ndarray:
        """
        Preprocess face image for emotion detection
        """
        # Convert to grayscale if needed
        if len(face_image.shape) == 3:
            face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
        
        # Resize to model input size
        face_image = cv2.resize(face_image, (48, 48))
        
        # Normalize pixel values
        face_image = face_image.astype('float32') / 255.0
        
        # Reshape for model input
        face_image = np.expand_dims(face_image, axis=-1)
        face_image = np.expand_dims(face_image, axis=0)
        
        return face_image
    
    def detect_emotion(self, image: np.ndarray) -> Optional[Dict]:
        """
        Detect emotion from image
        """
        if not self.model_loaded:
            return None
        
        # Detect faces
        faces = self.detect_faces(image)
        
        if len(faces) == 0:
            return None
        
        # Use the largest face
        largest_face = max(faces, key=lambda f: f[2] * f[3])
        x, y, w, h = largest_face
        
        # Extract face region
        face_image = image[y:y+h, x:x+w]
        
        # Preprocess face
        processed_face = self.preprocess_face(face_image)
        
        # Predict emotion
        predictions = self.model.predict(processed_face, verbose=0)
        emotion_probabilities = predictions[0]
        
        # Get top emotion
        top_emotion_idx = np.argmax(emotion_probabilities)
        top_emotion = self.emotions[top_emotion_idx]
        confidence = float(emotion_probabilities[top_emotion_idx])
        
        # Create emotion probability dictionary
        all_emotions = {
            emotion: float(prob) 
            for emotion, prob in zip(self.emotions, emotion_probabilities)
        }
        
        return {
            'emotion': top_emotion,
            'confidence': confidence,
            'all_emotions': all_emotions,
            'face_location': {
                'x': int(x), 'y': int(y), 
                'width': int(w), 'height': int(h)
            }
        }
    
    def detect_emotion_realtime(self, frame: np.ndarray) -> Dict:
        """
        Detect emotion from video frame with face tracking
        """
        result = self.detect_emotion(frame)
        
        if result:
            # Draw bounding box and emotion on frame
            face_loc = result['face_location']
            x, y, w, h = face_loc['x'], face_loc['y'], face_loc['width'], face_loc['height']
            
            # Draw rectangle around face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Draw emotion text
            emotion_text = f"{result['emotion']}: {result['confidence']:.2f}"
            cv2.putText(frame, emotion_text, (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
            result['annotated_frame'] = frame
        
        return result or {'emotion': 'neutral', 'confidence': 0.0, 'annotated_frame': frame}
    
    def get_supported_emotions(self) -> List[str]:
        """
        Get list of supported emotions
        """
        return self.emotions.copy()
    
    def get_model_info(self) -> Dict:
        """
        Get information about the loaded model
        """
        return {
            'model_type': 'CNN',
            'input_shape': '(48, 48, 1)',
            'emotions': self.emotions,
            'total_emotions': len(self.emotions),
            'model_loaded': self.model_loaded
        }
    
    def update_model(self, new_model_path: str) -> bool:
        """
        Update the emotion detection model
        """
        try:
            if os.path.exists(new_model_path):
                self.model = tf.keras.models.load_model(new_model_path)
                self.model_loaded = True
                return True
            return False
        except Exception:
            return False

import os
import joblib
import numpy as np
import random
from tensorflow.keras.models import load_model
from django.conf import settings
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

# Paths
NN_PATH = os.path.join(settings.BASE_DIR, 'movies', 'joblibs', 'NN')
MODEL_PATH = os.path.join(NN_PATH, 'movie_rating_model.keras')
SCALER_PATH = os.path.join(NN_PATH, 'rating_count_scaler.pkl')
MOVIES_DATA_PATH = os.path.join(NN_PATH, 'final_movie_data.pkl')

def recommend_movies_nn(movie_titles, top_k=10):
    """
    Recommend movies using a neural network model based on input movie titles.
    
    Args:
        movie_titles: List of movie titles or single movie title
        top_k: Number of recommendations to return for each input title
    
    Returns:
        Dictionary with input titles as keys and recommendation lists as values
    """
    # Reset random seed for different results each time
    import time
    random.seed(int(time.time()))
    
    if isinstance(movie_titles, str):
        movie_titles = [movie_titles]
    
    # Load the pre-trained model and movie data with error handling
    try:
        model = load_model(MODEL_PATH)
        movies_data = joblib.load(MOVIES_DATA_PATH)
        logger.info("NN model files loaded successfully")
    except Exception as e:
        logger.warning(f"Failed to load NN model files: {e}")
        return {title: "Model data not available" for title in movie_titles}
    
    results = {}
    
    # Features to use for the neural network (21 features total)
    feature_columns = [col for col in movies_data.columns 
                      if col not in ['title', 'genres', 'movieId', 'rating_count', 'avg_rating']]
    
    for title in movie_titles:
        try:
            title = title.strip()
            
            # Find the input movie
            movie_match = movies_data[movies_data['title'].str.lower() == title.lower()]
        
            if movie_match.empty:
                results[title] = [f"Movie '{title}' not found in database."]
                continue
                
            # Get input movie features
            input_features = movie_match[feature_columns].values[0].astype('float32')
            
            # Get features for all movies in the dataset
            all_features = movies_data[feature_columns].values.astype('float32')
            
            # Calculate cosine similarity between input movie and all movies
            input_features = input_features.reshape(1, -1)
            similarities = cosine_similarity(input_features, all_features)[0]
        
            # Add small random noise to similarities for variety (without destroying ranking too much)
            noise = np.random.randn(len(similarities)) * 0.01  # Small random noise
            similarities = similarities + noise
            
            # Exclude the input movie itself
            input_index = movie_match.index[0]
            similarities[input_index] = -1
            
            # Get more candidates than requested for randomization
            search_k = min(top_k * 3, len(movies_data))  # Get 3x more results or all available
            top_indices = np.argsort(similarities)[::-1][:search_k]
            
            # Extract movie titles from candidates
            candidate_recommendations = movies_data.iloc[top_indices]['title'].tolist()
            
            # Randomly shuffle and select the requested number of recommendations
            if len(candidate_recommendations) > top_k:
                random.shuffle(candidate_recommendations)
                recommendations = candidate_recommendations[:top_k]
            else:
                recommendations = candidate_recommendations
            
            results[title] = recommendations
        
        except Exception as e:
            logger.error(f"Error processing movie '{title}': {e}")
            results[title] = "Error processing recommendation"
    
    return results


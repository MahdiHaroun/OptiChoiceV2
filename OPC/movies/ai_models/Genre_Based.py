import joblib
import os
import numpy as np
from django.conf import settings
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

# Define the base directory for joblib files
GENRE_BASED_PATH = os.path.join(settings.BASE_DIR, 'movies', 'joblibs', 'Genre-Based')

# Initialize variables
movies = None
genre_matrix = None
title_index = None

# Load data with error handling
try:
    movies = joblib.load(os.path.join(GENRE_BASED_PATH, 'movies_genre_based.joblib'))
    genre_matrix = joblib.load(os.path.join(GENRE_BASED_PATH, 'genre_Based_matrix.joblib'))
    title_index = joblib.load(os.path.join(GENRE_BASED_PATH, 'title_index_genre-based.joblib'))
    logger.info("Genre-based model files loaded successfully")
except Exception as e:
    logger.warning(f"Failed to load Genre-based model files: {e}")
    movies = None
    genre_matrix = None
    title_index = {}

def recommend_movies_by_genre(favorite_movies, number_of_results=5):
    """
    Generate random genre-based movie recommendations for each favorite movie.

    Args:
        favorite_movies (list): List of favorite movie titles.
        number_of_results (int): Number of random recommendations to return.

    Returns:
        dict: Mapping of favorite movie to list of recommended titles.
    """
    # Check if model data is available
    if genre_matrix is None or movies is None or not title_index:
        logger.warning("Genre-based model data not available, returning empty recommendations")
        return {movie: "Model data not available" for movie in favorite_movies}
    
    recommendations = {}

    for movie_name in favorite_movies:
        try:
            idx = title_index.get(movie_name)

            if idx is None:
                recommendations[movie_name] = "Movie not found"
                continue

            selected_vector = genre_matrix[idx]
            similarity_scores = cosine_similarity([selected_vector], genre_matrix)[0]
            similarity_scores[idx] = -1  # exclude itself

            all_indices = np.arange(len(similarity_scores))
            sorted_indices = all_indices[np.argsort(similarity_scores)[::-1]]
            shuffled_indices = np.random.permutation(sorted_indices)

            selected_indices = shuffled_indices[:number_of_results]
            recommended_titles = movies.iloc[selected_indices]['title'].tolist()

            recommendations[movie_name] = recommended_titles
        
        except Exception as e:
            logger.error(f"Error processing movie '{movie_name}': {e}")
            recommendations[movie_name] = "Error processing recommendation"

    return recommendations

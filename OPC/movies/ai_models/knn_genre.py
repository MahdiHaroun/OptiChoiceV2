import os
from django.conf import settings
import joblib
import random
import logging

logger = logging.getLogger(__name__)

# Define the base directory for joblib files
KNN_GENRE_PATH = os.path.join(settings.BASE_DIR, 'movies', 'joblibs', 'GenreKnn')

# Initialize variables
model = None
movie_index_to_title = None
title_to_index = {}
features = None

# Load pre-trained components with error handling
try:
    model = joblib.load(os.path.join(KNN_GENRE_PATH, 'genre_knn_model.joblib'))
    movie_index_to_title = joblib.load(os.path.join(KNN_GENRE_PATH, 'genre_index_to_title.joblib'))
    title_to_index = joblib.load(os.path.join(KNN_GENRE_PATH, 'genre_title_to_index.joblib'))
    features = joblib.load(os.path.join(KNN_GENRE_PATH, 'genre_movies_df.joblib'))
    logger.info("KNN Genre model files loaded successfully")
except Exception as e:
    logger.warning(f"Failed to load KNN Genre model files: {e}")
    model = None
    movie_index_to_title = {}
    title_to_index = {}
    features = None

GENRE_COLUMNS = ['Action', 'Adventure', 'Animation', 'Children', 'Comedy', 'Crime',
                 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'IMAX',
                 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']

# Extract genre features for all movies if available
if features is not None:
    features = features[GENRE_COLUMNS]


def recommend_movies_by_knn_genre(movie_titles, n=5):
    """
    Recommend N genre-similar movies for each input title using KNN.
    Returns a dict: {movie_title: [list of recommended movie titles]}
    The recommendations are randomly sampled from a default larger pool for variability.
    """
    # Check if model data is available
    if model is None or features is None or not title_to_index:
        logger.warning("KNN Genre model data not available, returning empty recommendations")
        return {title: "Model data not available" for title in movie_titles}
    
    results = {}
    default_pool_size = 25  # Can be adjusted if needed

    for title in movie_titles:
        try:
            if title not in title_to_index:
                results[title] = "Movie not found"
                continue

            idx = title_to_index[title]
            input_vector = features.iloc[idx].values.reshape(1, -1)

            # Get a larger pool of neighbors
            distances, indices = model.kneighbors(input_vector, n_neighbors=default_pool_size + 1)

            # Flatten and remove the movie itself
            neighbor_indices = [i for i in indices.flatten() if i != idx]

            # Shuffle and pick n unique recommendations
            sampled_indices = random.sample(neighbor_indices, min(n, len(neighbor_indices)))

            recommended_titles = [movie_index_to_title[i] for i in sampled_indices]
            results[title] = recommended_titles
        
        except Exception as e:
            logger.error(f"Error processing movie '{title}': {e}")
            results[title] = "Error processing recommendation"

    return results

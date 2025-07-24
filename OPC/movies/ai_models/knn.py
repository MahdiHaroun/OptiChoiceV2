import os
from django.conf import settings
import joblib
import logging

logger = logging.getLogger(__name__)

# Define the base directory for joblib files
KNN_PATH = os.path.join(settings.BASE_DIR, 'movies', 'joblibs', 'KNN')

# Initialize variables
model = None
movie_mapping = None
reverse_mapping = None
sparse_matrix = None

# Try to load data with error handling
try:
    model = joblib.load(os.path.join(KNN_PATH, 'knn_model.joblib'))
    movie_mapping = joblib.load(os.path.join(KNN_PATH, 'movie_mapping.joblib'))
    reverse_mapping = joblib.load(os.path.join(KNN_PATH, 'reverse_mapping.joblib'))
    sparse_matrix = joblib.load(os.path.join(KNN_PATH, 'sparse_matrix.joblib'))
    logger.info("KNN model files loaded successfully")
except Exception as e:
    logger.warning(f"Failed to load KNN model files: {e}")
    # Set default values or None
    model = None
    movie_mapping = {}
    reverse_mapping = {}
    sparse_matrix = None



import random

def recommend_movies_knn(movie_titles, n=5, top_k=20):
    """
    Recommend N random movies selected from the top K most similar movies.
    - n: number of final recommendations
    - top_k: number of top similar movies to consider for random sampling
    """
    results = {}

    # Check if model files are loaded
    if model is None or not movie_mapping or not reverse_mapping or sparse_matrix is None:
        for title in movie_titles:
            results[title] = "AI model not available - please check model files"
        return results

    for title in movie_titles:
        if title not in reverse_mapping:
            results[title] = "Movie not found"
            continue

        idx = reverse_mapping[title]

        # Get top K similar (excluding self)
        distances, indices = model.kneighbors(sparse_matrix[idx], n_neighbors=top_k + 1)
        similar_indices = [i for i in indices.flatten() if i != idx]

        # Map to titles
        similar_titles = [movie_mapping[i] for i in similar_indices]

        # Randomly select N from the top K similar titles
        if len(similar_titles) >= n:
            recommended = random.sample(similar_titles, n)
        else:
            recommended = similar_titles  # fallback if not enough results

        results[title] = recommended

    return results

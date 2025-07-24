import os
import joblib
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Define the base path for BOW models
BOW_MODEL_PATH = os.path.join(settings.BASE_DIR, 'movies', 'joblibs', 'BOW')

# Initialize variables
tfidf = None
model = None
title_to_index = None
tfidf_matrix = None

# Load joblib files using relative paths with error handling
try:
    tfidf = joblib.load(os.path.join(BOW_MODEL_PATH, 'tfidf_vectorizer.joblib'))
    model = joblib.load(os.path.join(BOW_MODEL_PATH, 'nn_model.joblib'))
    title_to_index = joblib.load(os.path.join(BOW_MODEL_PATH, 'title_to_index.joblib'))
    tfidf_matrix = joblib.load(os.path.join(BOW_MODEL_PATH, 'tfidf_matrix.joblib'))
    logger.info("TF-IDF model files loaded successfully")
except Exception as e:
    logger.warning(f"Failed to load TF-IDF model files: {e}")
    tfidf = None
    model = None
    title_to_index = {}
    tfidf_matrix = None

def recommend_movies_sparse_list(movie_titles, n=5):
    recommendations = {}
    
    # Check if model files are loaded
    if tfidf is None or model is None or not title_to_index or tfidf_matrix is None:
        for movie_title in movie_titles:
            recommendations[movie_title] = "TF-IDF model not available - please check model files"
        return recommendations
    
    for movie_title in movie_titles:
        if movie_title not in title_to_index:
            recommendations[movie_title] = f"'{movie_title}' not found."
            continue

        idx = title_to_index[movie_title]
        distances, indices = model.kneighbors(tfidf_matrix[idx], n_neighbors=n + 1)
        recommended = [list(title_to_index.keys())[list(title_to_index.values()).index(i)]
                       for i in indices.flatten() if i != idx]
        recommendations[movie_title] = recommended[:n]
    return recommendations
import joblib
import os
from django.conf import settings
import random
import logging

logger = logging.getLogger(__name__)

GRHR_PATH = os.path.join(settings.BASE_DIR, 'movies', 'joblibs', 'GRHR')

# Initialize variable
movies_df = None

# Load data with error handling
try:
    movies_df = joblib.load(os.path.join(GRHR_PATH, 'GRHR.joblib'))
    logger.info("GRHR model files loaded successfully")
except Exception as e:
    logger.warning(f"Failed to load GRHR model files: {e}")
    movies_df = None


def recommend_movies_GRHR(selected_genres, n=5):
    # Check if model data is available
    if movies_df is None:
        logger.warning("GRHR model data not available, returning empty recommendations")
        return []
    
    try:
        df = movies_df.copy()

        for genre in selected_genres:
            if genre not in df.columns:
                return { "error": f"Genre '{genre}' not found." }

            df = df[df[genre] == 1]

        df = df.dropna(subset=['avg_rating'])
        if df.empty:
            return { "error": "No matching movies found for selected genres." }

        top_movies = df.sort_values(by='avg_rating', ascending=False).head(25)
        sampled = top_movies.sample(n=min(n, len(top_movies)), random_state=random.randint(1, 9999))

        return sampled['title'].tolist()
    
    except Exception as e:
        logger.error(f"Error in recommend_movies_GRHR: {e}")
        return { "error": f"Error processing recommendation: {str(e)}" }
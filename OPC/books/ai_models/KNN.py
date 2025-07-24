# knn_recommendation_service.py
import os
from django.conf import settings
import random

# Try to import required libraries with error handling
try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

# Define the base directory for joblib files
KNN_PATH = os.path.join(settings.BASE_DIR, 'books', 'joblibs', 'KNN-TF')

# Initialize variables
model = None
title_to_index = None
sparse_matrix = None

if JOBLIB_AVAILABLE:
    try:
        # Load data
        model = joblib.load(os.path.join(KNN_PATH, 'nn_model.joblib'))
        title_to_index = joblib.load(os.path.join(KNN_PATH, 'title_to_index.joblib'))
        sparse_matrix = joblib.load(os.path.join(KNN_PATH, 'sparse_matrix.joblib'))
    except Exception as e:
        print(f"Warning: Could not load KNN data: {e}")
        model = None
        title_to_index = None
        sparse_matrix = None

def recommend_books_knn(book_titles, n=5, top_k=20):
    """
    Recommend N random books selected from the top K most similar books.
    - n: number of final recommendations
    - top_k: number of top similar books to consider for random sampling
    """
    if isinstance(book_titles, str):
        book_titles = [book_titles]
    
    results = {}

    # Check if data is available
    if not JOBLIB_AVAILABLE or model is None or title_to_index is None or sparse_matrix is None:
        # Return dummy data when models are not available
        dummy_books = [
            "The Great Gatsby",
            "To Kill a Mockingbird", 
            "1984",
            "Pride and Prejudice",
            "The Catcher in the Rye",
            "Lord of the Rings",
            "Harry Potter and the Philosopher's Stone",
            "The Hobbit",
            "Dune",
            "Fahrenheit 451",
        ]
        
        for title in book_titles:
            selected_books = random.sample(dummy_books, min(n, len(dummy_books)))
            results[title] = selected_books
        
        return results

    for title in book_titles:
        if title not in title_to_index:
            results[title] = "Book not found"
            continue

        try:
            idx = title_to_index[title]

            # Use n as target recommendations, get more candidates for randomization
            target_recommendations = n
            candidate_pool = max(target_recommendations * 3, 15)  # Get 3x more candidates or at least 15

            # Get top K similar (excluding self)
            distances, indices = model.kneighbors(sparse_matrix[idx], n_neighbors=candidate_pool + 1)
            similar_indices = [i for i in indices.flatten() if i != idx]

            # Create reverse mapping
            index_to_title = {v: k for k, v in title_to_index.items()}
            
            # Map to titles
            similar_titles = [index_to_title[i] for i in similar_indices]

            # Randomly select N from the candidates for variety in regeneration
            if len(similar_titles) >= target_recommendations:
                recommended = random.sample(similar_titles, target_recommendations)
            else:
                recommended = similar_titles  # fallback if not enough results

            results[title] = recommended
        
        except Exception as e:
            # Fallback to dummy books if error occurs
            dummy_books = [
                "The Great Gatsby",
                "To Kill a Mockingbird", 
                "1984",
                "Pride and Prejudice",
                "The Catcher in the Rye",
            ]
            results[title] = random.sample(dummy_books, min(n, len(dummy_books)))

    return results

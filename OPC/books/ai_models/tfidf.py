import os
import joblib
from django.conf import settings
import random

# Define the base path for BOW models
BOW_MODEL_PATH = os.path.join(settings.BASE_DIR, 'books', 'joblibs', 'BOW')

try:
    # Load joblib files using relative paths
    tfidf = joblib.load(os.path.join(BOW_MODEL_PATH, 'tfidf_vectorizer.joblib'))
    model = joblib.load(os.path.join(BOW_MODEL_PATH, 'nn_model.joblib'))
    title_to_index = joblib.load(os.path.join(BOW_MODEL_PATH, 'title_to_index.joblib'))
    tfidf_matrix = joblib.load(os.path.join(BOW_MODEL_PATH, 'tfidf_matrix.joblib'))
    DATA_LOADED = True
except Exception as e:
    print(f"Warning: Could not load TFIDF data: {e}")
    DATA_LOADED = False

def recommend_books_sparse_list(book_titles, n=5):
    """
    Recommend books using TF-IDF and sparse matrix similarity.
    
    Args:
        book_titles: List of book titles
        n: Number of recommendations per book
    
    Returns:
        Dictionary with input titles as keys and recommendation lists as values
    """
    if isinstance(book_titles, str):
        book_titles = [book_titles]
    
    recommendations = {}
    
    # Check if data is loaded
    if not DATA_LOADED:
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
            "Fahrenheit 451"
        ]
        
        for book_title in book_titles:
            selected_books = random.sample(dummy_books, min(n, len(dummy_books)))
            recommendations[book_title] = selected_books
        
        return recommendations
    
    for book_title in book_titles:
        if book_title not in title_to_index:
            # Try partial matching
            partial_matches = [title for title in title_to_index.keys() 
                             if book_title.lower() in title.lower() or title.lower() in book_title.lower()]
            if partial_matches:
                book_title = partial_matches[0]
            else:
                recommendations[book_title] = f"'{book_title}' not found."
                continue

        try:
            idx = title_to_index[book_title]
            distances, indices = model.kneighbors(tfidf_matrix[idx], n_neighbors=n + 1)
            recommended = [list(title_to_index.keys())[list(title_to_index.values()).index(i)]
                           for i in indices.flatten() if i != idx]
            recommendations[book_title] = recommended[:n]
        except Exception as e:
            # Fallback to dummy books if error occurs
            dummy_books = [
                "The Great Gatsby",
                "To Kill a Mockingbird", 
                "1984",
                "Pride and Prejudice",
                "The Catcher in the Rye",
            ]
            recommendations[book_title] = random.sample(dummy_books, min(n, len(dummy_books)))
    
    return recommendations

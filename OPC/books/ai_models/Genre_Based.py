import joblib
import os
import numpy as np
from django.conf import settings
from sklearn.metrics.pairwise import cosine_similarity
import random

# Define the base directory for joblib files
GENRE_BASED_PATH = os.path.join(settings.BASE_DIR, 'books', 'joblibs', 'Genre_knn')

try:
    # Load data
    books_df = joblib.load(os.path.join(GENRE_BASED_PATH, 'books_df.joblib'))
    category_encoder = joblib.load(os.path.join(GENRE_BASED_PATH, 'category_encoder.joblib'))
    category_knn_sparse = joblib.load(os.path.join(GENRE_BASED_PATH, 'category_knn_sparse.joblib'))
    
    # Create title to index mapping
    title_to_index = {title: idx for idx, title in enumerate(books_df['Title'])}
    book_index_to_title = {idx: title for idx, title in enumerate(books_df['Title'])}
    
    DATA_LOADED = True
except Exception as e:
    print(f"Warning: Could not load Genre-Based data: {e}")
    DATA_LOADED = False


def recommend_books_by_genre_selection(selected_genres, number_of_results=10):
    """
    Generate book recommendations based on selected genres.
    
    Args:
        selected_genres (list): List of genre names selected by user.
        number_of_results (int): Number of recommendations to return.
    
    Returns:
        list: List of recommended book titles.
    """
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
            "Fahrenheit 451",
            "The Chronicles of Narnia",
            "Jane Eyre",
            "Wuthering Heights",
            "Brave New World",
            "The Picture of Dorian Gray"
        ]
        
        return random.sample(dummy_books, min(number_of_results, len(dummy_books)))
    
    try:
        # Convert genre names to lowercase for better matching
        selected_genres_lower = [genre.lower() for genre in selected_genres]
        
        # Find books that match the selected genres
        matching_books = []
        
        # Check if books_df has a 'genres' or 'categories' column
        if 'Category' in books_df.columns:
            genre_column = 'Category'
        elif 'categories' in books_df.columns:
            genre_column = 'categories'
        elif 'genre' in books_df.columns:
            genre_column = 'genre'
        else:
            # If no genre column found, fall back to random selection from all books
            all_titles = books_df['Title'].tolist()
            return random.sample(all_titles, min(number_of_results, len(all_titles)))
        
        # Filter books based on genres
        for idx, row in books_df.iterrows():
            book_categories = row[genre_column]
            # Handle the case where categories is a list or string
            if isinstance(book_categories, list):
                book_genres_str = ' '.join(book_categories).lower()
            else:
                book_genres_str = str(book_categories).lower()
            
            # Check if any selected genre is in the book's genres
            if any(genre in book_genres_str for genre in selected_genres_lower):
                matching_books.append(row['Title'])  # Note: Column is 'Title' not 'title'
        
        # If we found matching books, randomly select from them
        if matching_books:
            if len(matching_books) >= number_of_results:
                return random.sample(matching_books, number_of_results)
            else:
                # If not enough matching books, add more from general collection
                remaining_needed = number_of_results - len(matching_books)
                all_titles = books_df['Title'].tolist()
                # Remove already selected books to avoid duplicates
                remaining_books = [title for title in all_titles if title not in matching_books]
                if remaining_books:
                    additional_books = random.sample(remaining_books, min(remaining_needed, len(remaining_books)))
                    return matching_books + additional_books
                else:
                    return matching_books
        else:
            # No genre matches found, return random books
            all_titles = books_df['Title'].tolist()
            return random.sample(all_titles, min(number_of_results, len(all_titles)))
            
    except Exception as e:
        print(f"Error in genre-based recommendation: {e}")
        # Fallback to dummy books
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
        return random.sample(dummy_books, min(number_of_results, len(dummy_books)))
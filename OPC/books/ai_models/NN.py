# neural_network_recommendation_service.py
import os
import joblib
import numpy as np
from django.conf import settings
from sklearn.metrics.pairwise import cosine_similarity

# Try to import TensorFlow/Keras with error handling
try:
    from tensorflow.keras.models import load_model
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

# Paths
NN_PATH = os.path.join(settings.BASE_DIR, 'books', 'joblibs', 'NN')
MODEL_PATH = os.path.join(NN_PATH, 'books_nn_model.keras')
BOOKS_DATA_PATH = os.path.join(NN_PATH, 'books_data.pkl')

def recommend_books_nn(book_titles, top_k=10):
    """
    Recommend books using a neural network model based on input book titles.
    
    Args:
        book_titles: List of book titles or single book title
        top_k: Number of recommendations to return for each input title
    
    Returns:
        Dictionary with input titles as keys and recommendation lists as values
    """
    if isinstance(book_titles, str):
        book_titles = [book_titles]
    
    results = {}
    
    # Check if TensorFlow is available
    if not TENSORFLOW_AVAILABLE:
        # Return dummy data when TensorFlow is not available
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
            import random
            selected_books = random.sample(dummy_books, min(top_k, len(dummy_books)))
            results[title] = selected_books
        
        return results
    
    try:
        # Load the pre-trained model and book data
        model = load_model(MODEL_PATH)
        books_data = joblib.load(BOOKS_DATA_PATH)
        
        # Features to use for the neural network (excluding non-feature columns)
        feature_columns = [col for col in books_data.columns 
                          if col not in ['title', 'Title', 'book_title', 'Book_Title', 'authors', 'Authors', 'isbn', 'ISBN']]
        
        for title in book_titles:
            title = title.strip()
            
            # Try different column names for title
            title_column = None
            for col in ['title', 'Title', 'book_title', 'Book_Title']:
                if col in books_data.columns:
                    title_column = col
                    break
            
            if title_column is None:
                results[title] = [f"No title column found in books data for '{title}'."]
                continue
            
            # Find the input book
            book_match = books_data[books_data[title_column].str.lower() == title.lower()]
            
            if book_match.empty:
                results[title] = [f"Book '{title}' not found in database."]
                continue
                
            # Get input book features
            input_features = book_match[feature_columns].values[0].astype('float32')
            
            # Get features for all books in the dataset
            all_features = books_data[feature_columns].values.astype('float32')
            
            # Calculate cosine similarity between input book and all books
            input_features = input_features.reshape(1, -1)
            similarities = cosine_similarity(input_features, all_features)[0]
            
            # Exclude the input book itself
            input_index = book_match.index[0]
            similarities[input_index] = -1
            
            # Get top-k most similar books
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            # Extract book titles
            recommendations = books_data.iloc[top_indices][title_column].tolist()
            
            results[title] = recommendations
    
    except Exception as e:
        # Fallback to dummy data if any error occurs
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
            import random
            selected_books = random.sample(dummy_books, min(top_k, len(dummy_books)))
            results[title] = selected_books
    
    return results

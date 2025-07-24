# recommendation_service.py
import os
from django.conf import settings

# Try to import the required libraries, fallback to dummy implementation if not available
try:
    import joblib
    import torch
    from sentence_transformers import SentenceTransformer, util
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

EMB_PATH = os.path.join(settings.BASE_DIR, 'books', 'joblibs', 'Embeddings')

# Initialize variables
model = None
books = None
book_embeddings = None

if DEPENDENCIES_AVAILABLE:
    try:
        # Load model and data with CPU device to avoid CUDA mismatch
        model = SentenceTransformer('all-MiniLM-L6-v2')
        model = model.to('cpu')  # Ensure model is on CPU
        books = joblib.load(os.path.join(EMB_PATH, 'books_emb.pkl'))
        book_embeddings = torch.load(os.path.join(EMB_PATH, 'books_embeddings.pt'), map_location=torch.device('cpu'))
        book_embeddings = torch.nn.functional.normalize(book_embeddings, p=2, dim=1)
        # Ensure embeddings stay on CPU
        book_embeddings = book_embeddings.to('cpu')
    except Exception as e:
        print(f"Warning: Could not load embeddings data: {e}")
        DEPENDENCIES_AVAILABLE = False

def recommend_books_embeddings(book_titles, top_k=10):
    """
    Recommend books using embeddings for multiple input titles
    Args:
        book_titles: List of book titles
        top_k: Number of recommendations per book
    Returns:
        Dictionary with input titles as keys and recommendation lists as values
    """
    if isinstance(book_titles, str):
        book_titles = [book_titles]
    
    results = {}
    
    # Check if dependencies and data are available
    if not DEPENDENCIES_AVAILABLE or model is None or books is None or book_embeddings is None:
        # Return dummy data for development/testing
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
        
        for title in book_titles:
            # Return a subset of dummy books for each input
            import random
            selected_books = random.sample(dummy_books, min(top_k, len(dummy_books)))
            results[title] = selected_books
        
        return results
    
    # Original implementation for when dependencies are available
    for title in book_titles:
        title = title.strip()
        
        # Try different column names for title
        title_column = None
        for col in ['title', 'Title', 'book_title', 'Book_Title']:
            if col in books.columns:
                title_column = col
                break
        
        if title_column is None:
            results[title] = [f"No title column found in books data for '{title}'."]
            continue
            
        idx = books[books[title_column].str.lower() == title.lower()].index
        
        if len(idx) == 0:
            results[title] = [f"Book '{title}' not found in database."]
            continue
        
        try:
            # Get the book description for embedding
            description_column = None
            for col in ['description', 'Description', 'summary', 'Summary']:
                if col in books.columns:
                    description_column = col
                    break
            
            if description_column and description_column in books.columns:
                book_description = books.loc[idx[0], description_column]
            else:
                book_description = None
                
            if not book_description or str(book_description).lower() == 'nan':
                # Fallback to title if no description
                book_description = title
            
            query_embedding = model.encode(book_description, convert_to_tensor=True)
            # Ensure query embedding is on CPU to match book_embeddings
            query_embedding = query_embedding.to('cpu')
            query_embedding = torch.nn.functional.normalize(query_embedding, p=2, dim=0)

            scores = util.pytorch_cos_sim(query_embedding, book_embeddings)[0]
            top_results = torch.topk(scores, k=top_k + 1)

            recommendations = []
            for i, score in zip(top_results[1], top_results[0]):
                idx_int = i.item()
                recommended_title = books.iloc[idx_int][title_column]
                
                # Skip the input book itself
                if recommended_title.lower() == title.lower():
                    continue
                    
                recommendations.append(recommended_title)
                
                # Stop when we have enough recommendations
                if len(recommendations) >= top_k:
                    break
            
            results[title] = recommendations
            
        except Exception as e:
            results[title] = [f"Error processing '{title}': {str(e)}"]
    
    return results

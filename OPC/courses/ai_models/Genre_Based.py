import pandas as pd
import numpy as np
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

try:
    from django.conf import settings
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False
    settings = None

def categorize_course_by_keywords(title):
    """
    Categorize a course based on keywords in its title.
    
    Args:
        title (str): Course title
        
    Returns:
        list: List of genre categories
    """
    title_lower = title.lower()
    genres = []
    
    # Python
    if any(keyword in title_lower for keyword in ['python', 'django', 'flask', 'pandas', 'numpy']):
        genres.append('Python')
    
    # Cloud Computing
    if any(keyword in title_lower for keyword in ['cloud', 'aws', 'azure', 'docker', 'kubernetes', 'serverless', 'containerizing']):
        genres.append('CloudComputing')
    
    # Data Analysis
    if any(keyword in title_lower for keyword in ['data analysis', 'analytics', 'visualization', 'excel', 'sql']):
        genres.append('DataAnalysis')
    
    # Containers
    if any(keyword in title_lower for keyword in ['docker', 'container', 'kubernetes', 'microservice']):
        genres.append('Containers')
    
    # Machine Learning
    if any(keyword in title_lower for keyword in ['machine learning', 'deep learning', 'neural network', 'tensorflow', 'ml', 'ai', 'artificial intelligence']):
        genres.append('MachineLearning')
    
    # Computer Vision
    if any(keyword in title_lower for keyword in ['computer vision', 'image', 'opencv', 'visual']):
        genres.append('ComputerVision')
    
    # Data Science
    if any(keyword in title_lower for keyword in ['data science', 'data scientist', 'predictive', 'statistics']):
        genres.append('DataScience')
    
    # Big Data
    if any(keyword in title_lower for keyword in ['big data', 'hadoop', 'spark', 'hive', 'mapreduce']):
        genres.append('BigData')
    
    # Chatbot
    if any(keyword in title_lower for keyword in ['chatbot', 'bot', 'watson', 'assistant']):
        genres.append('Chatbot')
    
    # R Programming
    if any(keyword in title_lower for keyword in [' r ', 'r for', 'r programming', 'ggplot']):
        genres.append('R')
    
    # Backend Development
    if any(keyword in title_lower for keyword in ['backend', 'microservice', 'api', 'restful', 'java', 'spring', 'database']):
        genres.append('BackendDev')
    
    # Frontend Development
    if any(keyword in title_lower for keyword in ['frontend', 'javascript', 'react', 'angular', 'html', 'css', 'web development']):
        genres.append('FrontendDev')
    
    # Blockchain
    if any(keyword in title_lower for keyword in ['blockchain', 'bitcoin', 'cryptocurrency']):
        genres.append('Blockchain')
    
    return genres if genres else ['General']

def load_course_data():
    """
    Load course data from the CSV file.
    
    Returns:
        pd.DataFrame: Course data with genres
    """
    # Try to get the CSV path from Django settings if available
    if DJANGO_AVAILABLE and settings and hasattr(settings, 'BASE_DIR'):
        try:
            csv_path = os.path.join(settings.BASE_DIR, '..', 'course_db.csv')
        except:
            # Fallback to relative path
            csv_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'course_db.csv')
    else:
        # Use relative path when Django is not available
        csv_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'course_db.csv')
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path)
        
        # Ensure the required columns exist
        if 'COURSE_ID' not in df.columns or 'TITLE' not in df.columns:
            raise ValueError("CSV file must contain 'COURSE_ID' and 'TITLE' columns")
        
        # Rename columns for consistency
        df = df.rename(columns={'COURSE_ID': 'course_id', 'TITLE': 'course_name'})
        
        # Add genres based on course titles
        df['genres'] = df['course_name'].apply(categorize_course_by_keywords)
        
        return df
        
    except FileNotFoundError:
        # Fallback: create dummy data if CSV is not found
        print("Course CSV file not found, using dummy data")
        return create_dummy_course_data()
    except Exception as e:
        print(f"Error loading course data: {str(e)}, using dummy data")
        return create_dummy_course_data()

def create_dummy_course_data():
    """
    Create dummy course data for testing.
    
    Returns:
        pd.DataFrame: Dummy course data
    """
    dummy_courses = [
        {'course_id': 'PY001', 'course_name': 'Python for Data Science', 'genres': ['Python', 'DataScience']},
        {'course_id': 'ML001', 'course_name': 'Machine Learning with Python', 'genres': ['MachineLearning', 'Python']},
        {'course_id': 'CC001', 'course_name': 'Cloud Computing Fundamentals', 'genres': ['CloudComputing']},
        {'course_id': 'DA001', 'course_name': 'Data Analysis with R', 'genres': ['DataAnalysis', 'R']},
        {'course_id': 'CV001', 'course_name': 'Computer Vision Basics', 'genres': ['ComputerVision', 'MachineLearning']},
        {'course_id': 'BD001', 'course_name': 'Big Data with Spark', 'genres': ['BigData', 'DataScience']},
        {'course_id': 'WD001', 'course_name': 'Full Stack Web Development', 'genres': ['FrontendDev', 'BackendDev']},
        {'course_id': 'BC001', 'course_name': 'Blockchain Fundamentals', 'genres': ['Blockchain']},
        {'course_id': 'CB001', 'course_name': 'Building Chatbots with AI', 'genres': ['Chatbot', 'MachineLearning']},
        {'course_id': 'CT001', 'course_name': 'Docker and Kubernetes', 'genres': ['Containers', 'CloudComputing']},
    ]
    
    return pd.DataFrame(dummy_courses)

def recommend_courses_by_genre(selected_genres, number_of_results=5):
    """
    Recommend courses based on selected genres.
    
    Args:
        selected_genres (list): List of selected genre strings
        number_of_results (int): Number of recommendations to return
        
    Returns:
        list: List of recommended course names
    """
    try:
        # Load course data
        courses_df = load_course_data()
        
        if courses_df.empty:
            return ["No courses available"]
        
        # Filter courses that match any of the selected genres
        matching_courses = []
        
        for _, course in courses_df.iterrows():
            course_genres = course['genres'] if isinstance(course['genres'], list) else []
            
            # Check if any selected genre matches the course genres
            if any(genre in course_genres for genre in selected_genres):
                matching_courses.append({
                    'course_id': course['course_id'],
                    'course_name': course['course_name'],
                    'genres': course_genres,
                    'match_score': len(set(selected_genres) & set(course_genres))
                })
        
        if not matching_courses:
            return ["No courses found for the selected genres"]
        
        # Sort by match score (how many genres match) and randomize within same scores
        matching_courses.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Add some randomization to avoid always returning the same results
        np.random.shuffle(matching_courses)
        
        # Return the top recommendations
        recommendations = [course['course_name'] for course in matching_courses[:number_of_results]]
        
        return recommendations
        
    except Exception as e:
        print(f"Error in recommend_courses_by_genre: {str(e)}")
        return [f"Error generating recommendations: {str(e)}"]

# Additional function for backwards compatibility
def recommend_courses_by_genre_legacy(favorite_courses, number_of_results=5):
    """
    Legacy function for course-to-course recommendations (not genre-based).
    This is kept for compatibility with the existing API structure.
    
    Args:
        favorite_courses (list): List of favorite course titles
        number_of_results (int): Number of recommendations to return
        
    Returns:
        dict: Mapping of favorite course to list of recommended titles
    """
    courses_df = load_course_data()
    recommendations = {}
    
    for course_name in favorite_courses:
        # Find the course in our dataset
        matching_course = courses_df[courses_df['course_name'].str.contains(course_name, case=False, na=False)]
        
        if matching_course.empty:
            recommendations[course_name] = ["Course not found"]
            continue
        
        # Get genres for this course
        course_genres = matching_course.iloc[0]['genres']
        if isinstance(course_genres, list) and course_genres:
            # Use the genre-based recommendation
            recommended_courses = recommend_courses_by_genre(course_genres, number_of_results)
            recommendations[course_name] = recommended_courses
        else:
            recommendations[course_name] = ["No similar courses found"]
    
    return recommendations

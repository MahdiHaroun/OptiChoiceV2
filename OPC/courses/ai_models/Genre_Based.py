import pandas as pd
import numpy as np
import os

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
        except Exception:
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

def recommend_courses_by_genre(selected_genres, number_of_results=5, similarity_threshold=0.3):
    """
    Recommend courses based on selected genres with similarity threshold filtering.
    
    Args:
        selected_genres (list): List of selected genre strings
        number_of_results (int): Number of recommendations to return
        similarity_threshold (float): Minimum similarity score (0.0-1.0) to include results
        
    Returns:
        list: List of recommended course names, empty if similarity too low
    """
    try:
        # Load course data
        courses_df = load_course_data()
        
        if courses_df.empty:
            return []
        
        # If too many genres are selected, similarity will be very low
        if len(selected_genres) > 8:  # Threshold for "too many" genres
            return []
        
        # Calculate similarity scores for each course
        matching_courses = []
        
        for _, course in courses_df.iterrows():
            course_genres = course['genres'] if isinstance(course['genres'], list) else []
            
            if not course_genres:
                continue
                
            # Calculate similarity score using Jaccard similarity
            # Jaccard = |intersection| / |union|
            intersection = len(set(selected_genres) & set(course_genres))
            union = len(set(selected_genres) | set(course_genres))
            
            if union == 0:
                continue
                
            jaccard_similarity = intersection / union
            
            # Calculate a weighted score that considers:
            # 1. Jaccard similarity (main factor)
            # 2. Coverage: how many of the selected genres are covered
            # 3. Specificity: prefer courses with fewer total genres (more specific)
            
            coverage_ratio = intersection / len(selected_genres) if len(selected_genres) > 0 else 0
            specificity_bonus = 1 / (len(course_genres) + 1)  # Prefer more specific courses
            
            # Combined similarity score
            similarity_score = (
                jaccard_similarity * 0.6 +      # 60% weight on Jaccard similarity
                coverage_ratio * 0.3 +          # 30% weight on coverage
                specificity_bonus * 0.1          # 10% weight on specificity
            )
            
            # Only include courses that meet the similarity threshold
            if similarity_score >= similarity_threshold:
                matching_courses.append({
                    'course_id': course['course_id'],
                    'course_name': course['course_name'],
                    'genres': course_genres,
                    'similarity_score': similarity_score,
                    'jaccard_similarity': jaccard_similarity,
                    'coverage_ratio': coverage_ratio,
                    'match_count': intersection
                })
        
        # If no courses meet the similarity threshold, return empty list
        if not matching_courses:
            return []
        
        # Sort by similarity score (highest first)
        matching_courses.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Add some controlled randomization within similar score ranges
        # Group by similarity score ranges and shuffle within groups
        score_groups = {}
        for course in matching_courses:
            score_range = round(course['similarity_score'], 1)  # Group by 0.1 increments
            if score_range not in score_groups:
                score_groups[score_range] = []
            score_groups[score_range].append(course)
        
        # Shuffle within each score group and reconstruct the list
        final_courses = []
        for score_range in sorted(score_groups.keys(), reverse=True):
            group_courses = score_groups[score_range]
            np.random.shuffle(group_courses)
            final_courses.extend(group_courses)
        
        # Return the top recommendations
        recommendations = [course['course_name'] for course in final_courses[:number_of_results]]
        
        # Debug information (can be removed in production)
        if recommendations:
            print(f"Genre recommendation: {len(selected_genres)} genres selected, "
                  f"{len(matching_courses)} courses above threshold {similarity_threshold}, "
                  f"returning {len(recommendations)} recommendations")
            for course in final_courses[:3]:  # Log top 3 for debugging
                print(f"  - {course['course_name']}: score={course['similarity_score']:.3f}, "
                      f"jaccard={course['jaccard_similarity']:.3f}, coverage={course['coverage_ratio']:.3f}")
        
        return recommendations
        
    except Exception as e:
        print(f"Error in recommend_courses_by_genre: {str(e)}")
        return []

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

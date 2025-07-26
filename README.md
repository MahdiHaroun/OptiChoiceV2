p# OptiChoice - Comprehensive System Documentation

![OptiChoice Logo](logo.png)

## Deployment Status

- Deployed on www.optichoice.me

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Authentication System](#authentication-system)
4. [AI Models & Recommendation Engine](#ai-models--recommendation-engine)
5. [Database Models](#database-models)
6. [API Endpoints](#api-endpoints)
7. [Services & External Dependencies](#services--external-dependencies)
8. [Frontend Implementation](#frontend-implementation)
9. [Deployment & Infrastructure](#deployment--infrastructure)
10. [Security Features](#security-features)
11. [Configuration Management](#configuration-management)
12. [Development & Testing](#development--testing)

---

## Project Overview

**OptiChoice** is a Django-based multi-domain recommendation system that provides AI-powered suggestions for:

- **Movies** 
- **Books** 
- **Courses** 

### Key Features

- Multiple AI recommendation algorithms
- JWT-based authentication with email verification
- RESTful API architecture
- Real-time search with autocomplete
- Recommendation history tracking
- Responsive web interface
-
---

## System Architecture

### Technology Stack

- **Backend**: Django 5.2.1 + Django REST Framework
- **Database**: SQLite (development)
- **Authentication**: JWT + Session-based
- **AI/ML**: TensorFlow, scikit-learn, sentence-transformers
- **Frontend**: Django Templates + JavaScript (AJAX)
- **Deployment**: Gunicorn + Nginx
- **Email**: SMTP (Gmail integration)

### Application Structure

```
OPC/
├── authentication/          # User management & auth
├── movies/                 # Movie recommendations
├── books/                  # Book recommendations
├── courses/                # Course recommendations
├── OPC/                    # Project settings
├── static/                 # Static assets
└── templates/              # HTML templates
```

---

## Authentication System

### User Authentication Flow

#### 1. Registration Process

```python
# Two-phase registration for security
1. User submits registration form
2. Registration data stored in session (not database)
3. Activation email sent with temporary token
4. User clicks activation link
5. Account created and email verified
6. Welcome email sent
```

#### 2. Authentication Models

```python
# UserProfile Model (authentication/models.py)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_verified = models.BooleanField(default=False)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)
    password_reset_sent_at = models.DateTimeField(null=True, blank=True)
    account_deletion_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### 3. Security Features

- **Email Verification**: Required before login
- **Session Management**: Remember me functionality
- **JWT Integration**: API authentication
- **Password Validation**: Django's built-in validators

#### 4. Authentication Endpoints

```python
# Authentication URLs (authentication/urls.py)
- /                         # Home page
- /login/                   # User login
- /register/                # User registration
- /logout/                  # User logout
- /dashboard/               # User dashboard
- /profile/                 # User profile
- /activate-registration/<token>/  # Email activation
- /forgot-password/         # Password reset
- /delete-account/          # Account deletion
```

---

## AI Models & Recommendation Engine

### Movies Recommendation Models

#### 1. TF-IDF Model (`movies/ai_models/tfidf.py`)

```python
# Text-based similarity using TF-IDF vectorization
- Algorithm: Term Frequency-Inverse Document Frequency
- Input: Movie titles
- Features: Movie descriptions/content
- Output: Content-based recommendations
- Data: Sparse matrix of TF-IDF features
```

#### 2. K-Nearest Neighbors (`movies/ai_models/knn.py`)

```python
# Collaborative filtering using KNN
- Algorithm: K-Nearest Neighbors
- Input: Movie titles
- Features: User ratings and movie metadata
- Output: Similar movies based on user preferences
- Data: Sparse rating matrix
```

#### 3. Genre-Based KNN (`movies/ai_models/knn_genre.py`)

```python
# Genre-focused recommendations
- Algorithm: KNN with genre features
- Input: Movie titles
- Features: One-hot encoded genres
- Genres: ['Action', 'Adventure', 'Animation', 'Children', 'Comedy',
          'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir',
          'Horror', 'IMAX', 'Musical', 'Mystery', 'Romance',
          'Sci-Fi', 'Thriller', 'War', 'Western']
- Output: Genre-similar movies
```

#### 4. Neural Network Model (`movies/ai_models/NN.py`)

```python
# Deep learning approach
- Algorithm: Neural Network (TensorFlow/Keras)
- Input: Movie titles
- Features: 21 numerical features (ratings, popularity, etc.)
- Architecture: Multi-layer perceptron
- Output: Learned similarity patterns
```

#### 5. Embeddings Model (`movies/ai_models/Embeddings.py`)

```python
# Semantic similarity using sentence transformers
- Algorithm: Sentence-BERT embeddings
- Model: 'all-MiniLM-L6-v2'
- Input: Movie descriptions
- Features: 384-dimensional embeddings
- Similarity: Cosine similarity
- Output: Semantically similar movies
```

#### 6. Genre-Based Traditional (`movies/ai_models/Genre_Based.py`)

```python
# Traditional genre matching
- Algorithm: Cosine similarity on genre vectors
- Input: Movie titles or genre preferences
- Features: Binary genre encoding
- Output: Genre-matched recommendations
```

#### 7. GRHR Model (`movies/ai_models/GRHR.py`)

```python
# Genre-Rating Hybrid Recommendation
- Algorithm: Hybrid approach combining genres and ratings
- Input: User genre preferences
- Features: Genre weights + rating data
- Output: Personalized recommendations
```

### Books Recommendation Models

#### 1. K-Nearest Neighbors (`books/ai_models/KNN.py`)

```python
# Book similarity using KNN
- Algorithm: KNN on TF-IDF features
- Input: Book titles
- Features: Book descriptions, author, category
- Data: Sparse TF-IDF matrix
- Randomization: Top-K sampling for variety
```

#### 2. Neural Network (`books/ai_models/NN.py`)

```python
# Deep learning for books
- Algorithm: Neural Network (TensorFlow/Keras)
- Input: Book titles
- Features: Numerical book metadata
- Model: books_nn_model.keras
- Similarity: Cosine similarity on learned features
```

#### 3. Embeddings (`books/ai_models/Embeddings.py`)

```python
# Semantic book recommendations
- Algorithm: Sentence-BERT embeddings
- Model: 'all-MiniLM-L6-v2'
- Input: Book descriptions
- Features: 384-dimensional embeddings
- Fallback: Graceful degradation to dummy data
```

#### 4. TF-IDF (`books/ai_models/tfidf.py`)

```python
# Text-based book similarity
- Algorithm: TF-IDF + Nearest Neighbors
- Input: Book titles
- Features: Book content (title, description, author)
- Error Handling: Partial matching for similar titles
```

#### 5. Genre-Based (`books/ai_models/Genre_Based.py`)

```python
# Category-based book recommendations
- Algorithm: Genre/category matching
- Input: Book categories/genres
- Features: Book category metadata
- Output: Category-similar books
```

### Courses Recommendation Models

#### 1. Genre-Based (`courses/ai_models/Genre_Based.py`)

```python
# Educational content categorization
- Algorithm: Keyword-based genre classification
- Categories: 'Technology', 'Business', 'Health', 'Arts',
            'Science', 'Education', 'Language', 'Other'
- Input: Course titles or genre preferences
- Features: Course title analysis + genre matching
- Fallback: Dummy course data for development
```

#### 2. KNN Model (`courses/ai_models/KNN.py`)

```python
# Course similarity (placeholder implementation)
- Algorithm: KNN (to be implemented)
- Input: Course titles
- Status: Currently returns dummy data
```

### Model Loading & Data Management

#### Joblib Files Structure

```
Each model stores pre-trained components in joblibs/:
movies/joblibs/
├── BOW/                    # TF-IDF models
├── Embeddings/             # Sentence transformer data
├── Genre-Based/            # Genre similarity matrices
├── GenreKnn/              # Genre-based KNN
├── KNN/                   # Standard KNN models
└── NN/                    # Neural network models

books/joblibs/
├── BOW/                   # TF-IDF models
├── Embeddings/            # Book embeddings
├── Genre_knn/             # Genre KNN
├── KNN-TF/                # KNN with TF-IDF
└── NN/                    # Neural network models
```

---

## Database Models

### Authentication Models

```python
# Django's built-in User model extended with:
class UserProfile(models.Model):
    user = OneToOneField(User)
    email_verified = BooleanField(default=False)
    email_verification_sent_at = DateTimeField(null=True)
    password_reset_sent_at = DateTimeField(null=True)
    account_deletion_sent_at = DateTimeField(null=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### Movies Models

```python
class Movie(models.Model):
    movie_id = IntegerField(unique=True)
    title = CharField(max_length=255, db_index=True)
    genres = CharField(max_length=255, db_index=True)

class RecommendationHistory(models.Model):
    user = ForeignKey(User, related_name='movie_recommendation_history')
    input_title = CharField(max_length=255)
    recommended_titles = JSONField()
    model_used = CharField(max_length=100)
    timestamp = DateTimeField(auto_now_add=True)
```

### Books Models

```python
class Book(models.Model):
    book_id = IntegerField(unique=True)
    title = CharField(max_length=255, db_index=True)
    authors = CharField(max_length=255, db_index=True)
    description = TextField(blank=True, null=True)
    category = CharField(max_length=100, db_index=True)

class BookRecommendationHistory(models.Model):
    user = ForeignKey(User, related_name='book_recommendation_history')
    input_title = CharField(max_length=255)
    recommended_titles = JSONField()
    model_used = CharField(max_length=100)
    timestamp = DateTimeField(auto_now_add=True)
```

### Courses Models

```python
class Course(models.Model):
    course_id = CharField(unique=True)
    course_name = CharField(db_index=True)

class RecommendationHistory(models.Model):
    user = ForeignKey(User)
    input_title = CharField()
    recommended_titles = JSONField()
    model_used = CharField(max_length=100)
    timestamp = DateTimeField(auto_now_add=True)
```

---

## API Endpoints

### Authentication Endpoints

```python
# Base authentication URLs
GET  /                                     # Home page
POST /login/                              # User login
POST /register/                           # User registration
POST /logout/                             # User logout
GET  /dashboard/                          # User dashboard
GET  /activate-registration/<token>/      # Email verification
POST /forgot-password/                    # Password reset
POST /delete-account/                     # Account deletion
```

### Movies API

```python
# Movie recommendation endpoints
GET  /movies/                             # Movie recommendation page
GET  /genre-movies/                       # Genre-based page
GET  /history/                           # History page

# API endpoints
GET  /api/movies/search/                  # Search movies
POST /api/movies/recommend/               # Get recommendations
POST /api/movies/recommend-genre/         # Genre-based recommendations
POST /api/movies/save-selected/           # Save selected recommendations
GET  /api/movies/history/                 # Get recommendation history
POST /api/movies/history/delete-single/  # Delete single history entry
POST /api/movies/history/delete-bulk/    # Bulk delete history
```

### Books API

```python
# Book recommendation endpoints
GET  /books/                              # Book recommendation page
GET  /books/history/                      # History page
GET  /books/genre/                        # Genre-based page

# API endpoints
GET  /books/api/search/                   # Search books
POST /books/api/recommend/                # Get recommendations
POST /books/api/save-recommendations/     # Save selected recommendations
GET  /books/api/history/                  # Get recommendation history
POST /books/api/history/delete-single/   # Delete single history entry
POST /books/api/history/delete-bulk/     # Bulk delete history
POST /books/api/genre-recommendations/   # Genre-based recommendations
```

### Courses API

```python
# Course recommendation endpoints
GET  /courses/courses/                    # Course recommendation page
GET  /courses/history/                    # History page

# API endpoints
GET  /courses/api/courses/search/         # Search courses
POST /courses/api/courses/recommend/      # Get recommendations
POST /courses/api/courses/recommend-genre/ # Genre-based recommendations
POST /courses/api/courses/save-selected/ # Save selected recommendations
GET  /courses/api/courses/history/        # Get recommendation history
POST /courses/api/courses/history/delete-single/ # Delete single history
POST /courses/api/courses/history/delete-bulk/   # Bulk delete history
```

### API Request/Response Formats

#### Movie Recommendation Request

```json
{
  "movie_title": "The Matrix",
  "num_recommendations": 5,
  "model_used": "Embeddings",
  "save_history": true,
  "regenerate": false
}
```

#### Movie Recommendation Response

```json
{
  "recommendations": {
    "The Matrix": [
      "Blade Runner",
      "Ghost in the Shell",
      "Minority Report",
      "Ex Machina",
      "I, Robot"
    ]
  },
  "saved_history": true,
  "regenerated": false,
  "input_movie": "The Matrix"
}
```

---

## Services & External Dependencies

### Email Service

```python
# SMTP Configuration (settings.py)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

# Email Templates
- Registration activation emails
- Welcome confirmation emails
- Password reset emails
- Account deletion confirmations
```

### Machine Learning Dependencies

```python
# Core ML Libraries
- tensorflow==2.19.0              # Neural networks
- scikit-learn==1.6.1             # Traditional ML algorithms
- sentence-transformers==4.1.0    # Text embeddings
- torch==2.7.0                    # PyTorch backend
- transformers==4.52.4            # Transformer models

# Data Processing
- numpy==2.1.3                    # Numerical computations
- pandas==2.2.3                   # Data manipulation
- joblib==1.5.1                   # Model serialization

# Similarity Calculations
- cosine_similarity from sklearn  # Vector similarity
- pytorch_cos_sim from sentence_transformers
```

### Web Framework Dependencies

```python
# Django Stack
- Django==5.2.1                   # Core framework
- djangorestframework==3.16.0     # REST API
- django-cors-headers==4.7.0      # CORS handling
- djangorestframework_simplejwt==5.5.0  # JWT authentication

# Utilities
- python-decouple==3.8            # Environment variables
- gunicorn==22.0.0                # WSGI server
```

---

## Frontend Implementation

### Template Structure

```python
# Django Templates Organization
authentication/templates/
├── authen/                       # Authentication forms
│   ├── login.html
│   ├── register.html
│   └── password_reset.html
├── core/                         # Core pages
│   ├── landing.html              # Home page
│   ├── dashboard.html            # User dashboard
│   └── about.html
└── emails/                       # Email templates

movies/templates/movies/
├── movies.html                   # Movie recommendations
├── movies_history.html           # History page
└── genre_movies.html             # Genre-based page

books/templates/books/
├── books.html                    # Book recommendations
├── books_history.html            # History page
└── genre_books.html              # Genre-based page

courses/templates/courses/
├── courses.html                  # Course recommendations
├── courses_history.html          # History page
└── genre_courses.html            # Genre-based page
```

### JavaScript Features

```javascript
// Core Frontend Functionality
- AJAX-based search with autocomplete
- Real-time recommendation requests
- Dynamic UI updates without page reload
- Recommendation history management
- Model selection and parameter tuning
- Error handling and user feedback
- Responsive design elements

// Key JavaScript Libraries Used
- jQuery for DOM manipulation
- Bootstrap for responsive components
- Custom AJAX handling for API calls
```

### UI Components

```html
<!-- Search Interface -->
- Autocomplete search inputs - Model selection dropdowns - Number of
recommendations slider - Advanced filtering options

<!-- Results Display -->
- Card-based recommendation layout - Pagination for large result sets -
Save/bookmark functionality - Regenerate recommendations button

<!-- History Management -->
- Sortable recommendation history - Filter by model type - Bulk actions (delete,
export) - Statistics dashboard
```

---

## Deployment & Infrastructure

### Docker Configuration

#### Dockerfile

```dockerfile
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

EXPOSE 8000

# Production command
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "OPC.wsgi:application"]
```


```

### Environment Configuration

```python
# Environment Variables (.env)
SECRET_KEY=                       # Django secret key
DEBUG=False                       # Debug mode
ALLOWED_HOSTS=                    # Allowed hosts

# Database
DB_ENGINE=                        # Database engine
DB_NAME=                          # Database name
DB_USER=                          # Database user
DB_PASSWORD=                      # Database password
DB_HOST=                          # Database host
DB_PORT=                          # Database port

# Email Configuration
EMAIL_HOST_USER=                  # Gmail address
EMAIL_HOST_PASSWORD=              # Gmail app password

# JWT Configuration
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=1

# CORS Configuration
CORS_ALLOWED_ORIGINS=             # Frontend URLs
```

---

## Security Features

### Authentication Security

```python
# Email Verification
- Required before account activation
- Secure token generation using UUID

# Password Security
- Django's built-in password validation
- Minimum length requirements
- Common password checking
- User attribute similarity validation

# Session Management
- Configurable session timeouts
- Remember me functionality
- Secure session cookies
- CSRF protection on all forms
```

### API Security

```python
# JWT Authentication
- Access tokens (60 minutes default)
- Refresh tokens (1 day default)
- Token rotation on refresh
- Blacklisting after rotation

# CORS Configuration
- Restricted allowed origins
- Credential support
- Specific allowed headers and methods

# Input Validation
- Serializer-based validation
- Type checking and constraints
- SQL injection prevention
- XSS protection
```

### Data Protection

```python
# Database Security
- Indexed sensitive fields
- Foreign key constraints
- Soft delete for user data
- Audit trails for recommendations

# Privacy Features
- User can delete recommendation history
- Account deletion with confirmation
- Email verification for sensitive actions
- No storage of raw passwords
```

---

## Configuration Management

### Settings Architecture

```python
# Environment-based configuration
- Development settings (DEBUG=True)
- Production settings (DEBUG=False)
- Environment variable loading
- Fallback defaults for all configurations

# Database Configuration
- SQLite for development
- PostgreSQL for production
- Connection pooling
- Migration management

# Static Files
- Development: Django serves static files
- Production: Nginx serves static files
- Collectstatic for deployment
- CDN integration ready
```

### Feature Flags

```python
# Model Availability
- Graceful degradation when ML models unavailable
- Dummy data fallbacks for development
- Error handling for missing dependencies
- Configurable model selection

# Email Settings
- Optional email functionality
- Fallback to console backend
- Configurable timeout and retry logic
```

---

## Development & Testing

### Development Setup

```bash
# Local Development
1. Clone repository
2. Create virtual environment
3. Install dependencies: pip install -r requirements.txt
4. Set up environment variables
5. Run migrations: python manage.py migrate
6. Create superuser: python manage.py createsuperuser
7. Start server: python manage.py runserver
```

### Code Structure & Best Practices

```python
# Django Best Practices
- Apps organized by domain (movies, books, courses)
- Model-View-Serializer pattern for APIs
- Custom managers for complex queries
- Proper error handling and logging
- Environment-based configuration

# AI Model Integration
- Modular model loading
- Error handling for missing models
- Consistent interface across all models
- Randomization for recommendation variety
- Caching of expensive computations
```

### Testing Strategy

```python
# Test Coverage Areas
- Unit tests for models
- API endpoint testing
- Authentication flow testing
- AI model integration tests
- Frontend form validation
- Email functionality testing

# Test Command
python manage.py test
```

### Model Development Workflow

```python
# Adding New AI Models
1. Create model file in app/ai_models/
2. Implement standard recommendation function
3. Add model choice to serializers
4. Update view to handle new model
5. Add frontend model selection option
6. Test with sample data
7. Deploy trained model artifacts
```

---

## Performance Considerations

### Database Optimization

```python
# Indexing Strategy
- Database indexes on frequently queried fields
- title fields indexed for search
- Foreign keys optimized
- Composite indexes for complex queries

# Query Optimization
- Select_related for foreign keys
- Prefetch_related for reverse foreign keys
- Pagination for large datasets
- Efficient JSON field usage
```

### AI Model Performance

```python
# Model Loading Strategy
- Lazy loading of ML models
- Cached model instances
- Error handling for model failures
- Fallback to dummy data

# Recommendation Caching
- Session-based caching for recent requests
- Model-specific cache keys
- Regeneration capabilities
- History-based optimizations
```

### Scalability Features

```python
# Horizontal Scaling Ready
- Stateless application design
- Database-backed sessions
- External file storage support
- Load balancer friendly

# Resource Management
- Configurable recommendation limits
- Memory-efficient model loading
- Graceful degradation under load
- Health check endpoints
```

---

## Monitoring & Maintenance

### Logging Strategy

```python
# Application Logging
- Authentication events
- Recommendation requests
- Error tracking
- Performance metrics

# Security Monitoring
- Failed login attempts
- Suspicious API usage
- Email delivery failures
- Token expiration events
```

### Health Checks

```bash
# Available Health Monitoring
- health-check.sh script
- Database connectivity checks
- Email service verification
- ML model availability
- Static file serving
```

### Backup & Recovery

```python
# Data Backup Strategy
- Database backups
- User-generated content
- Model artifacts
- Configuration files

# Recovery Procedures
- Database restoration
- Model redeployment
- Configuration restoration
- Email service recovery
```

---

## Future Enhancements

### Planned Features

```python

# User Experience
- Mobile application
- Social features (sharing, reviews)
- Personalization improvements
- Multi-language support

# Technical Improvements
- Real-time notifications
```

### Integration Opportunities

```python
# External APIs
- Movie databases (TMDB, OMDB)
- Book catalogs (Google Books, GoodReads)
- Course platforms (Coursera)
- Social media integration

```

---

This comprehensive documentation covers all aspects of the OptiChoice recommendation system, from authentication and AI models to deployment and security. The system is designed to be maintainable, scalable, and secure while providing powerful recommendation capabilities across multiple domains.

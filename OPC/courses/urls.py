from django.urls import path
from . import views

urlpatterns = [
    # Course recommendation pages - now using genre-based as default
    path('courses/', views.genre_recommendation_page, name='course_recommendation_page'),
    path('genre-courses/', views.genre_recommendation_page, name='course_genre_recommendation_page'),
    path('history/', views.recommendation_history_page, name='course_recommendation_history_page'),
    # API endpoints
    path('api/courses/search/', views.CourseSearchView.as_view(), name='course_search'),
    path('api/courses/recommend/', views.CourseRecommendation_1.as_view(), name='course_recommend'),
    path('api/courses/recommend-genre/', views.CourseRecommendation_2.as_view(), name='course_recommend_genre'),
    path('api/courses/genre-recommend/', views.CourseGenreBasedRecommendationView.as_view(), name='course_genre_recommend'),
    path('api/courses/save-selected/', views.SaveSelectedCourseRecommendations.as_view(), name='save_selected_recommendations'),
    path('api/courses/history/', views.CourseHistoryView.as_view(), name='course_history'),
    path('api/courses/history/delete-single/', views.CourseHistorySingleClearView.as_view(), name='delete_single_history'),
    path('api/courses/history/delete-bulk/', views.CourseHistoryBulkClearView.as_view(), name='delete_bulk_history'),
]

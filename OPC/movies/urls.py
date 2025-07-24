from django.urls import path
from . import views

urlpatterns = [
    # Movie recommendation pages
    path('movies/', views.movie_recommendation_page, name='movie_recommendation_page'),
    path('genre-movies/', views.genre_recommendation_page, name='movie_genre_recommendation_page'),
    path('history/', views.recommendation_history_page, name='movie_recommendation_history_page'),
      # API endpoints
    path('api/movies/search/', views.MovieSearchView.as_view(), name='movie_search'),
    path('api/movies/recommend/', views.MovieRecommendation_1.as_view(), name='movie_recommend'),
    path('api/movies/recommend-genre/', views.MovieRecommendation_2.as_view(), name='movie_recommend_genre'),
    path('api/movies/save-selected/', views.SaveSelectedRecommendations.as_view(), name='save_selected_recommendations'),
    path('api/movies/history/', views.MovieHistoryView.as_view(), name='movie_history'),
    path('api/movies/history/delete-single/', views.MovieHistorySingleClearView.as_view(), name='delete_single_history'),
    path('api/movies/history/delete-bulk/', views.MovieHistoryBulkClearView.as_view(), name='delete_bulk_history'),
]
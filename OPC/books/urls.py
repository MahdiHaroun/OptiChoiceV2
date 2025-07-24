from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    # Template views
    path('', views.book_recommendation_page, name='book_recommendation_page'),
    path('history/', views.book_history_page, name='book_history_page'),
    path('genre/', views.genre_books_page, name='genre_books_page'),   
     
    # API endpoints
    path('api/search/', views.BookSearchView.as_view(), name='book_search'),
    path('api/recommend/', views.BookRecommendationView.as_view(), name='book_recommendation'),
    path('api/save-recommendations/', views.SaveSelectedRecommendations.as_view(), name='save_recommendations'),
    path('api/history/', views.BookHistoryView.as_view(), name='book_history'),
    path('api/history/delete-single/', views.BookHistoryDeleteView.as_view(), name='book_history_delete_single'),
    path('api/history/delete-bulk/', views.BookHistoryBulkClearView.as_view(), name='book_history_bulk_delete'),
    path('api/genre-recommendations/', views.GenreBasedRecommendationView.as_view(), name='genre_recommendations'),
]

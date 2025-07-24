from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import models
from rest_framework.permissions import IsAuthenticated 
from rest_framework import filters

from .serializers import BookRecommendationRequestSerializer, BookRecommendationHistorySerializer, BookSerializer, BookRecommendationUserGenreSerializer
from .models import Book, BookRecommendationHistory 
from .ai_models.Embeddings import recommend_books_embeddings
from .ai_models.KNN import recommend_books_knn
from .ai_models.NN import recommend_books_nn
from .ai_models.Genre_Based import recommend_books_by_genre_selection


class CustomLimitOffsetPagination(LimitOffsetPagination):
    """
    Custom offset pagination for search results with enhanced response format
    """
    default_limit = 5
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 50
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': (self.count + self.limit - 1) // self.limit if self.limit else 1,
            'current_page': (self.offset // self.limit) + 1 if self.limit else 1,
            'page_size': self.limit,
            'has_next': self.get_next_link() is not None,
            'has_previous': self.get_previous_link() is not None,
            'results': data
        })
    

class BookSearchView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookSerializer
    pagination_class = CustomLimitOffsetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'authors']
    
    def get_queryset(self):
        queryset = Book.objects.all()
        queryset = queryset.order_by('title')  
        return queryset
    

class BookRecommendationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = BookRecommendationRequestSerializer(data=request.data)
        if serializer.is_valid():
            book_title = serializer.validated_data['book_title']
            num_recommendations = serializer.validated_data['num_recommendations']
            model_used = serializer.validated_data['model_used']
            save_history = serializer.validated_data.get('save_history', False)
            regenerate = serializer.validated_data.get('regenerate', False)
        
            book_titles = [book_title]
        
            if model_used == 'Embeddings':
                results = recommend_books_embeddings(book_titles, num_recommendations)
            elif model_used == 'knn':
                results = recommend_books_knn(book_titles, num_recommendations)
            elif model_used == 'NN':
                results = recommend_books_nn(book_titles, num_recommendations)


            else:
                return Response(
                    {"error": f"Model '{model_used}' is not supported."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if save_history:
                for input_title, recommended in results.items():
                    if isinstance(recommended, list):
                        BookRecommendationHistory.objects.create(
                            user=request.user if request.user.is_authenticated else None,
                            input_title=input_title,
                            recommended_titles=recommended,
                            model_used=model_used
                        )

            return Response({
                "recommendations": results,
                "saved_history": save_history,
                "regenerated": regenerate,
                "input_book": book_title  # Include the single input book for frontend
            }, status=status.HTTP_200_OK)
    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        

class SaveSelectedRecommendations(APIView):
    def post(self, request):
        input_title = request.data.get('input_title')
        selected_recommendations = request.data.get('selected_recommendations', {})
        model_used = request.data.get('model_used', 'unknown')
        
        if not selected_recommendations:
            return Response({'error': 'No recommendations provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            for input_title, recommended_titles in selected_recommendations.items():
                BookRecommendationHistory.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    input_title=input_title, 
                    recommended_titles=recommended_titles,  # Store the list of strings directly
                    model_used=model_used
                )

            return Response({'status': 'Saved successfully.'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


# Template views
@login_required
def book_recommendation_page(request):
    """Main book recommendation page"""
    return render(request, 'books/books.html')

@login_required 
def book_history_page(request):
    """Book recommendation history page"""
    return render(request, 'books/books_history.html')

@login_required
def genre_books_page(request):
    """Genre-based book recommendations page"""
    return render(request, 'books/genre_books.html')

# API views



class BookHistoryDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """Delete a single recommendation history entry"""
        try:
            history_id = request.data.get('history_id')
            
            if not history_id:
                return Response({'error': 'History ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the history entry for the authenticated user
            history_entry = BookRecommendationHistory.objects.get(
                id=history_id,
                user=request.user
            )
            
            # Delete the entry
            history_entry.delete()
            
            return Response({'status': 'History entry deleted successfully.'}, status=status.HTTP_200_OK)
            
        except BookRecommendationHistory.DoesNotExist:
            return Response({'error': 'History entry not found.'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({'error': 'Invalid history ID format.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class BookHistoryBulkClearView(generics.DestroyAPIView):
    queryset = BookRecommendationHistory.objects.all()
    serializer_class = BookRecommendationHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, *args, **kwargs):
        """Delete all recommendation history entries for the authenticated user"""
        try:
            # Filter by user and delete all entries
            deleted_count, _ = BookRecommendationHistory.objects.filter(user=request.user).delete()
            return Response({
                'status': 'All history entries deleted successfully.',
                'deleted_count': deleted_count
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       


class BookHistoryView(generics.ListAPIView):
    serializer_class = BookRecommendationHistorySerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['input_title', 'model_used']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']  

    def get_queryset(self):
        """Return history entries for the authenticated user only"""
        return BookRecommendationHistory.objects.filter(user=self.request.user)
    

class GenreBasedRecommendationView(APIView):
    def post(self, request):
        serializer = BookRecommendationUserGenreSerializer(data=request.data)
        if serializer.is_valid():
            book_genres = serializer.validated_data['book_genres']
            num_recommendations = serializer.validated_data['num_recommendations']
            model_used = serializer.validated_data['model_used']
            regenerate = serializer.validated_data.get('regenerate', False)

            if model_used == 'Genre-Based':
                results = recommend_books_by_genre_selection(book_genres, num_recommendations)
                
                # Check if Genre-Based returned an error
                if isinstance(results, dict) and 'error' in results:
                    return Response({
                        "error": results['error']
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            elif model_used == 'knn_genre':
                return Response(
                    {"error": "Model 'knn_genre' is not implemented yet."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {"error": f"Model '{model_used}' is not supported."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response({
                "recommendations": results,
                "regenerated": regenerate
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
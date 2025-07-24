from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import  status
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import models


from .serializers import MovieRecommendationRequestSerializer, MovieRecommendationUserRatingSerializer , RecommendationHistorySerializer, MovieSerializer
from .models import RecommendationHistory 
from .ai_models.knn import recommend_movies_knn
from .ai_models.tfidf import recommend_movies_sparse_list
from .ai_models.Genre_Based import recommend_movies_by_genre
from .ai_models.GRHR import recommend_movies_GRHR
from .ai_models.knn_genre import recommend_movies_by_knn_genre
from .ai_models.Embeddings import recommend_movies_embeddings
from .ai_models.NN import recommend_movies_nn

from movies.models import Movie

from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination


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
    





class MovieSearchView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'genres']
    pagination_class = CustomLimitOffsetPagination
    
    def get_queryset(self):
        """
        Optimize the queryset for better performance with offset pagination
        """
        queryset = Movie.objects.all()
        
        # Add consistent ordering for pagination
        queryset = queryset.order_by('id')
        
        return queryset
    




class MovieRecommendation_1(APIView):
    def post(self, request):
        serializer = MovieRecommendationRequestSerializer(data=request.data)
        if serializer.is_valid():
            movie_title = serializer.validated_data['movie_title']
            num_recommendations = serializer.validated_data['num_recommendations']
            model_used = serializer.validated_data['model_used']
            save_history = serializer.validated_data.get('save_history', False)  # default True
            regenerate = serializer.validated_data.get('regenerate', False)    # default False

            # Convert single movie title to list for compatibility with existing AI models
            movie_titles = [movie_title]

            if model_used == 'tfidf':
                results = recommend_movies_sparse_list(movie_titles, num_recommendations)
            elif model_used == 'Genre-Based':
                results = recommend_movies_by_genre(movie_titles, num_recommendations)
            elif model_used == 'knn':
                results = recommend_movies_knn(movie_titles, num_recommendations)
            elif model_used == 'knn_genre':
                results = recommend_movies_by_knn_genre(movie_titles, num_recommendations)
            elif model_used == 'Embeddings':
                results = recommend_movies_embeddings(movie_titles, num_recommendations)
            elif model_used == 'NN':
                results = recommend_movies_nn(movie_titles, num_recommendations)
            else:
                return Response(
                    {"error": f"Model '{model_used}' is not supported."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if save_history:
                for input_title, recommended in results.items():
                    if isinstance(recommended, list):
                        RecommendationHistory.objects.create(
                            user=request.user if request.user.is_authenticated else None,
                            input_title=input_title,
                            recommended_titles=recommended,
                            model_used=model_used
                        )

            return Response({
                "recommendations": results,
                "saved_history": save_history,
                "regenerated": regenerate,
                "input_movie": movie_title  # Include the single input movie for frontend
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    






class MovieRecommendation_2(APIView):
    def post(self, request):
        serializer = MovieRecommendationUserRatingSerializer(data=request.data)
        if serializer.is_valid():
            movie_genres = serializer.validated_data['movie_genres']
            num_recommendations = serializer.validated_data['num_recommendations']
            model_used = serializer.validated_data['model_used']
            save_history = serializer.validated_data.get('save_history', False)
            regenerate = serializer.validated_data.get('regenerate', False)

            if model_used == 'GRHR':
                results = recommend_movies_GRHR(movie_genres, num_recommendations)
                
                # Check if GRHR returned an error
                if isinstance(results, dict) and 'error' in results:
                    return Response({
                        "error": results['error']
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            elif model_used == 'GRNR':
                return Response(
                    {"error": "Model 'GRNR' is not implemented yet."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {"error": f"Model '{model_used}' is not supported."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if save_history and isinstance(results, list):
                RecommendationHistory.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    input_title=", ".join(movie_genres),
                    recommended_titles=results,
                    model_used=model_used
                )

            return Response({
                "recommendations": results,
                "saved_history": save_history,
                "regenerated": regenerate
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
                RecommendationHistory.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    input_title= input_title, 
                    recommended_titles=recommended_titles,  # Assuming this is a JSONField or TextField
                    model_used=model_used
                )

            return Response({'status': 'Saved successfully.'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        





class MovieHistoryView(generics.ListAPIView):
    serializer_class = RecommendationHistorySerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['input_title', 'model_used']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']  

    def get_queryset(self):
        """Return history entries for the authenticated user only"""
        return RecommendationHistory.objects.filter(user=self.request.user)



class MovieHistorySingleClearView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """Delete a single recommendation history entry"""
        try:
            history_id = request.data.get('history_id')
            
            if not history_id:
                return Response({'error': 'History ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the history entry for the authenticated user
            history_entry = RecommendationHistory.objects.get(
                id=history_id,
                user=request.user
            )
            
            # Delete the entry
            history_entry.delete()
            
            return Response({'status': 'History entry deleted successfully.'}, status=status.HTTP_200_OK)
            
        except RecommendationHistory.DoesNotExist:
            return Response({'error': 'History entry not found.'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({'error': 'Invalid history ID format.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MovieHistoryBulkClearView(generics.DestroyAPIView):
    queryset = RecommendationHistory.objects.all()
    serializer_class = RecommendationHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, *args, **kwargs):
        """Delete all recommendation history entries for the authenticated user"""
        try:
            # Filter by user and delete all entries
            deleted_count, _ = RecommendationHistory.objects.filter(user=request.user).delete()
            return Response({
                'status': 'All history entries deleted successfully.',
                'deleted_count': deleted_count
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       
    
@login_required
def movie_recommendation_page(request):
    """Render the movie recommendation page"""
    return render(request, 'movies/movies.html')

@login_required
def genre_recommendation_page(request):
    """Render the genre-based movie recommendation page"""
    return render(request, 'movies/genre_movies.html')

@login_required
def recommendation_history_page(request):
    """Render the recommendation history page"""
    return render(request, 'movies/movies_history.html')
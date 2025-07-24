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



from .serializers import CourseRecommendationRequestSerializer, CourseRecommendationUserRatingSerializer , RecommendationHistorySerializer, CourseSerializer, CourseRecommendationUserGenreSerializer
from .models import RecommendationHistory, Course
# from .ai_models.knn import recommend_courses_knn
# from .ai_models.tfidf import recommend_courses_sparse_list
from .ai_models.Genre_Based import recommend_courses_by_genre
# from .ai_models.GRHR import recommend_courses_GRHR
# from .ai_models.knn_genre import recommend_courses_by_knn_genre
# from .ai_models.Embeddings import recommend_courses_embeddings
# from .ai_models.NN import recommend_courses_nn

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
    


class CourseSearchView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['course_name']
    pagination_class = CustomLimitOffsetPagination
    
    def get_queryset(self):
        """
        Optimize the queryset for better performance with offset pagination
        """
        queryset = Course.objects.all()
        
        # Add consistent ordering for pagination
        queryset = queryset.order_by('id')
        
        return queryset


class CourseRecommendation_1(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = CourseRecommendationRequestSerializer(data=request.data)
        if serializer.is_valid():
            course_title = serializer.validated_data['course_title']
            num_recommendations = serializer.validated_data['num_recommendations']
            model_used = serializer.validated_data['model_used']
            save_history = serializer.validated_data.get('save_history', False)  # default True
            regenerate = serializer.validated_data.get('regenerate', False)    # default False

            # Convert single course title to list for compatibility with existing AI models
            course_titles = [course_title]

            # TODO: Replace with actual AI model implementations when available
            # For now, return dummy data for all models
            if model_used == 'tfidf':
                # results = recommend_courses_sparse_list(course_titles, num_recommendations)
                results = {course_title: [f"Course {i} (TF-IDF)" for i in range(1, num_recommendations + 1)]}
            elif model_used == 'Genre-Based':
                # results = recommend_courses_by_genre(course_titles, num_recommendations)
                results = {course_title: [f"Course {i} (Genre-Based)" for i in range(1, num_recommendations + 1)]}
            elif model_used == 'knn':
                # results = recommend_courses_knn(course_titles, num_recommendations)
                results = {course_title: [f"Course {i} (KNN)" for i in range(1, num_recommendations + 1)]}
            elif model_used == 'knn_genre':
                # results = recommend_courses_by_knn_genre(course_titles, num_recommendations)
                results = {course_title: [f"Course {i} (KNN Genre)" for i in range(1, num_recommendations + 1)]}
            elif model_used == 'Embeddings':
                # results = recommend_courses_embeddings(course_titles, num_recommendations)
                results = {course_title: [f"Course {i} (Embeddings)" for i in range(1, num_recommendations + 1)]}
            elif model_used == 'NN':
                # results = recommend_courses_nn(course_titles, num_recommendations)
                results = {course_title: [f"Course {i} (Neural Network)" for i in range(1, num_recommendations + 1)]}
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
                "input_course": course_title  # Include the single input course for frontend
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseRecommendation_2(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = CourseRecommendationUserRatingSerializer(data=request.data)
        if serializer.is_valid():
            course_genres = serializer.validated_data['course_genres']
            num_recommendations = serializer.validated_data['num_recommendations']
            model_used = serializer.validated_data['model_used']
            save_history = serializer.validated_data.get('save_history', False)
            regenerate = serializer.validated_data.get('regenerate', False)

            # Use actual AI model for Genre-Based recommendations
            if model_used == 'Genre-Based':
                results = recommend_courses_by_genre(course_genres, num_recommendations)
            elif model_used == 'GRHR':
                # results = recommend_courses_GRHR(course_genres, num_recommendations)
                results = [f"Course {i} (GRHR - {', '.join(course_genres)})" for i in range(1, num_recommendations + 1)]
                    
            elif model_used == 'GRNR':
                # results = recommend_courses_GRNR(course_genres, num_recommendations)
                results = [f"Course {i} (GRNR - {', '.join(course_genres)})" for i in range(1, num_recommendations + 1)]
            else:
                return Response(
                    {"error": f"Model '{model_used}' is not supported."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if save_history and isinstance(results, list):
                RecommendationHistory.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    input_title=", ".join(course_genres),
                    recommended_titles=results,
                    model_used=model_used
                )

            return Response({
                "recommendations": results,
                "saved_history": save_history,
                "regenerated": regenerate
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SaveSelectedCourseRecommendations(APIView):
    permission_classes = [IsAuthenticated]
    
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


class CourseHistoryView(generics.ListAPIView):
    serializer_class = RecommendationHistorySerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['input_title', 'model_used']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']  

    def get_queryset(self):
        """Return history entries for the authenticated user only"""
        return RecommendationHistory.objects.filter(user=self.request.user)


class CourseHistorySingleClearView(APIView):
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


class CourseHistoryBulkClearView(generics.DestroyAPIView):
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


class CourseGenreBasedRecommendationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = CourseRecommendationUserGenreSerializer(data=request.data)
        if serializer.is_valid():
            course_genres = serializer.validated_data['course_genres']
            num_recommendations = serializer.validated_data['num_recommendations']
            model_used = serializer.validated_data['model_used']
            save_history = serializer.validated_data.get('save_history', False)
            regenerate = serializer.validated_data.get('regenerate', False)

            if model_used == 'Genre-Based':
                # Use the actual AI model
                results = recommend_courses_by_genre(course_genres, num_recommendations)
                    
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

            if save_history and isinstance(results, list):
                RecommendationHistory.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    input_title=f"Genre-based: {', '.join(course_genres)}",
                    recommended_titles=results,
                    model_used=model_used
                )

            return Response({
                "recommendations": results,
                "saved_history": save_history,
                "regenerated": regenerate,
                "selected_genres": course_genres
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@login_required
def genre_recommendation_page(request):
    """Render the genre-based course recommendation page"""
    return render(request, 'courses/genre_courses.html')

@login_required
def recommendation_history_page(request):
    """Render the recommendation history page"""
    return render(request, 'courses/courses_history.html')


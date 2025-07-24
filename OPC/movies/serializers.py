from movies.models import Movie, RecommendationHistory 
from rest_framework import serializers


class MovieRecommendationRequestSerializer(serializers.Serializer):
    Model_Choices = [
        ('tfidf', 'tfidf'),
        ('Genre-Based', 'Genre-Based'),
        ('knn', 'knn'),
        ('knn_genre', 'knn_genre'),
        ('Embeddings', 'Embeddings'),
        ('NN', 'NN'),
    ]
    movie_title = serializers.CharField(
        help_text="Single input movie title"
    )
    num_recommendations = serializers.IntegerField(
        min_value=1,
        default=5,
        help_text="Number of recommendations to return"
    )
    model_used = serializers.ChoiceField(
        choices=Model_Choices,
        required=True,
        help_text="Recommendation model to use"
    )
    save_history = serializers.BooleanField(
        required=False,
        default=True,
        help_text="Whether to save this recommendation to history"
    )
    
    regenerate = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Whether this request is a regeneration"
        )
    
class MovieRecommendationUserRatingSerializer(serializers.Serializer):
    Model_Choices = [
            ('GRHR', 'GRHR'),
            ('GRNR', 'GRNR'), 
        ]
    movie_genres = serializers.ListField(
            child=serializers.CharField(),
            allow_empty=False,
            help_text="List of input movie genres"
        )
    num_recommendations = serializers.IntegerField(
            min_value=1,
            default=5,
            help_text="Number of recommendations to return"
        )
    model_used = serializers.ChoiceField(
            choices=Model_Choices,
            required=True,
            help_text="Recommendation model to use"
        )
    save_history = serializers.BooleanField(
            required=False,
            default=True,
            help_text="Whether to save this recommendation to history"
        )
    regenerate = serializers.BooleanField(
            required=False,
            default=False,
            help_text="Whether this request is a regeneration"
        )


class RecommendationHistorySerializer(serializers.ModelSerializer): 
    class Meta: 
        model = RecommendationHistory
        fields = ['id', 'user', 'input_title', 'recommended_titles', 'model_used', 'timestamp']
        


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['movie_id', 'title', 'genres']




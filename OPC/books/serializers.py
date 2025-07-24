from books.models import Book , BookRecommendationHistory 
from rest_framework import serializers 




class BookRecommendationRequestSerializer(serializers.Serializer): 
    Model_Choices = [
        ('Genre-Based', 'Genre-Based'),
        ('knn', 'knn'),
        ('knn_genre', 'knn_genre'),
        ('Embeddings', 'Embeddings'),
        ('NN', 'NN'),
    ]
    book_title = serializers.CharField(
        help_text="Single input book title"
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



class BookRecommendationHistorySerializer(serializers.ModelSerializer): 
    class Meta: 
        model = BookRecommendationHistory
        fields = ['id', 'user', 'input_title', 'recommended_titles', 'model_used', 'timestamp']
        


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['book_id', 'title', 'authors', 'description', 'category']


class BookRecommendationUserGenreSerializer(serializers.Serializer):
    Model_Choices = [
            ('Genre-Based', 'Genre-Based'),
            
        ]
    book_genres = serializers.ListField(
            child=serializers.CharField(),
            allow_empty=False,
            help_text="List of input book genres"
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
    regenerate = serializers.BooleanField(
            required=False,
            default=False,
            help_text="Whether this request is a regeneration"
        )

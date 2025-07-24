from courses.models import Course, RecommendationHistory
from rest_framework import serializers


class CourseRecommendationRequestSerializer(serializers.Serializer):
    Model_Choices = [
        ('tfidf', 'tfidf'),
        ('Genre-Based', 'Genre-Based'),
        ('knn', 'knn'),
        ('knn_genre', 'knn_genre'),
        ('Embeddings', 'Embeddings'),
        ('NN', 'NN'),
    ]
    course_title = serializers.CharField(
        help_text="Single input course title"
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
    
class CourseRecommendationUserRatingSerializer(serializers.Serializer):
    Model_Choices = [
            ('GRHR', 'GRHR'),
            ('GRNR', 'GRNR'), 
        ]
    course_genres = serializers.ListField(
            child=serializers.CharField(),
            allow_empty=False,
            help_text="List of input course genres"
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
    input_course = serializers.SerializerMethodField()
    input_courses = serializers.SerializerMethodField()
    course_genres = serializers.SerializerMethodField()
    
    class Meta: 
        model = RecommendationHistory
        fields = ['id', 'user', 'input_title', 'input_course', 'input_courses', 'course_genres', 'recommended_titles', 'model_used', 'timestamp']
    
    def get_input_course(self, obj):
        """Return single course input if applicable"""
        if obj.model_used in ['Embeddings', 'KNN', 'Neural Network'] and not obj.input_title.startswith('Genre-based:'):
            return obj.input_title
        return None
    
    def get_input_courses(self, obj):
        """Return multiple courses input if applicable"""
        if ',' in obj.input_title and not obj.input_title.startswith('Genre-based:'):
            return [course.strip() for course in obj.input_title.split(',')]
        return None
    
    def get_course_genres(self, obj):
        """Return genres if this is a genre-based recommendation"""
        if obj.input_title.startswith('Genre-based:') or obj.model_used == 'Genre-Based':
            # Remove 'Genre-based:' prefix if present and split by comma
            genres_str = obj.input_title.replace('Genre-based:', '').strip()
            return [genre.strip() for genre in genres_str.split(',')]
        return None
        

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['course_id', 'course_name']


class CourseRecommendationUserGenreSerializer(serializers.Serializer):
    Model_Choices = [
        ('Genre-Based', 'Genre-Based'),
    ]
    course_genres = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of genres to filter courses by"
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
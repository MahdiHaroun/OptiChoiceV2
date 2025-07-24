from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Movie(models.Model):
    movie_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255, db_index=True)
    genres = models.CharField(max_length=255, db_index=True)  

    def __str__(self):
        return self.title


class RecommendationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='movie_recommendation_history')
    input_title = models.CharField(max_length=255)
    recommended_titles = models.JSONField()
    model_used = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} | {self.input_title} -> {len(self.recommended_titles)} recs"

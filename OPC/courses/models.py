from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Course(models.Model):

    course_id = models.CharField(unique=True)
    course_name = models.CharField(db_index=True)


    def __str__(self):
        return self.course_name


class RecommendationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True )
    input_title = models.CharField()
    recommended_titles = models.JSONField()
    model_used = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} | {self.input_title} -> {len(self.recommended_titles)} recs"

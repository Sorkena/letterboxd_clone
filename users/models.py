from django.db import models
from django.contrib.auth.models import User
from movies.models import Movie

class Watchlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='watchlist')
    movies = models.ManyToManyField(Movie, related_name='watchlist_by', blank=True)

    def __str__(self):
        return f"{self.user.username}'s Watchlist"

class CustomList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_lists')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    movies = models.ManyToManyField(Movie, related_name='featured_in_lists', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
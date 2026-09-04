from django.contrib.sites import requests
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.utils.text import slugify

from .forms import ReviewForm
from .models import Movie, Review
import requests

def movies(request):
  movies = Movie.objects.all().order_by('-release_date')
  paginator = Paginator(movies, 20)
  page_number = request.GET.get('page')

  page_obj = paginator.get_page(page_number)
  return render(request, 'movies/movie_list.html', {'page_obj': page_obj})


def movie_detail(request, slug):
    movie = get_object_or_404(Movie, slug=slug)
    reviews = movie.reviews.all().order_by('-reviewed_at')

    user_has_reviewed = None
    if request.user.is_authenticated:
        user_has_reviewed = Review.objects.filter(movie=movie, user=request.user).first()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('home')

        form = ReviewForm(request.POST, instance=user_has_reviewed)
        if form.is_valid():
            review = form.save(commit=False)
            review.movie = movie
            review.user = request.user
            review.save()
            return redirect('movie_detail', slug=movie.slug)
    else:
        form = ReviewForm(instance=user_has_reviewed)

    return render(request, 'movies/movie_detail.html', {
        'movie': movie,
        'reviews': reviews,
        'form': form,
        'user_has_reviewed': user_has_reviewed
    })
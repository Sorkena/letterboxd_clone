from django.contrib.sites import requests
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.utils.text import slugify
from users.models import Watchlist
from django.views import View
from users.models import CustomList
from .forms import ReviewForm, RatingForm
from .models import Movie, Review, MovieRating
from django.db.models import Count, Avg, F
from rest_framework import viewsets

class MovieViewSet(viewsets.ViewSet):
    genres = [
        "Aksiyon", "Macera", "Animasyon", "Komedi", "Suç", "Belgesel", "Dram",
        "Aile", "Fantastik", "Tarih", "Korku", "Müzik", "Gizem", "Romantik",
        "Bilim-Kurgu", "Gerilim", "Savaş", "Vahşi Batı"
    ]

    def list(self, request, *args, **kwargs):
        query = request.query_params.get('q', '').strip()
        genre = request.query_params.get('genre', '').strip()
        sort_by = request.query_params.get('sort', 'newest')

        movies_list = Movie.objects.all()

        if query:
            words = query.replace('-', ' ').split()
            for word in words:
                movies_list = movies_list.filter(title__icontains=word)

        if genre:
            movies_list = movies_list.filter(genres__icontains=genre)

        if sort_by == 'newest':
            movies_list = movies_list.order_by('-release_date')
        elif sort_by == 'oldest':
            movies_list = movies_list.order_by('release_date')
        elif sort_by == 'most_reviewed':
            movies_list = movies_list.annotate(review_count=Count('reviews', distinct=True)).order_by('-review_count')
        elif sort_by == 'least_reviewed':
            movies_list = movies_list.annotate(review_count=Count('reviews', distinct=True)).order_by('review_count')
        elif sort_by == 'highest_rated':
            movies_list = movies_list.annotate(avg_rating=Avg('ratings__rating')).order_by(
                F('avg_rating').desc(nulls_last=True))
        elif sort_by == 'lowest_rated':
            movies_list = movies_list.annotate(avg_rating=Avg('ratings__rating')).order_by(
                F('avg_rating').asc(nulls_last=True))
        else:
            movies_list = movies_list.order_by('-release_date')

        paginator = Paginator(movies_list, 20)
        page_obj = paginator.get_page(request.query_params.get('page'))

        context = {
            'page_obj': page_obj,
            'query': query,
            'genre': genre,
            'genres': self.genres,
            'sort_by': sort_by
        }

        return render(request, 'movies/movie_list.html', context)

    def retrieve(self, request, slug=None, *args, **kwargs):
        movie = get_object_or_404(Movie, slug=slug)
        reviews = movie.reviews.all().order_by('-reviewed_at')

        current_rating = None
        in_watchlist = False
        user_custom_lists = []
        if request.user.is_authenticated:
            user_custom_lists = request.user.custom_lists.all()
            current_rating = MovieRating.objects.filter(movie=movie, user=request.user).first()
            watchlist = Watchlist.objects.filter(user=request.user).first()
            in_watchlist = watchlist.movies.filter(pk=movie.pk).exists() if watchlist else False

        return render(request, 'movies/movie_detail.html', {
            'movie': movie,
            'reviews': reviews,
            'review_form': ReviewForm(),
            'rating_form': RatingForm(instance=current_rating),
            'current_rating': current_rating,
            'in_watchlist': in_watchlist,
            'user_custom_lists': user_custom_lists
        })

    def watchlist_add(self, request, slug=None, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')
        movie = get_object_or_404(Movie, slug=slug)
        watchlist, _ = Watchlist.objects.get_or_create(user=request.user)
        watchlist.movies.add(movie)
        return redirect('movie_detail', slug=movie.slug)

    def watchlist_remove(self, request, slug=None, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')
        movie = get_object_or_404(Movie, slug=slug)
        watchlist, _ = Watchlist.objects.get_or_create(user=request.user)
        watchlist.movies.remove(movie)
        return redirect('movie_detail', slug=movie.slug)

    def update_rating(self, request, slug=None, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')
        movie = get_object_or_404(Movie, slug=slug)
        current_rating = MovieRating.objects.filter(movie=movie, user=request.user).first()
        rating_form = RatingForm(request.data, instance=current_rating)
        if rating_form.is_valid():
            rating = rating_form.save(commit=False)
            rating.movie = movie
            rating.user = request.user
            rating.save()
        return redirect('movie_detail', slug=movie.slug)

    def delete_rating(self, request, slug=None, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')
        movie = get_object_or_404(Movie, slug=slug)
        current_rating = MovieRating.objects.filter(movie=movie, user=request.user).first()
        if current_rating:
            current_rating.delete()
        return redirect('movie_detail', slug=movie.slug)

    def add_review(self, request, slug=None, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')
        movie = get_object_or_404(Movie, slug=slug)
        form = ReviewForm(request.data)
        if form.is_valid():
            review = form.save(commit=False)
            review.movie = movie
            review.user = request.user
            review.save()
        MovieRating.objects.get_or_create(movie=movie, user=request.user, defaults={'rating': review.rating})
        return redirect('movie_detail', slug=movie.slug)

    def add_to_custom_list(self, request, slug=None, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')
        movie = get_object_or_404(Movie, slug=slug)
        list_id = request.data.get('list_id')
        if list_id:
            custom_list = get_object_or_404(CustomList, id=list_id, user=request.user)
            custom_list.movies.add(movie)
        return redirect('movie_detail', slug=movie.slug)

class ReviewViewSet(viewsets.ViewSet):

    def edit(self, request, slug=None, review_id=None, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')

        movie = get_object_or_404(Movie, slug=slug)
        review = get_object_or_404(Review, id=review_id, movie=movie, user=request.user)
        reviews = movie.reviews.all().order_by('-reviewed_at')
        current_rating = MovieRating.objects.filter(movie=movie, user=request.user).first()
        watchlist = Watchlist.objects.filter(user=request.user).first()
        in_watchlist = watchlist.movies.filter(pk=movie.pk).exists() if watchlist else False

        return render(request, 'movies/movie_detail.html', {
            'movie': movie,
            'reviews': reviews,
            'review_form': ReviewForm(instance=review),
            'rating_form': RatingForm(instance=current_rating),
            'current_rating': current_rating,
            'editing_review': review,
            'in_watchlist': in_watchlist,
            'user_custom_lists': request.user.custom_lists.all()
        })

    def update_review(self, request, slug=None, review_id=None, *args, **kwargs):
        if not request.user.is_authenticated:
          return redirect('home')
        movie = get_object_or_404(Movie, slug=slug)
        review = get_object_or_404( Review, id=review_id, movie=movie, user=request.user )
        review.content = request.data.get('content', '')
        review.save()
        return redirect('movie_detail', slug=movie.slug)

    def delete_review(self, request, slug=None, review_id=None, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')
        movie = get_object_or_404(Movie, slug=slug)
        review = get_object_or_404( Review, id=review_id, movie=movie, user=request.user )
        review.delete()
        return redirect('movie_detail', slug=movie.slug)

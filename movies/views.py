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


class MovieListView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()
        genre = request.GET.get('genre', '').strip()
        movies_list = Movie.objects.all()

        genres = [
            "Aksiyon", "Macera", "Animasyon", "Komedi", "Suç", "Belgesel", "Dram",
            "Aile", "Fantastik", "Tarih", "Korku", "Müzik", "Gizem", "Romantik",
            "Bilim Kurgu", "Gerilim", "Savaş", "Vahşi Batı"
        ]

        if query:
            words = query.replace('-', ' ').split()
            for word in words:
                movies_list = movies_list.filter(title__icontains=word)

        if genre:
            movies_list = movies_list.filter(genres__icontains=genre)

        movies_list = movies_list.order_by('-release_date')

        paginator = Paginator(movies_list, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj,
            'query': query,
            'genre': genre,
            'genres': genres
        }

        return render(request, 'movies/movie_list.html', context)


class MovieDetailView(View):
    def get(self, request, slug, *args, **kwargs):
        movie = get_object_or_404(Movie, slug=slug)
        reviews = movie.reviews.all().order_by('-reviewed_at')

        current_rating = None
        in_watchlist = False
        user_custom_lists = []
        if request.user.is_authenticated:
            user_custom_lists = request.user.custom_lists.all()
            current_rating = MovieRating.objects.filter(movie=movie,user=request.user).first()
            watchlist = Watchlist.objects.filter(user=request.user).first()
            in_watchlist = watchlist.movies.filter(pk=movie.pk).exists() if watchlist else False

        review_form = ReviewForm()
        rating_form = RatingForm(instance=current_rating)

        return render(request, 'movies/movie_detail.html', {
            'movie': movie,
            'reviews': reviews,
            'review_form': review_form,
            'rating_form': rating_form,
            'current_rating': current_rating,
            'in_watchlist': in_watchlist,
            'user_custom_lists': user_custom_lists
        })

    def post(self, request, slug, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')

        movie = get_object_or_404(Movie, slug=slug)

        if 'watchlist_add' in request.POST:
            watchlist, _ = Watchlist.objects.get_or_create(user=request.user)
            watchlist.movies.add(movie)
            return redirect('movie_detail', slug=movie.slug)

        if 'watchlist_remove' in request.POST:
            watchlist, _ = Watchlist.objects.get_or_create(user=request.user)
            watchlist.movies.remove(movie)
            return redirect('movie_detail', slug=movie.slug)

        if 'update_rating' in request.POST:
            current_rating= MovieRating.objects.filter(movie=movie,user=request.user).first()
            rating_form = RatingForm(request.POST,instance=current_rating)

            if rating_form.is_valid():
                rating= rating_form.save(commit=False)
                rating.movie = movie
                rating.user = request.user
                rating.save()
                return redirect('movie_detail',slug=movie.slug)

        if 'delete_rating' in request.POST:
            current_rating = MovieRating.objects.filter(movie=movie,user=request.user).first()
            if current_rating:
                current_rating.delete()
            return redirect('movie_detail',slug=movie.slug)

        if 'add_review' in request.POST:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.movie = movie
                review.user = request.user
                review.save()

                MovieRating.objects.get_or_create(movie=movie,user=request.user,defaults={'rating': review.rating})
                return redirect('movie_detail',slug=movie.slug)


        if 'add_to_custom_list' in request.POST:
            list_id = request.POST.get('list_id')
            if list_id:
                custom_list = get_object_or_404(CustomList, id=list_id, user=request.user)
                custom_list.movies.add(movie)
            return redirect('movie_detail', slug=movie.slug)

        reviews = movie.reviews.all().order_by('-reviewed_at')
        current_rating = MovieRating.objects.filter(movie=movie,user=request.user).first()
        rating_form = RatingForm(instance=current_rating)
        watchlist = Watchlist.objects.filter(user=request.user).first()
        in_watchlist = watchlist.movies.filter(pk=movie.pk).exists() if watchlist else False

        return render(request, 'movies/movie_detail.html', {
            'movie': movie,
            'reviews': reviews,
            'review_form': form if 'form' in locals() else ReviewForm(),
            'rating_form': rating_form,
            'current_rating': current_rating,
            'in_watchlist': in_watchlist,
            'user_custom_lists': request.user.custom_lists.all()
        })
class ReviewEditView(View):
    def get(self, request, slug, review_id, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')

        movie = get_object_or_404(Movie, slug=slug)
        review = get_object_or_404(Review,id=review_id,movie=movie,user=request.user)
        reviews = movie.reviews.all().order_by('-reviewed_at')

        current_rating = MovieRating.objects.filter(movie=movie,user=request.user).first()
        review_form = ReviewForm(instance=review)
        rating_form = RatingForm(instance=current_rating)

        watchlist = Watchlist.objects.filter(user=request.user).first()
        in_watchlist = (watchlist.movies.filter(pk=movie.pk).exists()if watchlist else False)

        return render(request, 'movies/movie_detail.html', {
            'movie': movie,
            'reviews': reviews,
            'review_form': review_form,
            'rating_form': rating_form,
            'current_rating': current_rating,
            'editing_review': review,
            'in_watchlist': in_watchlist,
            'user_custom_lists': request.user.custom_lists.all()
        })

    def post(self, request, slug, review_id, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')

        movie = get_object_or_404(Movie, slug=slug)
        review = get_object_or_404(Review,id=review_id,movie=movie,user=request.user)

        if 'delete_review' in request.POST:
            review.delete()
            return redirect('movie_detail',slug=movie.slug)

        if 'update_review' in request.POST:
            form = ReviewForm(request.POST,instance=review)
            if form.is_valid():
                review.content = form.cleaned_data['content']
                review.save()
                return redirect('movie_detail',slug=movie.slug)

        reviews = movie.reviews.all().order_by('-reviewed_at')
        current_rating = MovieRating.objects.filter(movie=movie,user=request.user).first()

        rating_form = RatingForm(instance=current_rating)
        watchlist = Watchlist.objects.filter(user=request.user).first()
        in_watchlist = (watchlist.movies.filter(pk=movie.pk).exists()if watchlist else False)

        return render(request, 'movies/movie_detail.html', {
            'movie': movie,
            'reviews': reviews,
            'review_form': ReviewForm(),
            'rating_form': rating_form,
            'current_rating': current_rating,
            'editing_review': review,
            'in_watchlist': in_watchlist,
            'user_custom_lists': request.user.custom_lists.all(),
        })
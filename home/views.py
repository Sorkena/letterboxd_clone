from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login
from django.db.models import Max, Q
from rest_framework import viewsets
from movies.models import Movie, Review
from users.forms import GenrePreferenceForm
from users.models import UserProfile

class HomeViewSet(viewsets.ViewSet):
    def get_recent_movies(self):
        recent_movies = list(
            Movie.objects.filter(reviews__isnull=False)
            .annotate(latest_review=Max('reviews__reviewed_at'))
            .order_by('-latest_review')[:5]
        )

        if len(recent_movies) < 3:
            exclude_ids = [movie.id for movie in recent_movies]
            fallback_movies = Movie.objects.exclude(id__in=exclude_ids).order_by('?')[:3 - len(recent_movies)]
            recent_movies.extend(fallback_movies)

        return recent_movies

    def get_following_reviews(self, user):
        if not user.is_authenticated:
            return Review.objects.none()
        following_ids = user.following.values_list( 'following_id', flat=True )
        return Review.objects.filter( user_id__in=following_ids ).select_related( 'user', 'movie' ).order_by( '-reviewed_at' )[:5]

    def get_recommended_movies(self, user):
        if not user.is_authenticated:
            return Movie.objects.none()

        profile = UserProfile.objects.filter(user=user).first()
        if not profile:
            return Movie.objects.none()

        genres = profile.interested_genres.all()
        if not genres.exists():
            return Movie.objects.none()

        query = Q()
        for genre in genres:
            query |= Q(genres__icontains=genre.name)

        return Movie.objects.filter(query).exclude(ratings__user=user).distinct().order_by('?')[:5]

    def get_home_context(self, request, register_form=None, login_form=None):
        return {
            'register_form': register_form or UserCreationForm(),
            'login_form': login_form or AuthenticationForm(),
            'recommended_movies': self.get_recommended_movies(request.user),
            'following_reviews': self.get_following_reviews(request.user),
            'recent_movies': self.get_recent_movies
        }
    def home(self, request, *args, **kwargs):
        context = self.get_home_context(request)
        return render(request, 'home/index.html', context)

    def register(self, request, *args, **kwargs):
        register_form = UserCreationForm(request.data)

        if register_form.is_valid():
            user = register_form.save()
            auth_login(request, user)
            return redirect('onboarding')

        context = self.get_home_context(request, register_form=register_form)
        return render(request, 'home/index.html', context)

    def login(self, request, *args, **kwargs):
        login_form = AuthenticationForm(data=request.data)

        if login_form.is_valid():
            user = login_form.get_user()
            auth_login(request, user)
            return redirect('home')

        context = self.get_home_context(request, login_form=login_form)
        return render(request, 'home/index.html', context)

    def onboarding_get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')

        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        form = GenrePreferenceForm(initial={'genres': profile.interested_genres.all()})
        return render(request, 'home/onboarding.html', {'form': form})

    def onboarding_post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')

        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        form = GenrePreferenceForm(request.data)

        if form.is_valid():
            profile.interested_genres.set(form.cleaned_data['genres'])
            return redirect('home')

        return render(request, 'home/onboarding.html', {'form': form})
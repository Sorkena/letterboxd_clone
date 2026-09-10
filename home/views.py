from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login
from django.db.models import Max
from django.views import View
from movies.models import Movie


class HomePageView(View):
    def get_recent_movies(self):
        recent_movies = list(
            Movie.objects.filter(reviews__isnull=False)
            .annotate(latest_review=Max('reviews__reviewed_at'))
            .order_by('-latest_review')[:3]
        )

        if len(recent_movies) < 3:
            exclude_ids = [m.id for m in recent_movies]
            fallback_movies = Movie.objects.exclude(id__in=exclude_ids).order_by('?')[:3 - len(recent_movies)]
            recent_movies.extend(fallback_movies)

        return recent_movies

    def get(self, request, *args, **kwargs):
        register_form = UserCreationForm()
        login_form = AuthenticationForm()

        context = {
            'register_form': register_form,
            'login_form': login_form,
            'recent_movies': self.get_recent_movies(),
        }
        return render(request, 'home/index.html', context)

    def post(self, request, *args, **kwargs):
        register_form = UserCreationForm()
        login_form = AuthenticationForm()

        if 'register' in request.POST:
            register_form = UserCreationForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                login(request, user)
                return redirect('home')

        elif 'login' in request.POST:
            login_form = AuthenticationForm(data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return redirect('home')

        context = {
            'register_form': register_form,
            'login_form': login_form,
            'recent_movies': self.get_recent_movies(),
        }
        return render(request, 'home/index.html', context)
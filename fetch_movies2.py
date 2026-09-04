import os
import django
import requests
from datetime import datetime
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'letterboxd.settings')
django.setup()

from movies.models import Movie

TMDB_API_KEY = 'b69ef646e496500a260bc1ccf689ff0d'
BASE_URL = 'https://api.themoviedb.org/3/discover/movie'
IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'


def fetch_movies_from_api(pages_to_fetch=5):
    for page in range(1, pages_to_fetch + 1):
        print(f"Sayfa {page} çekiliyor...")

        params = {
            'api_key': TMDB_API_KEY,
            'language': 'tr-TR',
            'sort_by': 'vote_count.desc',
            'vote_count.gte': 500,
            'page': page
        }

        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            movies_list = response.json().get('results', [])

            for item in movies_list:
                movie_id = item.get('id')
                poster_path = item.get('poster_path')
                poster_url = f"{IMAGE_BASE_URL}{poster_path}" if poster_path else None

                detail_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
                detail_params = {
                    'api_key': TMDB_API_KEY,
                    'language': 'tr-TR',
                    'append_to_response': 'credits'
                }

                genres_str = studio_str = country_str = director_str = cast_str = language_str = ""
                runtime = None

                try:
                    det_resp = requests.get(detail_url, params=detail_params)
                    if det_resp.status_code == 200:
                        det_data = det_resp.json()

                        genres_str = ", ".join([g['name'] for g in det_data.get('genres', [])])
                        studio_str = ", ".join([s['name'] for s in det_data.get('production_companies', [])])
                        country_str = ", ".join([c['name'] for c in det_data.get('production_countries', [])])

                        language_str = ", ".join([l.get('name', '') for l in det_data.get('spoken_languages', [])])
                        runtime = det_data.get('runtime')

                        crew = det_data.get('credits', {}).get('crew', [])
                        director_str = ", ".join([c['name'] for c in crew if c['job'] == 'Director'])

                        cast = det_data.get('credits', {}).get('cast', [])
                        cast_str = ", ".join([a['name'] for a in cast[:5]])
                except Exception as e:
                    print(f"{item.get('title')} detayları alınamadı: {e}")

                raw_date = item.get('release_date')
                release_date_str = raw_date.strip() if isinstance(raw_date, str) else ''

                if release_date_str:
                    try:
                        parsed_date = datetime.strptime(release_date_str, '%Y-%m-%d')
                        release_date = timezone.make_aware(parsed_date)
                    except (ValueError, TypeError):
                        release_date = timezone.now()
                else:
                    release_date = timezone.now()

                Movie.objects.update_or_create(
                    title=item.get('title'),
                    defaults={
                        'description': item.get('overview', ''),
                        'release_date': release_date,
                        'poster_url': poster_url,
                        'director': director_str,
                        'cast': cast_str,
                        'genres': genres_str,
                        'studio': studio_str,
                        'country': country_str,
                        'language': language_str,
                        'runtime': runtime,
                    }
                )

        except requests.exceptions.RequestException as e:
            print(f"API isteği sırasında hata oluştu: {e}")
            break

    print("Veriler güncellendi.")


if __name__ == '__main__':
    fetch_movies_from_api(pages_to_fetch=25)
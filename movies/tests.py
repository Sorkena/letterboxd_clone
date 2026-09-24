from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Movie, Review, MovieRating


class ReviewSecurityTestCase(TestCase):

    def setUp(self):
        self.user_neo = User.objects.create_user(
            username='neo',
            password='password123'
        )

        self.user_smith = User.objects.create_user(
            username='smith',
            password='password123'
        )

        self.movie = Movie.objects.create(
            title='Matrix',
            description='placeholder',
            release_date=timezone.now(),
            runtime=136,
            poster_url='',
            slug='matrix',
            director='placeholder',
            cast='placeholder',
            genres='Bilim-Kurgu',
            studio='placeholder',
            country='placeholder',
            language='English'
        )

        self.neo_review = Review.objects.create(
            user=self.user_neo,
            movie=self.movie,
            rating=8,
            content="Neo'nun yorumu"
        )

    def test_cannot_update_another_users_review(self):
        self.client.login(
            username='smith',
            password='password123'
        )

        url = reverse(
            'review_update',
            args=[self.movie.slug, self.neo_review.id]
        )

        response = self.client.post(url, {
            'content': "Smith Neo'nun yorumunu değiştirmeye çalışıyor"
        })

        self.assertEqual(response.status_code, 404)

        self.neo_review.refresh_from_db()

        self.assertEqual(self.neo_review.rating, 8)
        self.assertEqual(
            self.neo_review.content,
            "Neo'nun yorumu"
        )

        self.assertEqual(Review.objects.count(), 1)

    def test_user_can_add_own_review_without_changing_another_users_review(self):
        self.client.login(
            username='smith',
            password='password123'
        )

        url = reverse(
            'review_add',
            args=[self.movie.slug]
        )

        response = self.client.post(url, {
            'rating': 2,
            'content': "Smith'in yorumu"
        })

        self.assertEqual(response.status_code, 302)

        self.neo_review.refresh_from_db()

        self.assertEqual(self.neo_review.rating, 8)
        self.assertEqual(
            self.neo_review.content,
            "Neo'nun yorumu"
        )

        self.assertEqual(Review.objects.count(), 2)

        smith_review = Review.objects.get(
            user=self.user_smith,
            movie=self.movie
        )

        self.assertEqual(smith_review.rating, 2)
        self.assertEqual(
            smith_review.content,
            "Smith'in yorumu"
        )

        smith_rating = MovieRating.objects.get(
            user=self.user_smith,
            movie=self.movie
        )

        self.assertEqual(smith_rating.rating, 2)
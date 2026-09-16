from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Movie, Review


class ReviewSecurityTestCase(TestCase):
    def setUp(self):
        self.user_neo = User.objects.create_user(username='neo', password='password123')
        self.user_smith = User.objects.create_user(username='smith', password='password123')

        self.movie = Movie.objects.create(
            title="Matrix",
            description = "placeholder",
            release_date=timezone.now(),
            runtime=136,
            poster_url ='',
            slug = "matrix",
            director = "placeholder",
            cast = "placeholder",
            genres = "placeholder",
            studio = "placeholder",
            country = "placeholder",
            language = "e",

        )

        self.neo_review = Review.objects.create(
            user=self.user_neo,
            movie=self.movie,
            rating=8,
            content="Neo'nun yorumu"
        )

    def test_cannot_update_another_users_review(self):
        self.client.login(username='smith', password='password123')

        url = reverse('movie_detail', args=[self.movie.slug])
        response = self.client.post(url, {
            'rating': 2,
            'content': "Smith'in yorumu"
        })


        self.neo_review.refresh_from_db()

        self.assertEqual(self.neo_review.rating, 8)
        self.assertEqual(self.neo_review.content, "Neo'nun yorumu")


        self.assertEqual(Review.objects.count(), 2)

        smith_review = Review.objects.get(user=self.user_smith, movie=self.movie)
        self.assertEqual(smith_review.rating, 2)
        self.assertEqual(smith_review.content, "Smith'in hackli yorumu")
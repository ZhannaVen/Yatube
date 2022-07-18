from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from posts.forms import PostForm

User = get_user_model()


class TestCreateNewUser(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()

    def setUp(self):
        self.first_name = 'Test',
        self.last_name = 'User',
        self.username = 'TestUser2',
        self.email = 'testuser@email.com',
        self.password = 'N564v8n59'

    def test_new_user_is_created(self):
        """Создается новый пользователь."""

        user_count = User.objects.count()
        form_data = {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'username': self.username,
            'email': self.email,
            'password1': self.password,
            'password2': self.password

        }
        response = self.client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), user_count + 1)
        self.assertTrue(
            User.objects.filter(
                username='TestUser2',
            ).exists()
        )

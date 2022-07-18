from django import forms
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ..forms import CreationForm

User = get_user_model()


class UsersPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.user = User.objects.create_user(username='TestUser')

    def test_signup_page_show_correct_context(self):
        """Шаблон signup.html сформирован с правильным контекстом."""

        response = self.client.get(reverse('users:signup'))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context.get('form'), CreationForm)
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,

        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

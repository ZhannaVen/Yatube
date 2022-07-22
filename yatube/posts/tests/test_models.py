from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 1234567890',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""

        objects = {
            self.group: self.group.title,
            self.post: self.post.text[:15]
        }
        for key, value in objects.items():
            with self.subTest(key=key):
                self.assertEqual(value, str(key))

    def test_verbose_name_group(self):
        """verbose_name полей модели Group совпадают с ожидаемыми."""

        group = self.group
        verbose_names = {
            'title': 'Название сообщества',
            'slug': 'Slug сообщества',
            'description': 'Описание'
        }
        for field, verbose_name in verbose_names.items():
            with self.subTest(field=field):
                verbose_name_field = group._meta.get_field(field).verbose_name
                self.assertEqual(verbose_name_field, verbose_name)

        verbose_name_meta = group._meta.verbose_name
        verbose_names_meta = group._meta.verbose_name_plural
        self.assertEqual(verbose_name_meta, 'Сообщество')
        self.assertEqual(verbose_names_meta, 'Сообщества')

    def test_verbose_name_post(self):
        """verbose_name полей модели Post совпадают с ожидаемыми."""

        post = self.post
        verbose_names = {
            'text': 'Текст поста',
            'pub_date': 'Дата создания',
            'author': 'Автор',
            'group': 'Сообщество'
        }
        for field, verbose_name in verbose_names.items():
            with self.subTest(field=field):
                verbose_name_field = post._meta.get_field(field).verbose_name
                self.assertEqual(verbose_name_field, verbose_name)

        verbose_name_meta = post._meta.verbose_name
        verbose_names_meta = post._meta.verbose_name_plural
        self.assertEqual(verbose_name_meta, 'Пост')
        self.assertEqual(verbose_names_meta, 'Посты')

    def test_help_text(self):
        """help_text поля title модели Post совпадает с ожидаемым."""
        post = self.post
        help_text = post._meta.get_field('group').help_text
        self.assertEqual(
            help_text,
            'Сообщество, к которому будет относиться пост'
        )
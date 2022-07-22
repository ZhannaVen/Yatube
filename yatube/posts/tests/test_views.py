import shutil
import tempfile

from http import HTTPStatus

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Follow, Group, Post


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая запись 1',
            group=PostPagesTests.group,
            image='TestImg'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='TestImg',
            content=cls.small_gif,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def some_func_for_testing_context(self, response, bool=False):
        if bool is True:
            return response.context['post']
        return response.context['page_obj'][0]

    def test_pages_show_correct_context(self):
        """Шаблоны: index.html, group_list.html, profile.html,
        post_detail.html сформированы с правильным контекстом.
        Также  это задание 3 - доп. проверка при создании поста.
        """

        templates = (
            ('posts:index', None, ''),
            ('posts:group_list', (self.group.slug,), ''),
            ('posts:profile', (self.user.username,), ''),
            ('posts:post_detail', (self.post.id,), True),
        )

        for template, args, bool in templates:
            with self.subTest(template=template):
                response = self.client.get(reverse(template, args=args))
                object = self.some_func_for_testing_context(response, bool)
                object_text_0 = object.text
                object_group_0 = object.group
                object_author_0 = object.author
                object_pub_date_0 = object.pub_date
                object_image_0 = object.image
                self.assertEqual(object_text_0, self.post.text)
                self.assertEqual(object_group_0, self.post.group)
                self.assertEqual(object_author_0, self.post.author)
                self.assertEqual(object_pub_date_0, self.post.pub_date)
                self.assertEqual(object_image_0, self.post.image)
                self.assertContains(response, '<img')
                if template in ('posts:profile'):
                    object = response.context['profile']
                    self.assertEqual(object, self.post.author)
                elif template in ('posts:group_list'):
                    object = response.context['group']
                    self.assertEqual(object, self.post.group)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create.html сформирован с правильным контекстом."""

        templates = (
            ('posts:post_edit', (self.post.id,)),
            ('posts:post_create', ''),
        )
        for template, args in templates:
            with self.subTest(template=template):
                response = self.authorized_client.get(
                    reverse(template, args=args)
                )
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context.get('form'), PostForm)
                fields = {
                    'group': forms.fields.ChoiceField,
                    'text': forms.fields.CharField,
                }
                for value, expected in fields.items():
                    with self.subTest(value=value):
                        field = response.context.get('form').fields.get(value)
                        self.assertIsInstance(field, expected)

    def test_post_doesnot_belong_to_the_group_none(self):
        """Пост не попал в группу, для которой не был предназначен."""

        second_post = Post.objects.create(
            author=self.user,
            text='Тестовая запись 2',
            group=self.group,
        )
        group_none = Group.objects.create(
            title='Тестовая группа None',
            slug='test_group_none',
            description='Какое-то тестовое описание',
        )
        response = self.client.get(
            reverse('posts:group_list', args=(group_none.slug,))
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.context['page_obj']), 0)

        response = self.client.get(
            reverse('posts:group_list', args=(self.group.slug,))
        )
        self.assertEqual(second_post, response.context['page_obj'][0])

    def test_cache_index(self):
        """Тестирование функции кэша на главной странице."""

        response = self.client.get(reverse('posts:index'))
        content_old = response.content
        Post.objects.create(
            author=self.user,
            text='test cache',
            group=self.group,
        )
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(response.content, content_old)
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, content_old)


class PaginatorPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser3')
        cls.user2 = User.objects.create_user(username='UserForTestFollow')
        cls.group = Group.objects.create(
            title='Тестовая группа3',
            slug='test_group3',
            description='Тестовое описание3',
        )
        for post in range(settings.NUM2):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовая запись 3',
                group=PaginatorPagesTests.group,
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client2 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2.force_login(self.user2)

    def test_paginator(self):
        """Количество постов на первых страницах:
        index, group_list, profile и follow_index равно 10,
        на вторых - 3.
        """

        templates = (
            ('posts:index', ''),
            ('posts:group_list', (self.group.slug,)),
            ('posts:profile', (self.user,)),
            ('posts:follow_index', None),
        )
        self.authorized_client2.get(
            reverse('posts:profile_follow', args=(self.user,))
        )
        for template, args in templates:
            with self.subTest(template=template):
                number_of_posts = (
                    ('?page=1', settings.NUM),
                    ('?page=2', settings.NUM2 - settings.NUM)
                )
                for page, quantity in number_of_posts:
                    with self.subTest(page=page):
                        response = self.authorized_client2.get(
                            reverse(template, args=args)
                            + page
                        )
                        self.assertEqual(len(
                            response.context['page_obj']),
                            quantity
                        )


class SubcribtionTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='TestUser1')
        cls.user2 = User.objects.create_user(username='TestUser2')
        cls.user3 = User.objects.create_user(username='TestUser3')

    def setUp(self):
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(self.user1)
        self.authorized_client3 = Client()
        self.authorized_client3.force_login(self.user3)

    def test_follow(self):
        """Авторизованный пользователь может
        подписываться на других пользователей."""

        following_number_old = Follow.objects.filter(
            user=self.user1.id,
            author=self.user2.id
        ).count()
        self.assertEqual(following_number_old, 0)
        self.authorized_client1.get(
            reverse('posts:profile_follow', args=(self.user2,))
        )
        following_number_new = Follow.objects.filter(
            user=self.user1.id,
            author=self.user2.id
        ).count()
        self.assertEqual(following_number_new, 1)

        following = Follow.objects.first()
        self.assertEqual(following.user, self.user1)
        self.assertEqual(following.author, self.user2)

    def test_unfollow(self):
        """Авторизованный пользователь может
        отписываться от других пользователей."""

        Follow.objects.create(
            user=self.user1,
            author=self.user2,
        )
        following_number_old = Follow.objects.filter(
            user=self.user1.id,
            author=self.user2.id
        ).count()
        self.assertEqual(following_number_old, 1)
        self.authorized_client1.get(
            reverse('posts:profile_unfollow', args=(self.user2,))
        )
        following_number_new = Follow.objects.filter(
            user=self.user1.id,
            author=self.user2.id
        ).count()
        self.assertEqual(following_number_new, 0)

    def test_new_post_in_news(self):
        """Новая запись пользователя появляется
        в ленте тех, кто на него подписан
        и не появляется в ленте тех, кто не подписан.
        """

        post = Post.objects.create(
            author=self.user2,
            text='Тестовая запись пользователя 2',
        )
        Follow.objects.create(
            user=self.user1,
            author=self.user2,
        )
        response = self.authorized_client1.get(
            reverse('posts:follow_index')
        )
        self.assertContains(response, post.text)

        response = self.authorized_client3.get(
            reverse('posts:follow_index')
        )
        self.assertNotContains(response, post.text)

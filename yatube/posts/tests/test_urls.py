from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Group, Post


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.user_not_author = User.objects.create_user(username='TestUser2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая запись 1',
        )
        cls.urls = (
            ('posts:index', None),
            ('posts:group_list', (cls.group.slug,)),
            ('posts:profile', (cls.user,)),
            ('posts:post_detail', (cls.post.id,)),
            ('posts:post_edit', (cls.post.id,)),
            ('posts:post_create', None),
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user_not_author)

    def test_url_exists_at_desired_location(self):
        """Проверка namespace:name = URL."""

        namespaces = (
            ('posts:index', None, '/'),
            ('posts:group_list',
                (self.group.slug,),
                f'/group/{self.group.slug}/'),
            ('posts:profile', (self.user,), f'/profile/{self.user}/'),
            ('posts:post_detail', (self.post.id,), f'/posts/{self.post.id}/'),
            (
                'posts:post_edit',
                (self.post.id,),
                f'/posts/{self.post.id}/edit/'
            ),
            ('posts:post_create', None, '/create/'),
        )
        for namespace, args, url in namespaces:
            with self.subTest(url=url):
                self.assertEqual(reverse(namespace, args=args), url)

    def test_page_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон.
        Проверка namespace:name.
        """

        templates = (
            ('posts:index', None, 'posts/index.html'),
            ('posts:group_list',
                (self.group.slug,),
                'posts/group_list.html'),
            ('posts:profile', (self.user,), 'posts/profile.html'),
            ('posts:post_detail',
                (self.post.id,),
                'posts/post_detail.html'),
            ('posts:post_edit',
                (self.post.id,),
                'posts/post_create.html'),
            ('posts:post_create',
                None,
                'posts/post_create.html'),
        )
        for namespace, args, template in templates:
            with self.subTest(namespace=namespace):
                response = self.authorized_client.get(
                    reverse(namespace, args=args)
                )
                self.assertTemplateUsed(response, template)

    def test_urls_are_available_to_author(self):
        """Все URL-адреса доступны автору."""

        for url, args in self.urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(reverse(url, args=args))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_are_available_to_not_author_except_edit(self):
        """Все URL-адреса, кроме post_edit доступны не автору,
        а адрес post_edit - перенаправляет не автора на post_detail.
        """

        for url, args in self.urls:
            if url in ('posts:post_edit',):
                response = self.authorized_client2.get(reverse(url, args=args))
                self.assertRedirects(
                    response,
                    reverse('posts:post_detail', args=(self.post.id,))
                )
            else:
                with self.subTest(url=url):
                    response = self.authorized_client2.get(
                        reverse(url, args=args)
                    )
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_are_available_to_guest_except_edit_and_create(self):
        """Все URL-адреса, кроме post_edit и post_create
         доступны неавторизованному пользователю,
        а адреса post_edit и post_create -
        перенаправляют неавторизованного пользователя на login.
        """

        for url, args in self.urls:
            with self.subTest(url=url):
                if url in ('posts:post_edit', 'posts:post_create'):
                    smth_1 = reverse('users:login')
                    smth_2 = reverse(url, args=args)
                    response = self.client.get(smth_2, follow=True)
                    self.assertRedirects(response, f'{smth_1}?next={smth_2}')
                else:
                    response = self.client.get(reverse(url, args=args))
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_all_user(self):
        """Страница /posts/unexisting_page/ доступна любому пользователю."""

        response = self.client.get('posts:unexisting_page')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_unexisting_page_custom_template(self):
        """Страница 404 отдает кастомный шаблон."""

        response = self.client.get('posts:unexisting_page')
        self.assertTemplateUsed(response, 'core/404.html')


from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_guest_client_uses_correct_location(self):
        """Проверка namespace:name = URL, проверка гостем."""

        namespaces = (
            ('users:signup', None, '/auth/signup/'),
            ('users:login', None, '/auth/login/'),
            ('users:password_reset', None, '/auth/password_reset/'),
            ('users:password_reset_done', None, '/auth/password_reset/done/'),
            (
                'users:password_reset_confirm',
                ('uidb64', 'token'),
                '/auth/reset/<uidb64>/<token>/'
            ),
            ('users:password_reset_complete', None, '/auth/reset/done/'),
        )
        for namespace, args, url in namespaces:
            response = self.client.get(
                reverse(namespace, args=args)
            )
            with self.subTest(namespace=namespace):
                self.assertTrue(response, url)

    def test_urls_authorized_client_uses_correct_location(self):
        """Проверка namespace:name = URL,
        проверка авторизованным пользователем.
        """

        namespaces = (
            ('users:password_change', '/auth/password_change/'),
            ('users:password_change_done', '/auth/password_change/done/'),
            ('users:logout', '/auth/logout/'),
        )
        for namespace, url in namespaces:
            with self.subTest(url=url):
                self.assertEqual(reverse(namespace), url)

    def test_page_uses_correct_template_tested_by_guest(self):
        """URL-адрес использует соответствующий шаблон.
        Проверка гостем.
        """

        namespaces = (
            ('users:signup', None, 'users/signup.html'),
            ('users:login', None, 'users/login.html'),
            ('users:password_reset', None, 'users/password_reset_form.html'),
            (
                'users:password_reset_done',
                None,
                'users/password_reset_done.html'
            ),
            (
                'users:password_reset_confirm',
                ('uidb64', 'token'),
                'users/password_reset_confirm.html'
            ),
            (
                'users:password_reset_complete',
                None,
                'users/password_reset_complete.html'
            ),
        )
        for namespace, args, template in namespaces:
            with self.subTest(namespace=namespace):
                response = self.client.get(
                    reverse(namespace, args=args)
                )
                self.assertTemplateUsed(response, template)

    def test_page_uses_correct_template_tested_by_authorized(self):
        """URL-адрес использует соответствующий шаблон.
        Проверка авторизованным пользователем.
        """

        namespaces = (
            ('users:password_change', 'users/password_change_form.html'),
            ('users:password_change_done', 'users/password_change_done.html'),
            ('users:logout', 'users/logged_out.html'),
        )
        for namespace, template in namespaces:
            with self.subTest(namespace=namespace):
                response = self.authorized_client.get(reverse(namespace))
                self.assertTemplateUsed(response, template)

    def test_urls_are_available_to_guest_except_password_change(self):
        """Все URL-адреса, кроме смены пароля - доступны гостю.
        страница смены пароля перенаправит гостя на страницу авторизации.
        """

        urls = (
            ('users:signup', None),
            ('users:login', None),
            ('users:password_reset', None),
            ('users:password_reset_done', None),
            ('users:password_reset_confirm', ('uidb64', 'token')),
            ('users:password_reset_complete', None),
            ('users:password_change', None),
            ('users:password_change_done', None),
            ('users:logout', None),
        )

        for url, args in urls:
            with self.subTest(url=url):
                if url in (
                    'users:password_change',
                    'users:password_change_done'
                ):
                    smth_1 = reverse('users:login')
                    smth_2 = reverse(url, args=args)
                    response = self.client.get(smth_2, follow=True)
                    self.assertRedirects(response, f'{smth_1}?next={smth_2}')
                else:
                    response = self.client.get(reverse(url, args=args))
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_change_password_are_available_to_authorized(self):
        """Страницы смены пароля доступны авторизованному пользователю."""

        urls = (
            ('users:password_change'),
            ('users:password_change_done'),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(reverse(url))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_all_user(self):
        """Страница /users/unexisting_page/ доступна любому пользователю."""
        response = self.client.get('users:unexisting_page')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

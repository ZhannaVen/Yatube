from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_url_is_OK(self):
        """Checking the availability of the address of static pages."""

        addresses = ('about:author', 'about:tech')
        for address in addresses:
            response = self.client.get(reverse(address))
            with self.subTest(address=address):
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_exists_at_desired_location(self):
        """Checking namespace:name = URL."""

        namespaces = (
            ('about:author', '/about/author/'),
            ('about:tech', '/about/tech/'),
        )
        for namespace, url in namespaces:
            with self.subTest(url=url):
                self.assertEqual(reverse(namespace), url)

    def test_pages_uses_correct_template(self):
        """The URL uses the appropriate pattern.
        Checking namespace:name.
        """

        templates_pages_names = (
            ('about/author.html', 'about:author'),
            ('about/tech.html', 'about:tech'),
        )

        for template, reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse(reverse_name))
                self.assertTemplateUsed(response, template)

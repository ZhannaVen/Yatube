import shutil
import tempfile

from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings, Client
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Group, Post

User = get_user_model()


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test_group',
            description='Test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test post 1',
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_form_create(self):
        """A valid form creates post in Post.
        The created post has the same author, group, text and picture.
        """
        post_count = Post.objects.count()

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'group': self.group.id,
            'text': 'Test post 2',
            'image': uploaded,
        }
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data,
                                               follow=True)
        self.assertRedirects(
            response,
            reverse('posts:profile', args=(self.user.username,))
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Test post 2',
                group=self.group,
                image='posts/small.gif'
            ).exists()
        )

        post = Post.objects.first()
        post_text_0 = post.text
        post_group_0 = post.group
        post_author_0 = post.author
        post_image_0 = post.image
        self.assertEqual(post_text_0, form_data['text'])
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_form_edit(self):
        """A valid form edits post in Post.
        The edited post has the same author,
        group, and text.
        """
        group_2 = Group.objects.create(
            title='Test group 2',
            slug='test_group2',
            description='Test group 2',
        )
        post_count = Post.objects.count()
        form_data = {
            'group': group_2.id,
            'text': 'Test post 1(edited)',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(self.post.id,))
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group']
            ).exists()
        )

        post = Post.objects.first()
        post_text_0 = post.text
        post_group_0 = post.group
        post_author_0 = post.author
        self.assertEqual(post_text_0, form_data['text'])
        self.assertEqual(post_group_0, group_2)
        self.assertEqual(post_author_0, self.user)

        response = self.authorized_client.get(reverse(
            'posts:group_list',
            args=(self.group.slug,))
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(
            response.context['page_obj']), 0
        )

    def test_form_is_not_created(self):
        """A valid form does not create post in Post
        from an unauthorized user.
        """
        post_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Test post 3',
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            '/auth/login/?next=/create/'
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertFalse(
            Post.objects.filter(
                text='Test post 3',
                group=self.group
            ).exists()
        )

    def test_title_label(self):
        """The function checks labels."""

        group_label = TestCreateFormTests.form.fields['group'].label
        text_label = TestCreateFormTests.form.fields['text'].label
        self.assertEqual(group_label, 'Группа')
        self.assertEqual(text_label, 'Текст')

    def test_title_help_text(self):
        """The function checks help_text."""

        group_help_text = TestCreateFormTests.form.fields['group'].help_text
        text_help_text = TestCreateFormTests.form.fields['text'].help_text
        self.assertEqual(group_help_text, 'Выберите группу из списка')
        self.assertEqual(
            text_help_text,
            'Здесь должен быть какой-нибудь текст'
        )

    def test_form_create_comment(self):
        """A valid form creates a comment in the Comment.
         The created comment has the same text.
        """
        comment_count = Comment.objects.filter(pk=self.post.id).count()
        form_data = {
            'text': 'A comment to the post',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', args=(self.post.id,)),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(self.post.id,))
        )
        self.assertEqual(
            Comment.objects.filter(pk=self.post.id).count(),
            comment_count + 1
        )
        self.assertTrue(
            Comment.objects.filter(
                text='A comment to the post',
            ).exists()
        )

        comment = Comment.objects.filter(pk=self.post.id).first()
        comment_text_0 = comment.text
        comment_author_0 = comment.author.username
        comment_post_0 = comment.post.pk
        self.assertEqual(comment_text_0, form_data['text'])
        self.assertEqual(comment_author_0, self.user.username)
        self.assertEqual(comment_post_0, self.post.pk)

    def test_form_is_not_created_comment(self):
        """A valid form does not create a comment in Comment
        from an unauthorized user.
        """

        comment_count = Comment.objects.filter(pk=self.post.id).count()
        form_data = {
            'text': 'Comment to the post 2',
        }
        response = self.client.post(
            reverse('posts:add_comment', args=(self.post.id,)),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.id}/comment/'
        )
        self.assertEqual(
            Comment.objects.filter(pk=self.post.id).count(),
            comment_count
        )
        self.assertFalse(
            Comment.objects.filter(
                text='Comment to the post 2',
            ).exists()
        )

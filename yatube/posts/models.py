from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        'Group name',
        max_length=200,
    )
    slug = models.SlugField(
        'Group slug',
        unique=True,
    )
    description = models.TextField('Group description')

    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField('Post text')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Author'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Group',
        help_text='The group to which the post will belong'
    )
    image = models.ImageField(
        'Image',
        upload_to='posts/',
        blank=True
    )
    pub_date = models.DateTimeField(
        'Date of publication',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Post'
        verbose_name_plural = 'Post'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Post commented on'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Author of the comment'
    )
    text = models.TextField('Comment text')
    pub_date = models.DateTimeField(
        'Date of publication',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="follower",
        verbose_name='Follower')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="following",
        verbose_name='Subscribe to the author')

    class Meta:

        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'

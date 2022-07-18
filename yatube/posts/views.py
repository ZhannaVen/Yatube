from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post
from .utils import paginator_yatube


User = get_user_model()


@cache_page(50, key_prefix='index_page')
def index(request):
    post_list = Post.objects.select_related('author', 'group')
    page_obj = paginator_yatube(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = paginator_yatube(request, post_list)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    post_list = profile.posts.select_related('group')
    page_obj = paginator_yatube(request, post_list)
    user = request.user
    if (
        (request.user.is_authenticated)
        and (profile.following.filter(user=user))
        and (user != profile)
    ):
        following = True
    else:
        following = False
    context = {
        'profile': profile,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comment_list = post.comments.select_related('author')
    context = {
        'post': post,
        'form': CommentForm(),
        'comment_list': comment_list,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if not form.is_valid():
        context = {'form': form}
        return render(request, 'posts/post_create.html', context)
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', request.user.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if not form.is_valid():
        context = {
            'form': form,
        }
        return render(request, 'posts/post_create.html', context)
    form.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    following = Follow.objects.filter(user=request.user).all()
    author_list = []
    for author in following:
        author_list.append(author.author.id)
    post_list = Post.objects.filter(author__in=author_list).all()
    page_obj = paginator_yatube(request, post_list)
    context = {
        'author_list': author_list,
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    follow_number = Follow.objects.filter(
        user=user.id,
        author=author.id
    ).count()
    if follow_number == 0 and author.id != user.id:
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    user = request.user.id
    author = get_object_or_404(User, username=username)
    follow_number = Follow.objects.filter(
        user=user,
        author=author.id
    ).count()
    if follow_number == 1:
        Follow.objects.filter(
            user=request.user,
            author=author
        ).delete()
    return redirect('posts:profile', username=username)

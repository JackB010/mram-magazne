try:
    from django.utils import simplejson as json
except ImportError:
    import json

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect
from django.http import Http404, HttpResponse
from .models import Article, Tag, Comment
from .forms import ArticleForm, TagForm, CommentForm
import random


@login_required
def create_post(request):
    if (not request.user.profile.super_profile):
        raise Http404()
    form_a = ArticleForm(request.POST or None, request.FILES or None)
    form_t = TagForm(request.POST or None)
    if request.method == 'POST':
        if form_t.is_valid() and form_a.is_valid():
            tags = form_t.cleaned_data['tag'].split(' ')
            tags = list(filter(lambda x: x.replace(' ', '') != '', tags))
            [Tag.objects.get_or_create(tag=i)for i in tags]
            tags = [Tag.objects.get(tag=i) for i in tags]
            data = form_a.clean()
            data['user'] = request.user
            obj = Article.objects.create(**data)
            obj.tags.set(tags)
            return redirect('posts')
    form_a = ArticleForm()
    form_t = TagForm()
    context = {
        'form_a': form_a,
        'form_t': form_t
    }
    return render(request, 'articles/create.html', context)


def top_tags(request):
    items = {i.id: i.count_tag for i in Tag.objects.all()}
    items = sorted(items.items(), key=lambda x: x[1], reverse=True)[:10]
    items = [i[0] for i in items]
    tags = [Tag.objects.get(id=i) for i in items]

    return render(request, 'articles/top_tags.html', {'tags': tags})


def top_posts(request):
    posts = Article.objects.filter(Q(status='PUB') & Q(
        active=True)).order_by('-total_likes_f')[:10]
    return render(request, 'articles/posts.html', {'posts': posts})


def post_by_tag(request, tag=None):
    tag = get_object_or_404(Tag, tag=tag)
    posts = Article.objects.filter(
        Q(tags=tag) & Q(status='PUB') & Q(active=True)).order_by('-created')
    return render(request, 'articles/posts.html', {'posts': posts, 'tag': tag})


def posts_list(request):
    posts = Article.objects.filter(
        Q(status='PUB') & Q(active=True)).order_by('-created')
    return render(request, 'articles/posts.html', {'posts': posts})


def post(request, id=None, status=None):
    post = get_object_or_404(Article, Q(status=status)
                             & Q(id=id) & Q(active=True))
    comments = post.comments.filter(active=True).order_by('-created')
    form = CommentForm(request.POST or None)
    related_posts = Article.objects.filter(Q(tags__in=post.tags.all()) & Q(status='PUB')
                                           & Q(active=True)).exclude(id=post.id).order_by('?')[:8]

    return render(request, 'articles/post.html', {'post': post,
                                                  'form': form,
                                                  'comments': comments,
                                                  'related_posts': set(related_posts)})


@login_required
def update_post(request, id=None, status=None):

    post = get_object_or_404(Article, Q(status=status)
                             & Q(id=id) & Q(active=True))
    if not request.user.profile.super_profile and post.user != request.user:
        raise Http404()
    form = ArticleForm(instance=post)
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            if post.status == 'DRA':
                return redirect('post', id=id, status='DRA')
            return redirect('post', id=id, status='PUB')

    return render(request, 'articles/update.html', {'form': form,   'post': post})


def search(request):
    query = request.GET.get('q')

    if query == '':
        return redirect('posts')
    if query != '':
        posts = Article.objects.filter(
            Q(status='PUB') & Q(active=True)).order_by('-created')
        posts = posts.filter(Q(tags__tag__icontains=query) |
                             Q(title__icontains=query) |
                             Q(user__username=query))

    return render(request, 'articles/posts.html', {'posts': set(posts), 'query': query})
#########  api  ###############


@ login_required
@ require_POST
def like_api(request, id=None):
    if request.method == 'POST':
        user = request.user
        obj = Article.objects.get(id=id)
        if obj.likes.filter(id=user.id).exists():
            obj.likes.remove(user)
        else:
            obj.likes.add(user)
        obj.total_likes_f = obj.total_likes
        # obj.save()
        user_liked = user in obj.likes.all()
        num = obj.comments.filter(active=True).count()
        ctx = json.dumps({'likes_count': obj.total_likes,
                          'comments_count':num,
                          'user_liked': user_liked})

    return HttpResponse(ctx, content_type='application/json')


@ login_required
def is_liked_api(request):
    if request.method == 'GET':
        user = request.user
        id = request.GET.get('id')
        obj = get_object_or_404(Article, id=id)
        user_liked = user in obj.likes.all()
    return HttpResponse(json.dumps({'user_liked': user_liked}), content_type='application/json')


@ login_required
@ require_POST
def delete_comment_api(request):
    if request.method == 'POST':
        user = request.user
        id = request.POST.get('id')

        comment = Comment.objects.get(id=id)
        if comment.user != user:
            return HttpResponse()
        else:
            comment.active = False
            comment.save()
            num = comment.article.comments.filter(active=True).count()
        return HttpResponse(json.dumps({'comments_count':num}), content_type='application/json')


@ login_required
@ require_POST
def comment_api(request):
    if request.method == 'POST':
        user = request.user
        id = request.POST.get('id')
        comment = request.POST.get('comment')
        obj = Article.objects.get(id=id)
        if comment.replace(' ', '') == '':
            return HttpResponse()
        num = Comment.objects.filter(Q(article=obj) and Q(active=True)).count()+1
        obj = Comment.objects.create(article=obj, user=user, comment=comment)

        return HttpResponse(json.dumps({'comment': obj.comment, 'id': str(obj.id), 'comments_count':num}), content_type='application/json')


@ login_required
@ require_POST
def save_api(request):
    if request.method == 'POST':
        user = request.user
        id = request.POST.get('id')
        obj = get_object_or_404(Article, id=id)

        if obj.saved.filter(id=user.id).exists():
            obj.saved.remove(user)
        else:
            obj.saved.add(user)
        is_post_saved = user in obj.saved.all()
    return HttpResponse(json.dumps({'is_post_saved': is_post_saved}), content_type='application/json')


@ login_required
def is_saved_api(request):
    if request.method == 'GET':
        user = request.user
        id = request.GET.get('id')
        if id != '':
            post = Article.objects.get(id=id)
            items = user in post.saved.all()
        else:
            posts = Article.objects.filter(
                Q(status='PUB') & Q(active=True)).order_by('-created')

            profile_id = request.GET.get('profile_id')
            ###################
            if profile_id:
                profile = get_user_model().objects.filter(profile__id=profile_id).first()
                posts = profile.creater.filter(
                    Q(status='PUB') & Q(active=True)).order_by('-created')
            top = request.GET.get('top')
            if top:
                posts = Article.objects.filter(Q(status='PUB') & Q(
                    active=True)).order_by('-total_likes_f')[:10]
            tag = request.GET.get('tag')
            if tag != '':
                tag = Tag.objects.get(tag=tag)
                posts = posts.filter(tags=tag)
            items = [user in post.saved.all() for post in posts]
            query = request.GET.get('query')
            if query != '':
                posts = posts.filter(Q(tags__tag__icontains=query) |
                                     Q(title__icontains=query) |
                                     Q(user__username=query))
                items = [user in post.saved.all() for post in set(posts)]
    return HttpResponse(json.dumps({'items': items}), content_type='application/json')


@ login_required
@ require_POST
def delete_post_api(request):
    if request.method == 'POST':
        user = request.user
        id = request.POST.get('id')
        obj = Article.objects.get(id=id)
        if user == obj.user:
            obj.active = False
            obj.save()
    return HttpResponse(json.dumps({}), content_type='application/json')


@ login_required
@ require_POST
def super_profile_api(request):
    if request.method == 'POST':
        user = request.user
        id = request.POST.get('id')
        obj = get_user_model().objects.get(profile__id=id)
        if user.is_superuser:

            obj.profile.super_profile = not obj.profile.super_profile
            obj.profile.save()

    return HttpResponse(json.dumps({'is_super_profile': obj.profile.super_profile}), content_type='application/json')


@ login_required
def is_super_profile_api(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        obj = get_user_model().objects.get(profile__id=id)
        x = obj.profile.super_profile
    return HttpResponse(json.dumps({'is_super_profile': x}), content_type='application/json')

import os
import secrets
from PIL import Image
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from django.db.models import Q
from ckeditor_uploader.fields import RichTextUploadingField
from uuid import uuid4
from PIL import Image

####### Classes #####
"""Tags"""


class Tag(models.Model):
    tag = models.CharField(_('Tag'), max_length=200, blank=True)
    created = models.DateTimeField(_("كتب في "), auto_now_add=True)

    @property
    def count_tag(self):
        return self.tags.filter(Q(status='PUB') & Q(active=True)).count()

    def __str__(self):
        return self.tag


"""Article"""


class Article(models.Model):

    class StatusChoices(models.TextChoices):
        DRAFT = 'DRA', _('غير مكتمل')
        PUBLISH = 'PUB', _('نشر')

    # author, show_article
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='creater')
    # title, photo, article, slug
    title = models.CharField(_('العنوان'), max_length=200)
    sub_title = models.TextField(_('العنوان الفرعي'))
    body = RichTextUploadingField(_("المقال"))
    slug = models.SlugField(
        max_length=255, unique_for_date='publish', allow_unicode=True)
    picture = models.ImageField(
        _('خلفية'), default='default/default_post.jpg', upload_to='post_pics', blank=True)
    # DATE Info
    publish = models.DateTimeField(default=timezone.now, editable=False)
    created = models.DateTimeField(_("كتب في "), auto_now_add=True)
    updated = models.DateTimeField(_("عدل في"), auto_now=True)
    # Tags
    tags = models.ManyToManyField(Tag, related_name='tags', blank=True)
    status = models.CharField(_('الحالة'),
                              max_length=3, default=StatusChoices.DRAFT, choices=StatusChoices.choices)
    active = models.BooleanField(_(' مفعل'), default=True)
    likes = models.ManyToManyField(
        get_user_model(), related_name='likes', blank=True)
    saved = models.ManyToManyField(
        get_user_model(), related_name='saved', blank=True)
    total_likes_f = models.IntegerField(default=0)

    def get_absolute_url(self):
	    return reverse('post', args=[ self.id, self.status])
    @ property
    def total_likes(self):
        return self.likes.count()
    def save(self, *args, **kwargs):
        slug = slugify(self.title)
        has_slug = Article.objects.filter(slug=slug).exists()
        count = 1
        while has_slug:
            count = count + 1
            has_slug = Article.objects.filter(slug=slug).exists()
        self.slug = f'{slug}-{count}'

        super().save(*args, **kwargs)
        size = (700, 700)
        img = Image.open(self.picture.path)
        img.thumbnail(size)
        img.save(self.picture.path)

    class Meta:
        ordering = ('-created', )

    def __str__(self):
        return self.title


"""Article Comments"""


class Comment(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    article = models.ForeignKey(
        "Article", on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    comment = models.CharField(
        _('تعليق'), max_length=500, blank=False, null=False)
    created = models.DateTimeField(_("كتب في "), auto_now_add=True)
    updated = models.DateTimeField(_("عدل في"), auto_now=True)
    comment_likes = models.ManyToManyField(
        get_user_model(), blank=True, related_name='comment_likes')
    active = models.BooleanField(_(' مفعل'), default=True)

    def __str__(self):
        return f'{self.user} {self.comment}'

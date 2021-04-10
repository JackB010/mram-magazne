from django.contrib import admin
from .models import (Article, Tag, Comment)


class CommentInLines(admin.TabularInline):
    model = Comment


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):

    list_display = ('title',  'updated', 'user')
    list_filter = ('active', 'status')
    ordering = ('-updated', )
    search_fields = ('title',  'article')
    filter_horizontal = ('tags',)
    prepopulated_fields = {'slug': ('title',)}

    inlines = [
        CommentInLines,
    ]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['tag', 'created']
    search_fields = ('tag',)
    ordering = ('-created', )

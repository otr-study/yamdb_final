from django.contrib import admin

from .models import Categories, Comment, Genres, Review, Title


class GenresAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('name',)


class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('name',)


class TitlesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'year', 'description', 'category')
    search_fields = ('name', 'year', 'category',)
    list_filter = ('year',)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'title', 'text', 'pub_date')
    list_display_links = ('pk', 'author')
    search_fields = ('text',)
    list_filter = ('author',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'review', 'text', 'pub_date')
    list_display_links = ('pk', 'author')
    search_fields = ('text',)
    list_filter = ('author',)


admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Genres, GenresAdmin)
admin.site.register(Categories, CategoriesAdmin)
admin.site.register(Title, TitlesAdmin)

from django.contrib import admin
from .models import Author, Genre, Book, BookInstance, BookReview, Profile


class BookInstanceInLine(admin.TabularInline):
    model = BookInstance
    extra = 0
    can_delete = False
    readonly_fields = ('id',)


class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'summary', 'display_genre')
    inlines = [BookInstanceInLine]


class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'due_back', 'status')
    list_filter = ('due_back', 'status', )
    search_fields = ('id', 'book__title')
    fieldsets = (
        ('Bendra', {
            'fields': ('id', 'book')
        }),
        ('Prieinamumas', {
            'fields': ('due_back', 'status', 'reader')
        })
    )


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'display_books')


class BookReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'date_created', 'reviewer', 'content')


admin.site.register(BookReview, BookReviewAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Genre)
admin.site.register(Book, BookAdmin)
admin.site.register(BookInstance, BookInstanceAdmin)
admin.site.register(Profile)

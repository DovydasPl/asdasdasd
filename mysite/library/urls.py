from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('authors/', views.authors, name='authors'),
    path('authors/<int:author_id>', views.author, name='author'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('books/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('search/', views.search, name='search'),
    path('my-books/', views.TakenBooksByUserListView.as_view(), name='my-books'),
    path('my-books/<str:pk>',
         views.TakenBooksByUserDetailView.as_view(), name='my-book'),
    path('my-books/new/', views.TakenBooksByUserCreateView.as_view(),
         name='my-borrowed-new'),
    path('my-books/<str:pk>/delete/',
         views.TakenBooksByUserDeleteView.as_view(), name='my-book-delete'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
]

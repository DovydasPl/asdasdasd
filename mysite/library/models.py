from django.db import models
from django.urls import reverse
import uuid
from django.contrib.auth.models import User
from datetime import date, timedelta
from tinymce.models import HTMLField
from PIL import Image
# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profilis')
    photo = models.ImageField(
        'Profilio nuotrauka', upload_to='profile_pics', default='profile_pics/default.jpeg')
    verified_until = models.DateField(
        'Patvirtintas iki', null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.photo.path)

        if img.height > 300 or img.width > 300:
            img.thumbnail((300, 300))
            img.save(self.photo.path)

    def is_overdue(self):
        if self.verified_until and date.today() + timedelta(days=30) > self.verified_until:
            return True
        return False

    def days_remaining(self):
        skirtumas = self.verified_until - date.today()
        return skirtumas.days


class Genre(models.Model):
    name = models.CharField('Pavadinimas', max_length=200,
                            help_text='Įveskite knygos žanrą (pvz. detektyvas)')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Žanras'
        verbose_name_plural = 'Žanrai'


class Book(models.Model):
    """Modelis reprezentuoja knygą (bet ne specifinę knygos kopiją)"""
    title = models.CharField('Pavadinimas', max_length=200)
    author = models.ForeignKey(
        'Author', on_delete=models.SET_NULL, null=True, related_name='books')
    summary = models.TextField(
        'Aprašymas', max_length=1000, help_text='Trumpas knygos aprašymas')
    isbn = models.CharField(
        'ISBN', max_length=13, help_text='13 Simbolių <a href="https://www.isbn-international.org/content/what-isbn">ISBN kodas</a>')
    genre = models.ManyToManyField(
        Genre, help_text='Išrinkite žanrą(us) šiai knygai')
    cover_image = models.ImageField(
        'Virselis', upload_to='covers', null=True, blank=True)

    def __str__(self):
        return self.title

    def display_genre(self):
        sarasas = [genre.name for genre in self.genre.all()]
        return ', '.join(sarasas)

    class Meta:
        verbose_name = 'Knyga'
        verbose_name_plural = 'Knygos'


class BookInstance(models.Model):
    """Modelis, aprašantis konkrečios knygos kopijos būseną"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text='Unikalus ID knygos kopijai')
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    due_back = models.DateField('Bus prieinama', null=True, blank=True)
    reader = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL)

    LOAN_STATUS = (
        ('a', 'Administruojama'),
        ('p', 'Paimta'),
        ('g', 'Galima paimti'),
        ('r', 'Rezervuota')
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='a',
        help_text='Statusas',
    )

    class Meta:
        ordering = ['due_back']
        verbose_name = 'Knygos ID'
        verbose_name_plural = 'Knygų ID'

    def __str__(self):
        return f'{self.id} ({self.book.title})'

    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False


class Author(models.Model):
    """Model representing an author."""
    first_name = models.CharField('Vardas', max_length=100)
    last_name = models.CharField('Pavardė', max_length=100)
    description = HTMLField()

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.last_name} {self.first_name}'

    def display_books(self):
        sarasas = [book.title for book in self.books.all()]
        return ', '.join(sarasas)

    class Meta:
        verbose_name = 'Autorius'
        verbose_name_plural = 'Autoriai'


class BookReview(models.Model):
    book = models.ForeignKey(
        'Book', on_delete=models.SET_NULL, null=True, blank=True)
    reviewer = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    content = models.TextField('Review', max_length=2000)

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = 'Reviews'
        ordering = ['-date_created']

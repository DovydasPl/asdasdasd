# Generated by Django 4.2.4 on 2023-09-01 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0005_book_cover_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='cover_image',
            field=models.ImageField(null=True, upload_to='library/covers', verbose_name='Cover image'),
        ),
    ]

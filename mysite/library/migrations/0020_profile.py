# Generated by Django 4.2.4 on 2023-09-07 15:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('library', '0019_delete_profile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(default='profile_pics/default.jpeg', upload_to='profile_pics', verbose_name='Profilio nuotrauka')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profilis', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
# Generated by Django 2.0.7 on 2018-09-20 15:26

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mediaportalapp', '0004_comments'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='users_reaction',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]

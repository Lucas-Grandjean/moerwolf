# Generated by Django 4.0.3 on 2022-04-06 21:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='guarded',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='healed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='wolf_votes',
            field=models.IntegerField(default=0),
        ),
    ]

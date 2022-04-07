from django.db import models

class Card(models.Model):
    side_choices = [
        ('GOOD', 'Gentil'),
        ('EVIL', 'Mechant'),
        ('NEUTRAL', 'Neutre'),
    ]
    name = models.CharField(max_length=30)
    description = models.TextField()
    img = models.ImageField(upload_to='cards/')
    side = models.CharField(max_length=32,choices=side_choices,)
    unique = models.BooleanField(default=False)

    class Meta:
        ordering = ['side']

    def __str__(self):
        return self.name


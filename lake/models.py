from django.db import models
from django.contrib.auth import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    bio = models.TextField(blank=True, null=True, max_length=500)
    profile_picture = models.ImageField(upload_to="profiles/")
    cover_photo = models.ImageField(upload_to='covers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class Post(models.Model): # on crée une table appélé Post , models.model django sait que c'est une table

    # dans le modèle Post,
    # je crée une ForeignKey author qui relie chaque post à un utilisateur CustomUser pour identifier l'auteur.
    author = models.Foreign_key(CustomUser,on_delete=models.CASCADE, related_name='posts')

    caption = models.TextField(blank=True, max_length=2000)
    image = models.ImageField(upload_to='posts/')
    video = models.FileField(upload_to='videos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

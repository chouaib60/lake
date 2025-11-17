import self
from django.db import models
from django.contrib.auth import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    bio = models.TextField(blank=True, null=True, max_length=500)
    profile_picture = models.ImageField(upload_to="profiles/")
    cover_photo = models.ImageField(upload_to='covers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    following_count = models.IntegerField(default=0)
    followers_count = models.IntegerField(default=0)



    def __str__(self): # pour affichage humain
        return self.username



class Post(models.Model): # on crée une table appélé Post , models.model django sait que c'est une table

    # dans le modèle Post,
    # je crée une ForeignKey author qui relie chaque post à un utilisateur CustomUser pour identifier l'auteur.
    author = models.Foreign_key(CustomUser,on_delete=models.CASCADE, related_name='posts')

    caption = models.TextField(blank=True, max_length=2000)
    image = models.ImageField(upload_to='posts/')
    video = models.FileField(upload_to='videos/', blank=True, null=True)
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) # auto_now = true : la date du post se remplit automatiquement

    # class de métadonnées = des informations sur le modèle ,
    # c'est une classe imbriqué qui dit à Django comment se comporter
    class Meta :

        # ordering : c'est dans quel ordre afficher les postes ,
        # ici j'ai choisi par date de création
        ordering = ['-created_at']

class Follow(models.Model):
    # les username des followers et followings sont définie dans custumuser et je les relie avec leur clé étrangere à la table follower
    follower = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True) # auto_now_add = true : la date du follow se remplit automatiquement


    class Meta :
  # cette combinaison de champs doit etre u,ique , ca veut dire qu'un utilisateur
  # ne peut suivre qu'une seule fois le meme utilisateur
        unique_together = ['follower','following']


     def __str__(self):
         return f"{self.follower.username} follows {self.following.username}"

class Like(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='liked_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'post']
        indexes = [
            models.Index(fields=['post']),
        ]

    def __str__(self):
        return f"{self.user.username} likes {self.post.id}"

class Comment(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(max_length = 5000)
    like_counts = models.IntegerField(default = 0)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now_add = True)

    class Meta :
        ordering = ['-created_at']


class Comment(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(max_length=500)
    likes_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post']),
        ]

    def __str__(self):
        return f"Comment by {self.author.username} on post {self.post.id}"


class CommentLike(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='liked_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'comment']

    def __str__(self):
        return f"{self.user.username} likes comment {self.comment.id}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='sent_notifications'
    )
    notification_type = models.CharField(
        max_length=10,
        choices=NOTIFICATION_TYPES
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username} from {self.sender.username}"












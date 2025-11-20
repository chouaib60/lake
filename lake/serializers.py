from django.contrib.auth import authenticate
from django.db.models.fields import return_None
from django.template.defaulttags import comment
from rest_framework import serializers
from .models import CustomUser, Post, Like, Comment, Follow, CommentLike, Notification
# . signifie du meme dossier

# ============================================
# 1. SERIALIZERS POUR L'AUTHENTIFICATION
# ============================================
# serializer pour permettre aux utilisateurs de créer un compte
# 1. il valide que tous les mot des passes sont corrects (Hash)
# 2. il enregistre le compte de l'utilisateur dans la BD
# 3. il retourne les données de l'utilisateur crée.

class Authentification(serializers.ModelSerializer): # serializers.ModelSerializer  générer automatiquement les champs de notre modèle au lieu d'écrire tous les composants manuellement

# champ password qui n'existe qu'en mode écriture
    password = serializers.CharField(
        # le client envoie le password , mais on ne le retourne pas
       read_only=True,
       min_length=8,
        style={'input_type' : 'password'}
    )
# l'utilisateur doit valider le mot de passe
    password2 = serializers.CharField(
        write_only=True,
        style={'input_type' : 'password'}
    )
    class Meta:
        model = CustomUser # lemodèle qu'on va sérialiser
        # liste des champs à inclure dans la sérialisation
        fields = ['id','username', 'email', 'password', 'password2', 'first_name', 'last_name']
        # champs qui ne peuvent pas etre modifiés via Api
        read_only_fields = ['id']

# vérification des données
     # : on vérifie que les mots de passes se correspondent

    def validate(self,data):
# lorsque le client envoie une requete {
#     "username": "alice",
#     "email": "alice@example.com",
#     "password": "SecurePass123",
#     "password2": "SecurePass123"
# }  Django crée automatiquement un dictionnaire data qui va contenir ces données

        if data['password'] != data['password2']:
            raise serializers.ValidationError(
                {"password" : "les mots de passes ne se correspondent pas"}
            )
        return data # data c'est la sortie sérialisé

    # après validation des données , on va créer l'objet (le compte) dans la BD
    def create(self, validated_data):
        # on récupère les données validées
       password = validated_data.pop('password')
       password2 = validated_data.pop('password2')

        # on crée l'utilisateur avec la méthode create_user() (prédéfini) , elle hash le mot de passe (elle protège le mot de passe en le transformant en chaine de caractères aléatoires

       user = CustomUser.objects.create_user(
           password = password ,
           ** validated_data # validated_data contient username, email, first_name, last_name
       )
       return user

    ## Serializer pour se connecter (le login) : permet au cient de se connecteur avec username et password

class Login(serializers.Serializer):
    # username du client
    username = serializers.CharField() # cette ligne crée un champ de sérialisation de type char nommé username
    # password du client
    password = serializers.CharField( # meme chose mais avec 2 validation
        write_only=True,
        style={'input_type':'password'}
    )
# on valide que le username te le password sont correctes

    def validate(self, data):
        # on essaye d'authentifier l'utilisateur
        user = authenticate(
            username = data.get('username'),
            password = data.get('password')
        )

    # si l'authentification échoue
        if not user :
           raise serializers.ValidationError(
            "les identifiants sont incorrectes."
        )

    # on stocke l'utilisateur si c'est valide
        data['user'] = user
        return data
        # data devient
        # data = {
        # 'username': 'john',
        # 'password': 'secret123',
        # 'user': <User: john>  # Objet Django User
#}


# ============================================
# 2. SERIALIZERS POUR LES UTILISATEURS
# ===============================================

# serializer pour afficher les infos de l'utilisateur
# role c'est convertir les données d'un utilisateur en JSon
class UserSerializer(serializers.ModelSerializer):
    # je veux calculer le nombre de follower
    # SerializerMethodField est un champ de sérialiseur qui permet de calculer une valeur dynamiquement via une méthode python
    followers_count = serializers.SerializerMethodField()

    # le nombre de follower que l'utilisateur suit
    following_count = serializers.SerializerMethodField()

    # is_following : est ce que l'utilisateur suit celui ci
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id',
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'profile_picture',
            'cover_photo',
            'followers_count',
            'following_count',
            'is_following',
            'created_at']
        read_only_fields = ['id', 'created_at', 'followers_count', 'following_count', 'is_following']

        # la méthode qu'on va définir pour calculer le nombre de followers
        def get_followers_count(self, obj): # obj : c'est l'objet 'user' qu'on sérialise on a défini user précedemment avec user = CustomUser.objects.create_user(
            return obj.followers.all().count() # elle doit retourner une valeur

        def get_following_count(self, obj):

            return obj.following.all().count()

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    like_counts = serializers.SerializerMethodField()
    user_liked = serializers.SerializerMethodField()

    class Meta:
        model= comment
        fields = ['id', 'author', 'text', 'likes_count', 'user_liked',
        'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'likes_count']

        def get_likes_count(self,obj): # compte le nombre de likes du commentaire
            return obj.liked_by.count()


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True) # le role de many c'est affiche tous les commentaires de manière imbriqués
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    user_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'caption', 'image', 'video', 'likes_count',
                  'comments_count', 'comments', 'user_liked', 'created_at']
        read_only_fields = ['id', 'created_at', 'likes_count', 'comments_count']

    def get_likes_count(self, obj):
        return obj.liked_by.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_user_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.liked_by.filter(user=request.user).exists()
        return False


class FollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['id', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    post = PostSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'sender', 'notification_type', 'post',
            'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
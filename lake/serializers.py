from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import CustomUser, Post, Like, Comment, Follow, CommentLike, Notification

# ============================================
# 1. SERIALIZERS POUR L'AUTHENTIFICATION

# serializer pour permettre aux utilisateurs de créer un compte
# 1. il valide que tous les mot des passes sont corrects (Hash)
# 2. il enregistre le compte de l'utilisateur dans la BD
# 3. il retourne les données de l'utilisateur crée.

class Authentification(serializers.ModelSerializer):

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
        model = CustomUser
        # champs utilisés pour l'enregistrement
        fields = ['id','username', 'email', 'password', 'password2', 'first_name', 'last_name']
        # le client peut recevoir l'id' mais il peut pas le modifier c'est comme du read-only , i'id est crée automatiquement
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
        return data

    # après validation des données , on va créer l'objet (le compte) dans la BD
    def create(self, validated_data):
        # on récupère les données validées
       password = validated_data.pop('password')
       password2 = validated_data.pop('password2')

        # on crée l'utilisateur avec la méthode create_user() (prédéfini) , elle hash le mot de passe (elle protège le mot de passe en le transformant en chaine de caractères aléatoires

       user = CustomUser.objects.create_user(
           password = password ,

       )



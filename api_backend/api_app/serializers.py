from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from rest_framework.serializers import (
    EmailField,
    CharField,
    ModelSerializer,
    SerializerMethodField,
    ValidationError,
)
from .models import User, Viewer, Role, Camera

#User= get_user_model()



#register user
class UserCreateSerializer(ModelSerializer):
    email = EmailField(label = 'Email Address')
    #email2 = EmailField(label='Confirm Email')

    class Meta:
        model = User
        fields = [
            'username', 
            'email',
            #'email2', 
            'password',
            # 'role',
            ]
        extra_kwargs = {"password": {"write_only": True}}
        #write_only = 'password'
        #fields='__all__'

    # def validated_email(self, value):
    #     data = self
    #     email1 = data["email"]
    #     email2 = data.get["email2"]
    #     if email1 != email2:
    #         raise ValidationError("Emails must match")
    #     return value

    def create(self, validated_data):
        email = validated_data['email']
        username = validated_data['username']
        password = validated_data['password']
        # role = validated_data['role']
        user_obj = User(
                email = email,
                username = username,
               # role = role,
               # password_hash=password_hash
            )
        user_obj.set_password(password)
        user_obj.save()
        return validated_data

#login serializer


class UserLoginSerializer(ModelSerializer):
    token = CharField(allow_blank=True, read_only=True)
    dropbox_token = CharField(allow_blank=True, read_only=True)

    username = CharField(required=False, allow_blank=True)
    email = EmailField(label= 'Email Address', required=False, allow_blank=True)
    first_name = CharField(read_only=True, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'email', 
            'username', 
            'password',
            'first_name',
            'token',
            'dropbox_token',
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        user_obj = None
        email = data.get("email",None)
        username = data.get("username", None)
        password = data["password"]
        if not email and not username:
            raise ValidationError("A username or email is required to login")

        user = User.objects.filter(
            Q(email=email) |
            Q(username=username)
        ).distinct()

        if user.exists() and user.count() == 1:
            user_obj = user.first()
        else:
            raise ValidationError("This username/email is not valid.")

        if user_obj:
            if not user_obj.check_password(password):
                raise ValidationError("Incorrect credential")

        data["token"] = "Some token"
        data["first_name"] = user_obj.get_full_name()
        data["dropbox_token"] = user_obj.dropbox_token
        return data


class UserProfileSerializer(ModelSerializer):
  class Meta:
        model = User
        fields = [
            'first_name', 
            'last_name',  
            ]
  def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name',instance.last_name)
        instance.save()
        return instance


class CameraSerializer(ModelSerializer):
    class Meta:
        model= Camera
        fields='__all__'


class ViewerSerializer(ModelSerializer):

    class Meta:
        model= Viewer
        fields=[
            'master',
            'viewer']
        #fields='__all__'


class RoleSerializer(ModelSerializer):

    class Meta:
        model= Role
        fields='__all__'
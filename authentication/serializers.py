from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from authentication.models import User
from filemanager import models as file_models


class GenericRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class ResetPassSerializer(GenericRequestSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)


class CreateUserSerializer(serializers.Serializer):
    full_name = serializers.CharField(required=True)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())])
    phone_number = serializers.CharField(
        required=True, max_length=10, min_length=10,
        validators=[RegexValidator(r'^\d{0,10}$', 'Kindly add valid phone number')],
        error_messages={
            "invalid": "Kindly add valid number",
            "min_length": "Should be at least 10 numbers",
            "max_length": "Should be at most 10 numbers",
        })
    user_type = serializers.CharField(allow_null=True, allow_blank=True)


class RegisterSerializer(CreateUserSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    profile_photo = serializers.CharField(allow_null=True, allow_blank=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            user_type = validated_data['user_type']
            user = User.objects.create_user(
                password=validated_data['password'],
                email=validated_data['email'],
                is_staff=False
            )
            user.full_name = validated_data['full_name']
            user.phone_number = validated_data['phone_number']
            user.profile_photo = validated_data['profile_photo']
            user.is_active = True
            user.enable_phone_notification = True
            user.enable_email_notification = True
            user.save()
            if user_type:
                # fetch details of the group selected
                try:
                    group_instance = Group.objects.get(name=user_type)
                except Exception as e:
                    print(e)
                    transaction.set_rollback(True)
                    raise serializers.ValidationError("Group does not exist")
                user.groups.add(group_instance)

        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)

        # Add custom claims
        token['email'] = user.email
        token['names'] = user.full_name
        token['phone_number'] = user.phone_number
        token['role'] = user.primary_role
        return token


class GroupSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()


class ListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'full_name',
            'phone_number',
            'account_status',
            'date_registered',
        ]


class UserSerializer(ListUserSerializer):
    roles = serializers.SerializerMethodField('get_user_roles')
    profile_photo = serializers.SerializerMethodField('get_profile_photo')

    class Meta:
        model = User
        fields = ListUserSerializer.Meta.fields + [
            'is_active', 'usertype', 'roles',
            'profile_photo', 'enable_phone_notification',
            'enable_email_notification', 'date_registered',
        ]

    def get_user_roles(self, obj):
        all_roles = obj.groups.all()
        records = GroupSerializer(all_roles, many=True)
        return records.data

    def get_profile_photo(self, obj):
        try:
            request = self.context.get('request')
            profile = obj.profile_photo
            profile_inst = file_models.Poster.objects.get(id=profile)
            url = request.build_absolute_uri(profile_inst.poster.url)
            return url
        except Exception as e:
            print(e)
            return None
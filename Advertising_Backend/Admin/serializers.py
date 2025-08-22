from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Category, SubCategory, ImageUpload, Subscription, YoutubeVideo

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'email', 'is_active', 'is_staff', 'profile_image', 'logo']


class EditUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'email', 'is_active', 'is_staff', 'profile_image', 'logo']
       

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    is_staff = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = ['username', 'phone', 'email', 'password', 'is_staff', 'profile_image', 'logo']

    def create(self, validated_data):
        is_staff = validated_data.pop('is_staff', False)

        # Extract image fields if provided
        profile_image = validated_data.pop('profile_image', None)
        logo = validated_data.pop('logo', None)

        # Create user
        user = User.objects.create_user(
            username=validated_data['username'],
            phone=validated_data.get('phone'),
            email=validated_data.get('email'),
            password=validated_data['password'],
        )

        # Assign optional fields
        user.is_staff = is_staff
        if profile_image:
            user.profile_image = profile_image
        if logo:
            user.logo = logo

        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()  # Can be username, email, or phone
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data.get('identifier')
        password = data.get('password')

        # Allow login via username, email, or phone
        user = None
        if '@' in identifier:  # likely email
            user = User.objects.filter(email=identifier).first()
        elif identifier.isdigit():  # likely phone
            user = User.objects.filter(phone=identifier).first()
        else:  # fallback to username
            user = User.objects.filter(username=identifier).first()

        if user and user.check_password(password):
            if not user.is_active:
                raise serializers.ValidationError("User is inactive")
            data['user'] = user
            return data

        raise serializers.ValidationError("Invalid credentials")

#---------------------------------------------------


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'


class ImageUploadSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)

    class Meta:
        model = ImageUpload
        fields = '__all__'
        
#---------------------------------------------------
class YoutubeVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = YoutubeVideo
        fields = "__all__"


# class SubscriptionSerializer(serializers.ModelSerializer):
#     user = serializers.StringRelatedField(read_only=True)  # show username
#     user_id = serializers.PrimaryKeyRelatedField(
#         queryset=Subscription._meta.get_field("user").related_model.objects.all(),
#         source="user",
#         write_only=True
#     )

#     class Meta:
#         model = Subscription
#         fields = ['id', 'user', 'user_id', 'plan', 'start_date', 'end_date', 'is_active']
#         read_only_fields = ['start_date', 'end_date', 'is_active']


from rest_framework import serializers
from .models import Subscription

# class SubscriptionSerializer(serializers.ModelSerializer):
#     user = serializers.StringRelatedField(read_only=True)  # show username
#     user_id = serializers.PrimaryKeyRelatedField(
#         queryset=Subscription._meta.get_field("user").related_model.objects.all(),
#         source="user",
#         write_only=True
#     )

#     # Add is_active as a computed field
#     is_active = serializers.SerializerMethodField()

#     class Meta:
#         model = Subscription
#         fields = ['id', 'user', 'user_id', 'plan', 'start_date', 'end_date', 'is_active','revoke']
#         read_only_fields = ['start_date','is_active']

#     def get_is_active(self, obj):
#         return obj.is_active  # uses the @property in the model
class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # show username
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=Subscription._meta.get_field("user").related_model.objects.all(),
        source="user",
        write_only=True
    )

    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ['id', 'user', 'user_id', 'plan', 'start_date', 'end_date', 'is_active', 'revoke']
        read_only_fields = ['start_date', 'is_active']

    def get_is_active(self, obj):
        return obj.is_active

    def validate(self, data):
        revoke = data.get('revoke', False)

        # If revoking, ignore plan
        if revoke:
            data['plan'] = None
        else:
            if not data.get('plan') and not self.instance:
                raise serializers.ValidationError(
                    {"plan": "Plan is required unless subscription is revoked."}
                )
        return data

    def update(self, instance, validated_data):
        # If revoke is True, wipe out plan + dates
        if validated_data.get('revoke') is True:
            instance.plan = None
            instance.start_date = None
            instance.end_date = None
        else:
            # Otherwise normal update
            instance.plan = validated_data.get('plan', instance.plan)
            instance.start_date = validated_data.get('start_date', instance.start_date)
            instance.end_date = validated_data.get('end_date', instance.end_date)

        instance.revoke = validated_data.get('revoke', instance.revoke)
        instance.save()
        return instance

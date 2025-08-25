
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Category, CustomUser, SubCategory, ImageUpload, Subscription, YoutubeVideo,Carousel

User = get_user_model()


# -------------------- Subscription --------------------
class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # show username
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=Subscription._meta.get_field("user").related_model.objects.all(),
        source="user",
        write_only=True
    )

    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_phone = serializers.CharField(source="user.phone", read_only=True)

    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'user_id', "user_email", "user_phone",
            'plan', 'start_date', 'end_date', 'is_active', 'revoke'
        ]
        read_only_fields = ['start_date', 'is_active', 'user_email', 'user_phone']

    def get_is_active(self, obj):
        return obj.is_active

    def validate(self, data):
        revoke = data.get('revoke', False)
        if revoke:
            data['plan'] = None
        else:
            if not data.get('plan') and not self.instance:
                raise serializers.ValidationError(
                    {"plan": "Plan is required unless subscription is revoked."}
                )
        return data

    def update(self, instance, validated_data):
        if validated_data.get('revoke') is True:
            instance.plan = None
            instance.start_date = None
            instance.end_date = None
        else:
            instance.plan = validated_data.get('plan', instance.plan)
            instance.start_date = validated_data.get('start_date', instance.start_date)
            instance.end_date = validated_data.get('end_date', instance.end_date)

        instance.revoke = validated_data.get('revoke', instance.revoke)
        instance.save()
        return instance


# -------------------- User --------------------
class UserSerializer(serializers.ModelSerializer):
    subscriptions = SubscriptionSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'phone', 'email',
            'is_active', 'is_staff', 'profile_image', 'logo',
            "subscriptions"
        ]


class EditUserSerializer(serializers.ModelSerializer):
    subscription = SubscriptionSerializer(read_only=True, source='subscriptions')  # read-only

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'phone', 'email',
            'is_active', 'is_staff', 'profile_image', 'logo',
            'subscription'  # include subscription info
        ]



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    is_staff = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = ['username', 'phone', 'email', 'password', 'is_staff', 'profile_image', 'logo']

    def create(self, validated_data):
        is_staff = validated_data.pop('is_staff', False)
        profile_image = validated_data.pop('profile_image', None)
        logo = validated_data.pop('logo', None)

        user = User.objects.create_user(
            username=validated_data['username'],
            phone=validated_data.get('phone'),
            email=validated_data.get('email'),
            password=validated_data['password'],
        )
        user.is_staff = is_staff
        if profile_image:
            user.profile_image = profile_image
        if logo:
            user.logo = logo
        user.save()
        return user
  

class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data.get('identifier')
        password = data.get('password')

        user = None
        if '@' in identifier:
            user = User.objects.filter(email=identifier).first()
        elif identifier.isdigit():
            user = User.objects.filter(phone=identifier).first()
        else:
            user = User.objects.filter(username=identifier).first()

        if user and user.check_password(password):
            if not user.is_active:
                raise serializers.ValidationError("User is inactive")
            data['user'] = user
            return data

        raise serializers.ValidationError("Invalid credentials")





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


class CarouselSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carousel
        fields = ["id", "image1", "image2", "image3", "image4"]

    def update(self, instance, validated_data):
        for field in ["image1", "image2", "image3", "image4"]:
            if field in validated_data:
                # Update only if new value is provided
                setattr(instance, field, validated_data[field])
        instance.save()
        return instance
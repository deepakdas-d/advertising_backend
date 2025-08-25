from datetime import date, timedelta
from django.conf import settings



from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

def user_profile_image_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/profile_images/<username>/<filename>
    return f'profile_images/{instance.username}/{filename}'

def user_logo_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_logos/<username>/<filename>
    return f'user_logos/{instance.username}/{filename}'

def carousel_image_path(instance, filename):
    return f"carousel/{filename}"


class CustomUserManager(BaseUserManager):
    def create_user(self, username, phone, email, password=None, **extra_fields):
        if not email and not phone:
            raise ValueError("Either email or phone number is required")

        if email:
            email = self.normalize_email(email)

        user = self.model(username=username, phone=phone, email=email, **extra_fields)
        user.set_password(password)  # Hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, username, phone, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, phone, email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    profile_image = models.ImageField(upload_to=user_profile_image_path, null=True, blank=True)
    logo = models.ImageField(upload_to=user_logo_path, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["phone", "email"]

    def __str__(self):
        return self.username


#-----------------------------------------------------------



class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, related_name="subcategories", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('category', 'name')

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class ImageUpload(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='images',null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"Image {self.id}"


#-----------------------------------------------------------

class YoutubeVideo(models.Model):
    CATEGORY_CHOICES = [
        ("Education", "Education"),
        ("Entertainment", "Entertainment"),
        ("Music", "Music"),
        ("Sports", "Sports"),
        ("Technology", "Technology"),
        ("Lifestyle", "Lifestyle"),
    ]

    video_url = models.URLField(max_length=500)
    video_name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.video_name


# ------------------ Subscriptions -------------------

from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

class Subscription(models.Model):
    PLAN_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES,null=True, blank=True)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(blank=True, null=True)
    revoke=models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.revoke:
            self.plan = None

        if not self.start_date:
            self.start_date = timezone.now().date()

        if not self.end_date:
            if self.plan == 'monthly':
                self.end_date = self.start_date + timedelta(days=30)
            elif self.plan == 'yearly':
                self.end_date = self.start_date + timedelta(days=365)

        super().save(*args, **kwargs)

    @property
    def is_active(self):
        """Dynamically check if subscription is valid."""
        if not self.end_date or not self.plan or self.revoke:
            return False
        return self.end_date >= timezone.now().date()

    def __str__(self):
        return f"{self.user.username} - {self.plan}"



# ------------------------------------------------------

class Carousel(models.Model):
    image1 = models.ImageField(upload_to=carousel_image_path, blank=True, null=True)
    image2 = models.ImageField(upload_to=carousel_image_path, blank=True, null=True)
    image3 = models.ImageField(upload_to=carousel_image_path, blank=True, null=True)
    image4 = models.ImageField(upload_to=carousel_image_path, blank=True, null=True)

    def add_image(self, new_image):

        if not self.image1:
            self.image1 = new_image
        elif not self.image2:
            self.image2 = new_image
        elif not self.image3:
            self.image3 = new_image
        elif not self.image4:
            self.image4 = new_image
        else:
            # shift images: drop oldest (image1) and move others left
            self.image1.delete(save=False)  # delete old file
            self.image1, self.image2, self.image3 = self.image2, self.image3, self.image4
            self.image4 = new_image
        self.save()

    def __str__(self):
        return "Carousel"

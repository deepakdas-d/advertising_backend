from django.shortcuts import render


# Create your views here.
from .models import Category, SubCategory, ImageUpload, YoutubeVideo, Carousel
from .serializers import CategorySerializer, EditUserSerializer, SubCategorySerializer, ImageUploadSerializer, \
    YoutubeVideoSerializer, CarouselSerializer
from rest_framework.parsers import MultiPartParser, FormParser,JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import generics, status, permissions, viewsets
from rest_framework.views import APIView
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework import generics, permissions
from .models import Subscription
from .serializers import SubscriptionSerializer
from django.contrib.auth import get_user_model

User=get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        })

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['username', 'email', 'phone','id']
    permission_classes =  [AllowAny]


class EditUserByIdView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = EditUserSerializer
    # permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser,JSONParser]

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  #  important for file upload

    def get(self, request):
        user = request.user
        serializer = EditUserSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        serializer = EditUserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        user = request.user
        serializer = EditUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# -----------------------------------------------------------


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SubCategoryListCreateView(generics.ListCreateAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer

class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SubCategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer


#-----------------------------------------------------------------------

class ImageUploadView(generics.ListCreateAPIView):
    # permission_classes = [IsAuthenticated]
    queryset = ImageUpload.objects.all()
    serializer_class = ImageUploadSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category','subcategory','id','user']
    

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ImageUploadDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ImageUpload.objects.all()
    serializer_class = ImageUploadSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]


    def update(self, request, *args, **kwargs):
        kwargs['partial'] = request.method.lower() == 'patch'  # allow partial updates
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)



#-----------------------------------------------------------------------


class YoutubeVideoListCreateView(generics.ListCreateAPIView):
    queryset = YoutubeVideo.objects.all()
    serializer_class = YoutubeVideoSerializer


# Retrieve, update, or delete a single video
class YoutubeVideoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = YoutubeVideo.objects.all()
    serializer_class = YoutubeVideoSerializer




class SubscriptionListCreateView(generics.ListCreateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()    # respects user_id from request data
  # triggers model save logic to set end_date & is_active


class SubscriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:  
            # staff/admin can update any subscription
            return Subscription.objects.all()
        return Subscription.objects.filter(user=user)





class CarouselListCreateView(generics.ListCreateAPIView):
    queryset = Carousel.objects.all()
    serializer_class = CarouselSerializer
    parser_classes = [MultiPartParser, FormParser]

# Retrieve, update, or delete a single carousel entry
class CarouselDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Carousel.objects.all()
    serializer_class = CarouselSerializer
    parser_classes = [MultiPartParser, FormParser]
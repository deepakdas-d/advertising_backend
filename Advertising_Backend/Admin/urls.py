from django.urls import path
from .views import CategoryRetrieveUpdateDestroyView, EditUserByIdView, RegisterView, LoginView, \
    SubCategoryRetrieveUpdateDestroyView, SubscriptionDetailView, SubscriptionListCreateView, UserList, UserProfileView, \
    YoutubeVideoDetailView, YoutubeVideoListCreateView, CarouselListCreateView, CarouselDetailView

from .views import CategoryListCreateView, SubCategoryListCreateView, ImageUploadView,ImageUploadDeleteView


urlpatterns = [
    
    path('signup/', RegisterView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('users/',UserList.as_view(),name='users'),
     path('edit-user/<int:pk>/', EditUserByIdView.as_view(), name='edit-user-by-id'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),


     path('categories/', CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryRetrieveUpdateDestroyView.as_view(), name='category-detail'),

    path('subcategories/', SubCategoryListCreateView.as_view(), name='subcategory-list'),
    path('subcategories/<int:pk>/', SubCategoryRetrieveUpdateDestroyView.as_view(), name='subcategory-detail'),

    path('images/', ImageUploadView.as_view(), name='image-upload'),
    path('images/<int:pk>/', ImageUploadDeleteView.as_view(), name='image-delete'),

    path('videos/', YoutubeVideoListCreateView.as_view(), name='video-list-create'),
    path('videos/<int:pk>/', YoutubeVideoDetailView.as_view(), name='video-detail'),

    path('carousels/', CarouselListCreateView.as_view(), name='carousel-list-create'),
    path('carousels/<int:pk>/', CarouselDetailView.as_view(), name='carousel-detail'),
    path('subscriptions/', SubscriptionListCreateView.as_view(), name='subscription-list-create'),
    path('subscriptions/<int:pk>/', SubscriptionDetailView.as_view(), name='subscription-detail'),

]
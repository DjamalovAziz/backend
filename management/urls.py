from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import SignupView, MeView, SignoutView, CustomTokenObtainPairView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('signin/', CustomTokenObtainPairView.as_view(), name='signin'),
    path('signout/', SignoutView.as_view(), name='signout'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', MeView.as_view(), name='me'),
]
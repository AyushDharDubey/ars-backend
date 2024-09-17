from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    SignupAPIView,
    AccountActivateView,
    ResetPasswordView,
    ChangePasswordView,
    LogoutView,
    LoginView,
    Oauth2ChanneliView
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('signup/', SignupAPIView.as_view(), name='signup'),
    path('activate_account/', AccountActivateView.as_view(), name='activate-account'),
    path('reset_password/', ResetPasswordView.as_view(), name='reset-password'),
    path('change_password/', ChangePasswordView.as_view(), name='change-password'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('oauth2/channeli/callback/', Oauth2ChanneliView.as_view(), name='oauth2-channeli-callback'),
]

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    SignupAPIView,
    ResetPasswordView,
    ChangePasswordView,
    LogoutView,
    LoginView,
    OauthChanneliView,
    ProfileView,
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('signup/', SignupAPIView.as_view(), name='signup'),
    path('reset_password/', ResetPasswordView.as_view(), name='reset-password'),
    path('change_password/', ChangePasswordView.as_view(), name='change-password'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('oauth/channeli/callback/', OauthChanneliView.as_view(), name='oauth-channeli-callback'),
    path('profile/', ProfileView.as_view(), name='who-am-i'),
]

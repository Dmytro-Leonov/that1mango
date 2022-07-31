from django.urls import path
from .views import (
    UserDetail, UserCreate, MyTokenObtainPairView, ChangePasswordView, VerifyRegistrationView,
    SendPasswordResetEmailView, PasswordResetView, UserFullInfo, DeleteProfilePic, UserSearchView,
    UserUpdate, UserDelete
)
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

app_name = "users"

urlpatterns = [
    path("register/", UserCreate.as_view(), name="createUser"),
    path("register/verify/", VerifyRegistrationView.as_view(), name="verifyRegistration"),
    path("send-password-reset-email/", SendPasswordResetEmailView.as_view(), name="sendResetPasswordEmail"),
    path("password-reset/", PasswordResetView.as_view(), name="resetPassword"),

    path("login/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("change-password/", ChangePasswordView.as_view(), name="changePassword"),

    path("user/<str:username>/", UserFullInfo.as_view(), name="userRetrieveDestroy"),
    path("user/update/<int:id>/", UserUpdate.as_view(), name="userUpdate"),
    path("user/delete/<int:id>/", UserDelete.as_view(), name="userDelete"),
    path("user/search/<str:username>/", UserSearchView.as_view(), name="userSearch"),
    path("user/delete-profile-pic/<int:id>/", DeleteProfilePic.as_view(), name="userDestroyPicture"),
    path("<int:id>/", UserDetail.as_view(), name="userRetrieve"),
]

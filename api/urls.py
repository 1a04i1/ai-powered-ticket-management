from django.urls import path
from api.views import GoogleLoginView

urlpatterns = [
    path(
        'auth/google/',
        GoogleLoginView.as_view(),
        name='google-login'
    ),
]
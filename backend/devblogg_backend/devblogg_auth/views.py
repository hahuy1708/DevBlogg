# devblogg_auth/views.py
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings

from .oauth_client import DjRestAuthOAuth2Client

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = f"{settings.FRONTEND_URL}/auth/callback"
    client_class = DjRestAuthOAuth2Client

class GitHubLogin(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    callback_url = f"{settings.FRONTEND_URL}/auth/callback"
    client_class = DjRestAuthOAuth2Client
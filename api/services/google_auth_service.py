from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction

from google.auth.transport import requests
from google.oauth2 import id_token

from api.models import SocialAccount


class GoogleAuthError(Exception):
    pass


@transaction.atomic
def authenticate_google_user(token):
    try:
        id_info = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )

    except ValueError:
        raise GoogleAuthError("Invalid Google ID token.")

    except Exception:
        raise GoogleAuthError("Unable to verify Google token.")

    email = id_info.get("email")
    google_id = id_info.get("sub")
    email_verified = id_info.get("email_verified", False)

    if not email or not google_id:
        raise GoogleAuthError("Google account information is incomplete.")

    if not email_verified:
        raise GoogleAuthError("Google email is not verified.")

    social_account = SocialAccount.objects.select_related(
        "user"
    ).filter(
        provider="google",
        provider_user_id=google_id
    ).first()

    if social_account:
        return social_account.user, False

    existing_user = User.objects.filter(email__iexact=email).first()

    if existing_user:
        raise GoogleAuthError(
            "An account with this email already exists. "
            "Sign in using your existing account before linking Google."
        )

    user = User.objects.create_user(
        username=email,
        email=email,
        first_name=id_info.get("given_name", ""),
        last_name=id_info.get("family_name", "")
    )

    SocialAccount.objects.create(
        user=user,
        provider="google",
        provider_user_id=google_id,
        email=email
    )

    return user, True
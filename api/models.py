from django.db import models
from django.contrib.auth.models import User


class SocialAccount(models.Model):

    PROVIDER_CHOICES = [
        ('google', 'Google'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='social_accounts'
    )

    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES
    )

    provider_user_id = models.CharField(
        max_length=255,
        unique=True
    )

    email = models.EmailField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'social_accounts'

    def __str__(self):
        return f"{self.provider}: {self.email}"
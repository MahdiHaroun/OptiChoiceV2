from django.db import models

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid # Unique identifier for each user
# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_verified = models.BooleanField(default=False)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)
    password_reset_sent_at = models.DateTimeField(null=True, blank=True)
    account_deletion_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"UserProfile for {self.user.username}"
    
    def is_email_verification_valid(self):
        # Check if the email verification token is still valid
        if not self.email_verification_sent_at:         
            return False
        return (timezone.now() - self.email_verification_sent_at).total_seconds() < 3600 # 1 hour validity
    
    def is_password_reset_valid(self):
        # Check if the password reset token is still valid
        if not self.password_reset_sent_at:
            return False
        return (timezone.now() - self.password_reset_sent_at).total_seconds() < 86400  # 24 hours validity

    def is_account_deletion_valid(self):
        # Check if the account deletion token is still valid
        if not self.account_deletion_sent_at:
            return False
        return (timezone.now() - self.account_deletion_sent_at).total_seconds() < 3600  # 1 hour validity

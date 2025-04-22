from django.db import models

from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
import os

def user_profile_photo_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/users/<username>/profile_photos/<filename>
    return os.path.join('users', instance.user.username, 'profile_photos', filename)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_photo = models.ImageField(
        upload_to=user_profile_photo_path,
        blank=True,
        null=True,
        verbose_name='Profile Photo'
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

# Signal to automatically create profile when user is created
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.profile.save()

from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager

class CustomUser(AbstractBaseUser):
    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(max_length=1000)
    # post_img = models.ImageField(upload_to='post_images', default='blank-profile-picture.png')
    profile_img = models.ImageField(upload_to='profile_images/', default='profile_images/blank-profile-picture.png')
    cover_img = models.ImageField(upload_to='cover_images/', default='cover_images/blank-cover-picture.png')
    background_img = models.ImageField(upload_to='background_images/', default='background_images/blank-background-picture.jpeg')
    img1 = models.ImageField(upload_to='img1/', default='cover_images/blank-cover-picture.png')
    img2 = models.ImageField(upload_to='img2/', default='cover_images/blank-cover-picture.png')
    img3 = models.ImageField(upload_to='img3/', default='cover_images/blank-cover-picture.png')
    img4 = models.ImageField(upload_to='img4/', default='cover_images/blank-cover-picture.png')
    img5 = models.ImageField(upload_to='img5/', default='cover_images/blank-cover-picture.png')
    img6 = models.ImageField(upload_to='img6/', default='cover_images/blank-cover-picture.png')
    active = models.BooleanField(default=True)  # able to login
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
    
    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active
        
class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    friends = models.ManyToManyField('self', blank=True, related_name='friends')
   
    def __str__(self):
        return self.user.username
    
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class FriendRequest(models.Model):
    from_user = models.ForeignKey(CustomUser, related_name='friend_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(CustomUser, related_name='friend_requests_received', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.from_user} to {self.to_user}'
    
class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)  # Assuming Profile is the user's profile model
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    post_img = models.ImageField(upload_to='post_images/', default='', blank=True)

    def __str__(self):
        return f'{self.user.username} on {self.profile.user.username}\'s profile'
    

class ProfanityWord(models.Model):
    word = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.word
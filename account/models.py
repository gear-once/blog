from django.db import models
from django.conf import settings
from django.db.models.signals import post_save


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/',
                              blank=True)

    def __str__(self):
        return f'Profile of {self.user.username}'


#Signals: create Profile for USer if it was created in admin Panel
def post_user_created_signal(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


post_save.connect(post_user_created_signal, sender=settings.AUTH_USER_MODEL)
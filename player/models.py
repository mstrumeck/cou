from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)
    current_turn = models.IntegerField(default=1)

    chance_to_marriage_percent = models.FloatField(default=0.80)
    chance_to_born_baby_percent = models.FloatField(default=0.60)

    standard_residential_zone_taxation = models.FloatField(default=0.01)

    primary_school_education_ratio = models.FloatField(default=0.0104)

    if_social_enabled = models.BooleanField(default=False)


class Message(models.Model):
    profile = models.ForeignKey(Profile)
    turn = models.IntegerField(default=0)
    text = models.TextField()


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


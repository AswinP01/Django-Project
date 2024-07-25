from django.contrib.auth.models import User
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from .models import Profile

@receiver(post_save,sender=User)
def cpro(sender,instance,created,**kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            email=instance.email,
            first_name=instance.first_name,
            last_name=instance.last_name,
            full_name=f"{instance.first_name} {instance.last_name}",
            phone_no=''
            )
        

@receiver(post_delete,sender=Profile)
def deluser(sender,instance,**kwargs):
    user=instance.user
    user.delete()
           
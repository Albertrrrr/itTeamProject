from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser
from backstage.models import ShoppingCart

@receiver(post_save, sender=CustomUser)
def create_user_shopping_cart(sender, instance, created, **kwargs):
    if created and instance.user_type == 'user':
        ShoppingCart.objects.create(userID_id=instance.id)


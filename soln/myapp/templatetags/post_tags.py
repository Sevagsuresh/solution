from django import template
from ..models import Like

register = template.Library()

@register.filter
def has_liked(post, user):
    if user.is_authenticated:
        return Like.objects.filter(post=post, user=user).exists()
    return False
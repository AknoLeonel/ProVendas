from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    # Se for superusuário, sempre retorna True (acesso total)
    if user.is_superuser:
        return True
    
    # Verifica se o usuário pertence ao grupo
    return user.groups.filter(name=group_name).exists()
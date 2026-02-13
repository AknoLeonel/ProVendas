from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    """
    Verifica se o usuário pertence a um grupo específico.
    Uso no template: {% if request.user|has_group:"Administrador" %}
    """
    if user.is_superuser:
        return True # Superusuário é sempre "Administrador"
        
    try:
        group = Group.objects.get(name=group_name)
        return group in user.groups.all()
    except Group.DoesNotExist:
        return False
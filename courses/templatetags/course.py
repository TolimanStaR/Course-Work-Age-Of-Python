from django import template

register = template.Library()


@register.filter
def model_name(obj):
    try:
        return obj._meta.model_name
    except AttributeError:
        return None

@register.filter
def index(obj, index):
    try:
        return obj[index]
    except AttributeError:
        return None

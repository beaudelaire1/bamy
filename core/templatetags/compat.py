from django import template

register = template.Library()

@register.filter(name="length_is")
def length_is(value, arg):
    """Retourne True si len(value) == arg, sinon False."""
    try:
        return len(value) == int(arg)
    except Exception:
        return False

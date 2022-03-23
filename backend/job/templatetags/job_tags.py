from django import template

register = template.Library()


@register.filter(name="space_to_dash")
def space_to_dash(value: str):
    return value.replace(" ", "-")

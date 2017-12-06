from django import template

register = template.Library()


@register.filter
def my_range(n):
    return range(1, n + 1)

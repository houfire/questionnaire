from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def my_range(n):
    return range(1, n + 1)


@register.filter
def judge_zero(n):
    if n == '': return 0
    return n

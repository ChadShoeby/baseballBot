from django import template

register = template.Library()

@register.filter
def get_points(stats, stat_name):
    return getattr(stats, stat_name)
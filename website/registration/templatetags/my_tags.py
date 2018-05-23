from django import template

from random import choice

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.simple_tag
def random_classname():
    """
  Returns a random classname
  """
    classes = ['is-primary', 'is-link', 'is-info',
               'is-success', 'is-warning', 'is-danger',
               'is-black', 'is-dark', 'is-light', 'is-white']

    return str(choice(classes))

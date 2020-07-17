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


@register.filter('startswith')
def startswith(text, starts):
    if isinstance(text, str):
        return text.startswith(starts)
    return False


@register.filter(name='addclass')
def addclass(field, class_attr):
    return field.as_widget(attrs={'class': class_attr})

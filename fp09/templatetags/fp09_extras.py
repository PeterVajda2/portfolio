from django import template

register = template.Library()


@register.filter
def cut_after(text, cut_char):
    
    if cut_char in text:
        return text.split(cut_char)[0]
    else:
        return text
from django import template
register = template.Library()
@register.filter(name='currency')
def currency(number):
    return "UZS " + str(number)

@register.filter(name='multiply')
def muliply(number, number1):
    return number * number1

from django import template
register=template.Library()

def subtraction(value,s):
   val = value - s
   return val

register.filter('sub',subtraction)

def addition(value,s):
   val = value + s
   return val

register.filter('add',addition)
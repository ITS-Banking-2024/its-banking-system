from django import template

from core.models import Product

register = template.Library()


@register.inclusion_tag('orders/add_to_basket_form.html')
def additional_product_functionality(product: Product):
    # Determine the additional functionality based on the context
    # ...
    # Generate the HTML code or functionality dynamically
    return {'product': product}


@register.inclusion_tag('orders/basket_header.html', takes_context=True)
def additional_product_header(context):
    request = context['request']
    product_list = request.session.get('product_list', [])
    basket_count = len(product_list)
    return {'basket_count': basket_count}

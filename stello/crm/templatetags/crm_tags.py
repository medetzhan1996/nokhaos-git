from django import template
from crm.models import Integration, Order
from figma.models import Product, Material

register = template.Library()


@register.simple_tag
def get_product(product_id):
    product = Product.objects.get(id=product_id)
    if product:
        return product
    else:
        return '-----------'


@register.simple_tag
def get_material(material_id):
    if material_id:
        material = Material.objects.get(id=material_id)
        if material:
            return material.title
    else:
        return '-----------'


@register.simple_tag
def is_selected(option_val, val):
    if option_val == val:
        return 'selected'
    else:
        return ''


@register.simple_tag
def is_checked(check):
    if check:
        return 'checked'
    else:
        return ''


@register.simple_tag
def is_integrate(integration, user):
    if user:
        if Integration.objects.filter(
                managers=user, pk=integration.id).exists():
            return 'checked'
        else:
            return ''
    else:
        return None


@register.simple_tag
def is_active(val1, val2):
    if val1 == val2:
        return 'active'
    else:
        return ''


@register.simple_tag
def get_count_lead(lead):
    return lead.count()

@register.simple_tag
def get_count_order(user):
    return Order.objects.filter(company=user.profile.company).count()

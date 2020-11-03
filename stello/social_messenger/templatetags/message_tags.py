from django import template
register = template.Library()


@register.simple_tag
def is_fromMe(fromMe):
    if fromMe:
        return 'self'
    else:
        return ''


@register.simple_tag
def is_visible(val):
    if val:
        return 'main-visible'
    else:
        return ''

@register.simple_tag
def set_wss(user):
	if user.profile.type == 3:
		return user.id
	else:
		return 'company/{}'.format(user.profile.company.id)

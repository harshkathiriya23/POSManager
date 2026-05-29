from django import template

register = template.Library()


@register.filter
def user_initials(user):
    if user.name:
        parts = user.name.strip().split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return parts[0][:2].upper()
    if user.personID:
        return user.personID[:2].upper()
    return "U"

# apps/core/templatetags/custom_filters.py
# Create this file for better date formatting

from django import template
from django.utils import timezone
from datetime import datetime

register = template.Library()


@register.filter
def format_datetime(value):
    """Format datetime in user-friendly way"""
    if not value:
        return ''
    
    # Convert to local timezone if needed
    if timezone.is_aware(value):
        value = timezone.localtime(value)
    
    now = timezone.now()
    diff = now - value
    
    # Today
    if value.date() == now.date():
        return f"Today at {value.strftime('%I:%M %p')}"
    
    # Yesterday
    if (now - value).days == 1:
        return f"Yesterday at {value.strftime('%I:%M %p')}"
    
    # This week (last 7 days)
    if diff.days < 7:
        return value.strftime('%A at %I:%M %p')  # "Monday at 2:30 PM"
    
    # This year
    if value.year == now.year:
        return value.strftime('%b %d at %I:%M %p')  # "Nov 25 at 2:30 PM"
    
    # Older
    return value.strftime('%b %d, %Y')  # "Nov 25, 2024"


@register.filter
def format_date(value):
    """Format date only (no time)"""
    if not value:
        return ''
    
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d')
        except:
            return value
    
    now = timezone.now()
    
    # Today
    if value.date() == now.date():
        return "Today"
    
    # Yesterday
    if (now - value).days == 1:
        return "Yesterday"
    
    # This year
    if value.year == now.year:
        return value.strftime('%b %d')  # "Nov 25"
    
    # Older
    return value.strftime('%b %d, %Y')  # "Nov 25, 2024"


@register.filter
def format_currency(value):
    """Format currency with € symbol"""
    try:
        return f"€{float(value):,.2f}"
    except (ValueError, TypeError):
        return value


@register.filter
def stock_status_color(quantity, reorder_level):
    """Return color based on stock level"""
    if quantity <= 0:
        return 'red'
    elif quantity <= reorder_level:
        return 'orange'
    elif quantity <= reorder_level * 2:
        return 'yellow'
    return 'green'


@register.filter
def stock_status_text(quantity, reorder_level):
    """Return status text based on stock level"""
    if quantity <= 0:
        return 'OUT OF STOCK'
    elif quantity <= reorder_level:
        return 'LOW STOCK'
    elif quantity <= reorder_level * 2:
        return 'REORDER SOON'
    return 'IN STOCK'

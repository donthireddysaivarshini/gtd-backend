from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Order

def send_order_confirmation_email(order_id):
    try:
        order = Order.objects.get(id=order_id)
        items = order.items.all()
        
        subject = f'Order Confirmed! Order #{order.id} - GTD Fashion'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = order.user.email

        # Prepare data for the template
        context = {
            'order': order,
            'items': items,
        }

        # Render HTML content
        html_content = render_to_string('emails/order_confirmation.html', context)
        text_content = strip_tags(html_content) # Fallback for email clients that don't support HTML

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        print(f"DEBUG: Email sent successfully to {to_email}")
        
    except Exception as e:
        print(f"DEBUG: Error sending email: {str(e)}")
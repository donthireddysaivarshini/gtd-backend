import razorpay
from django.conf import settings

def _get_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def create_order(amount):
    """
    Amount should be in Rupees.
    Razorpay requires the amount in PAISE (int).
    """
    client = _get_client()
    # int(amount * 100) converts 100.00 Rupees to 10000 Paise
    return client.order.create({
        "amount": int(float(amount) * 100),
        "currency": "INR",
        "payment_capture": 1
    })

def verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    client = _get_client()
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })
        return True
    except Exception:
        return False
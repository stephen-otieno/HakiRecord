import africastalking
from django.conf import settings

def send_sms_message(phone_number, message):
    """
    Sends an SMS using Africa's Talking API.
    """
    africastalking.initialize(
        username=settings.AFRICASTALKING_USERNAME,
        api_key=settings.AFRICASTALKING_API_KEY
    )

    sms = africastalking.SMS

    try:
        response = sms.send(message, [phone_number])
        print(" SMS sent successfully:", response)
        return response
    except Exception as e:
        print(" SMS sending failed:", str(e))
        return None

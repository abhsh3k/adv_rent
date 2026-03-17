import random
import string
from django.utils import timezone
from datetime import timedelta


def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


def set_otp(user, method):
    """Generate and save OTP to user. Returns the code."""
    otp = generate_otp()
    user.otp_code      = otp
    user.otp_expires_at = timezone.now() + timedelta(minutes=10)
    user.otp_method    = method
    user.save()
    return otp


def verify_otp(user, code):
    """Returns True if code matches and hasn't expired."""
    if not user.otp_code or not user.otp_expires_at:
        return False
    if timezone.now() > user.otp_expires_at:
        return False
    return user.otp_code == code.strip()


def clear_otp(user):
    user.otp_code       = ''
    user.otp_expires_at = None
    user.otp_method     = ''
    user.save()
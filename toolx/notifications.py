import httpx
import logging
from django.conf import settings
from django.core.mail import send_mail
from django.utils.html import escape

logger = logging.getLogger(__name__)


def get_base_url():
    return getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000').rstrip('/')


def send_telegram(chat_id, message):
    if not chat_id:
        return
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if not token:
        logger.warning('Telegram notification skipped: TELEGRAM_BOT_TOKEN not set.')
        return
    try:
        response = httpx.post(
            f'https://api.telegram.org/bot{token}/sendMessage',
            json={
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': False
            },
            timeout=10
        )
        response.raise_for_status()
    except Exception as e:
        logger.error(f'Telegram send failed for chat_id {chat_id}: {e}')


def send_email(to_email, subject, body):
    if not to_email:
        return
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=True,
        )
    except Exception as e:
        logger.warning(f'Email send failed to {to_email}: {e}')


def send_sms(phone_number, message):
    """Send SMS via Twilio."""
    if not phone_number:
        return
    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        number = phone_number.strip()
        if not number.startswith('+'):
            number = '+' + number
        client.messages.create(
            from_=settings.TWILIO_SMS_FROM,
            to=number,
            body=message[:160]  # SMS limit
        )
    except Exception as e:
        logger.warning(f'SMS send failed: {e}')


def send_otp_email(user, otp):
    send_email(
        user.email,
        'Your ToolX verification code',
        f'Hi {user.first_name or user.username},\n\n'
        f'Your verification code is:\n\n'
        f'    {otp}\n\n'
        f'This code expires in 10 minutes.\n\n'
        f'— ToolX'
    )


def send_otp_sms(user, otp):
    send_sms(
        user.phone,
        f'Your ToolX code: {otp}. Valid for 10 minutes.'
    )


def notify_new_rental_request(rental):
    owner = rental.tool.owner
    renter = rental.renter
    tool = rental.tool
    cost = getattr(rental, 'total_cost', 'N/A')
    url = f"{get_base_url()}/dashboard/"

    msg_plain = (
        f'Hi {owner.first_name or owner.username},\n\n'
        f'{renter.get_full_name() or renter.username} wants to rent "{tool.name}"\n'
        f'{rental.start_date} → {rental.end_date} · ₹{cost}\n\n'
        f'Log in to approve: {url}'
    )
    msg_short = (
        f'🔧 New rental request!\n'
        f'{renter.get_full_name() or renter.username} wants to rent {tool.name}\n'
        f'{rental.start_date} → {rental.end_date} · ₹{cost}\n'
        f'Approve: {url}'
    )
    msg_telegram = (
        f'🔧 <b>New rental request!</b>\n'
        f'{escape(renter.get_full_name() or renter.username)} wants to rent <b>{escape(tool.name)}</b>\n'
        f'📅 {rental.start_date} → {rental.end_date}\n'
        f'💰 <b>₹{cost}</b>\n\n'
        f'<a href="{url}">Open Dashboard to Respond</a>'
    )
    send_email(owner.email, f'New rental request for {tool.name}', msg_plain)
    send_telegram(owner.telegram_chat_id, msg_telegram)
    send_sms(owner.phone, msg_short)


def notify_rental_approved(rental):
    renter = rental.renter
    tool = rental.tool
    thread_url = f"{get_base_url()}/rentals/rental/{rental.pk}/thread/"

    msg_plain = (
        f'Hi {renter.first_name or renter.username},\n\n'
        f'Your rental of "{tool.name}" has been approved!\n'
        f'Message the owner to arrange pickup: {thread_url}'
    )
    msg_short = (
        f'✅ Rental approved!\n'
        f'"{tool.name}" is confirmed.\n'
        f'Chat with owner: {thread_url}'
    )
    msg_telegram = (
        f'✅ <b>Rental approved!</b>\n'
        f'Your request for <b>{escape(tool.name)}</b> is confirmed.\n\n'
        f'<a href="{thread_url}">Chat with the owner</a>'
    )
    send_email(renter.email, f'Rental approved — {tool.name}', msg_plain)
    send_telegram(renter.telegram_chat_id, msg_telegram)
    send_sms(renter.phone, msg_short)


def notify_rental_declined(rental):
    renter = rental.renter
    tool = rental.tool
    tools_url = f"{get_base_url()}/tools/"

    msg_plain = (
        f'Hi {renter.first_name or renter.username},\n\n'
        f'Your rental request for "{tool.name}" was declined.\n'
        f'Browse other tools: {tools_url}'
    )
    msg_short = (
        f'❌ Rental declined.\n'
        f'Your request for "{tool.name}" was not approved.\n'
        f'Browse tools: {tools_url}'
    )
    msg_telegram = (
        f'❌ <b>Rental declined</b>\n'
        f'Your request for <b>{escape(tool.name)}</b> was not approved.\n\n'
        f'<a href="{tools_url}">Browse other tools</a>'
    )
    send_email(renter.email, f'Rental request declined — {tool.name}', msg_plain)
    send_telegram(renter.telegram_chat_id, msg_telegram)
    send_sms(renter.phone, msg_short)


def notify_tool_returned(rental):
    renter = rental.renter
    tool = rental.tool
    review_url = f"{get_base_url()}/reviews/review/{rental.pk}/"

    msg_plain = (
        f'Hi {renter.first_name or renter.username},\n\n'
        f'"{tool.name}" has been marked as returned.\n'
        f'Leave a review: {review_url}'
    )
    msg_short = (
        f'📦 Tool returned!\n'
        f'"{tool.name}" has been returned.\n'
        f'Leave a review: {review_url}'
    )
    msg_telegram = (
        f'📦 <b>Tool returned!</b>\n'
        f'<b>{escape(tool.name)}</b> has been returned successfully.\n\n'
        f'<a href="{review_url}">Leave a review for the owner</a>'
    )
    send_email(renter.email, f'How was {tool.name}? Leave a review!', msg_plain)
    send_telegram(renter.telegram_chat_id, msg_telegram)
    send_sms(renter.phone, msg_short)


def notify_new_message(rental, sender, recipient, message_preview):
    thread_url = f"{get_base_url()}/rentals/rental/{rental.pk}/thread/"

    msg_plain = (
        f'Hi {recipient.first_name or recipient.username},\n\n'
        f'{sender.username}: "{message_preview}"\n\n'
        f'Reply: {thread_url}'
    )
    msg_short = (
        f'💬 New message from {sender.get_full_name() or sender.username}\n'
        f'About: {rental.tool.name}\n'
        f'"{message_preview}"\n'
        f'Reply: {thread_url}'
    )
    msg_telegram = (
        f'💬 <b>New message</b> from {escape(sender.username)}\n'
        f'About: <b>{escape(rental.tool.name)}</b>\n\n'
        f'<i>"{escape(message_preview)}"</i>\n\n'
        f'<a href="{thread_url}">Reply in ToolX</a>'
    )
    send_email(recipient.email, f'New message about {rental.tool.name}', msg_plain)
    send_telegram(recipient.telegram_chat_id, msg_telegram)
    send_sms(recipient.phone, msg_short)
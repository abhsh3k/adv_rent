import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toolx.settings')
django.setup()


import httpx
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

def get_updates(offset=None):
    params = {'timeout': 30}
    if offset:
        params['offset'] = offset
    r = httpx.get(
        f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getUpdates',
        params=params,
        timeout=35
    )
    return r.json()

def send_message(chat_id, text):
    httpx.post(
        f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage',
        json={'chat_id': chat_id, 'text': text},
        timeout=5
    )

def handle_update(update):
    message = update.get('message', {})
    text = message.get('text', '')
    chat_id = message.get('chat', {}).get('id')

    if not text or not chat_id:
        return

    if text.startswith('/start'):
        parts = text.split(' ', 1)
        if len(parts) == 1:
            send_message(chat_id,
                '👋 Welcome to ToolX bot!\n\n'
                'Go to your profile on ToolX and click '
                '"Generate Telegram link" to link your account.'
            )
            return

        token = parts[1].strip()
        try:
            user = User.objects.get(telegram_link_token=token)
            user.telegram_chat_id = str(chat_id)
            user.telegram_link_token = ''
            user.save()
            send_message(chat_id,
                f'✅ Account linked!\n\n'
                f'Hi {user.first_name or user.username}! '
                f'You\'ll now receive rental updates here.'
            )
        except User.DoesNotExist:
            send_message(chat_id,
                '❌ Invalid or expired link.\n'
                'Generate a new one from your ToolX profile.'
            )

def run():
    print('ToolX Telegram bot started...')
    offset = None
    while True:
        try:
            data = get_updates(offset)
            for update in data.get('result', []):
                handle_update(update)
                offset = update['update_id'] + 1
        except Exception as e:
            print(f'Error: {e}')

if __name__ == '__main__':
    run()
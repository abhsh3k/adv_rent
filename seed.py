import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toolx.settings')
django.setup()

from tools.models import Category
from django.utils.text import slugify

def seed():
    default_categories = [
        {'name': 'Power Tools', 'icon': '⚡'},
        {'name': 'Hand Tools', 'icon': '🔨'},
        {'name': 'Measuring', 'icon': '📏'},
        {'name': 'Garden Tools', 'icon': '🌿'},
        {'name': 'Lab Equipment', 'icon': '🔬'},
        {'name': 'Art & Craft', 'icon': '🎨'},
        {'name': 'Electronics', 'icon': '💻'},
        {'name': 'Other', 'icon': '📦'},
    ]

    print("Seeding database...")
    for cat in default_categories:
        obj, created = Category.objects.get_or_create(
            slug=slugify(cat['name']),
            defaults={'name': cat['name'], 'icon': cat['icon']}
        )
        status = "Created" if created else "Already exists"
        print(f"{cat['name']}: {status}")

if __name__ == '__main__':
    seed()
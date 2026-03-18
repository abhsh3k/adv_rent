import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files import File
from tools.models import Category, Tool 

User = get_user_model()

class Command(BaseCommand):
    help = "Seeds ToolShare using images from genfiles/tools/"

    def handle(self, *args, **kwargs):
        # Path to your source folder (relative to project root)
        SOURCE_DIR = os.path.join(settings.BASE_DIR, 'genfiles', 'tools')
        
        self.stdout.write(self.style.MIGRATE_LABEL(f"--- Seeding from {SOURCE_DIR} ---"))

        # 1. Admin & Categories Setup
        admin_user, _ = User.objects.get_or_create(
            email="toolx2001@gmail.com",
            defaults={'username': 'admin', 'is_staff': True, 'is_superuser': True}
        )
        if _: admin_user.set_password('admin'); admin_user.save()

        categories_data = ["Power Tools", "Gardening", "Construction", "Cleaning", "Hand Tools"]
        cat_objs = {name: Category.objects.get_or_create(name=name)[0] for name in categories_data}

        # 2. Tool List
        manual_tools = [
            ("Makita Drill", "Power Tools", 450, "makita_drill.png"),
            ("Bosch Grinder", "Power Tools", 350, "bosch_grinder.jpg"),
            ("Stihl Chainsaw", "Gardening", 850, "stihl_chainsaw.jpg"),
            ("Karcher Washer", "Cleaning", 500, "karcher_washer.jpg"),
            ("Stanley Hammer", "Hand Tools", 150, "stanley_hammer.jpg"),
        ]

        for name, cat_name, price, img_name in manual_tools:
            source_path = os.path.join(SOURCE_DIR, img_name)
            
            if not os.path.exists(source_path):
                self.stdout.write(self.style.WARNING(f"⚠ Skipping {name}: {img_name} not found in genfiles/tools/"))
                continue

            # We use update_or_create to keep the DB in sync with your list
            tool, created = Tool.objects.update_or_create(
                name=name,
                defaults={
                    'category': cat_objs[cat_name],
                    'owner': admin_user,
                    'daily_rate': price,
                    'description': f"Professional grade {name} available for daily rent.",
                    'condition': 'good',
                    'location': 'Thiruvananthapuram',
                    'is_available': True,
                }
            )

            # IMPORTANT: We "open" the file from genfiles and "save" it into your MEDIA_ROOT
            # This ensures Django's FileField handles the URL correctly in your templates
            with open(source_path, 'rb') as f:
                tool.image.save(img_name, File(f), save=True)

            status = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"✔ {status}: {name}"))

        self.stdout.write(self.style.MIGRATE_LABEL("--- Seed Complete ---"))
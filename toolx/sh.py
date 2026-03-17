from django.contrib.auth import get_user_model
User = get_user_model()

# Get the user 'abhishek' (your DB user)
# If he doesn't exist, we'll create him
u, created = User.objects.get_or_create(username='abhishek')

u.set_password('Abhi@2412') # Using your DB password for simplicity
u.is_superuser = True
u.is_staff = True
u.is_active = True
u.save()

print(f"User {u.username} updated. Staff: {u.is_staff}, Active: {u.is_active}")
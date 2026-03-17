from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon name")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Tool(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('worn', 'Worn'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tools'
    )
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # FIX: This is now the actual link to your Category model
    category = models.ForeignKey(
        Category, 
        on_delete=models.PROTECT, 
        related_name='tools'
    )
    
    condition   = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='good')
    daily_rate  = models.DecimalField(max_digits=8, decimal_places=2)
    location    = models.CharField(max_length=100, blank=True)
    image       = models.ImageField(upload_to='tools/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    latitude    = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude   = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} by {self.owner.username}"

    class Meta:
        ordering = ['-created_at']
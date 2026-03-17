from django.db import models
from django.conf import settings

class Rental(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled'),
    ]

    tool = models.ForeignKey(
        'tools.Tool',
        on_delete=models.CASCADE,
        related_name='rentals'
    )
    renter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rentals'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    terms_accepted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # auto-calculate total cost before saving
        if self.start_date and self.end_date and self.tool:
            days = (self.end_date - self.start_date).days
            self.total_cost = days * self.tool.daily_rate
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.renter.username} renting {self.tool.name}"

    class Meta:
        ordering = ['-created_at']

class Message(models.Model):
    rental = models.ForeignKey(
        Rental,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username}: {self.body[:40]}"

    class Meta:
        ordering = ['created_at']
# models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.contrib.auth.models import User
import random

# Extended User Profile Model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.user.get_full_name() or self.user.username

# Invoice Model
class Invoice(models.Model):
    PRODUCT_TYPES = [
        ('domain', 'Domain'),
        ('email', 'Custom Email'),
    ]

    PAYMENT_STATUSES = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_GATEWAYS = [
        ('bank', 'Bank Deposit'),
        ('card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('crypto', 'Cryptocurrency'),
    ]

    id = models.CharField(max_length=6, primary_key=True, unique=True, editable=False)  # Custom 6-digit ID
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPES)
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    transaction_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    payment_gateway = models.CharField(max_length=10, choices=PAYMENT_GATEWAYS)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUSES, default='unpaid')

    def __str__(self):
        return f"Invoice #{self.id} - {self.user.get_full_name() or self.user.username}"

    def is_overdue(self):
        return self.payment_status == 'unpaid' and timezone.now() > self.due_date

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = self.generate_random_id()
        super().save(*args, **kwargs)

    def generate_random_id(self):
        """Generate a unique 6-digit random number."""
        while True:
            random_id = str(random.randint(100000, 999999))  # Generate a 6-digit number
            if not Invoice.objects.filter(id=random_id).exists():  # Ensure uniqueness
                return random_id

# Additional Charges Model
class AdditionalCharge(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='additional_charges')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.description} - ${self.amount}"
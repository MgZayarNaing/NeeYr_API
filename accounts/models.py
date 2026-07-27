import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


# ==========================================
# 0. Custom Authorization Models (UUID Primary Keys)
# ==========================================
class UUIDPermission(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=255)
    codename = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"

    def __str__(self):
        return f"{self.name} ({self.codename})"


class UUIDGroup(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=150, unique=True)
    permissions = models.ManyToManyField(
        UUIDPermission,
        blank=True,
        related_name="custom_groups"
    )

    class Meta:
        verbose_name = "Group"
        verbose_name_plural = "Groups"

    def __str__(self):
        return self.name


# ==========================================
# Custom User Model (UUID Primary Key)
# ==========================================
class User(AbstractUser):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # 🔹 Django Default Integer-based Groups/Permissions များကို Disable လုပ်ခြင်း
    groups = None
    user_permissions = None

    # 🔹 Custom UUID Models များဖြင့် ပြန်လည်ချိတ်ဆက်ခြင်း
    custom_groups = models.ManyToManyField(
        UUIDGroup,
        blank=True,
        related_name="users",
        verbose_name="groups"
    )
    custom_permissions = models.ManyToManyField(
        UUIDPermission,
        blank=True,
        related_name="users",
        verbose_name="user permissions"
    )

    def __str__(self):
        return self.username


# ==========================================
# 1. Subscription Plans
# ==========================================
class SubscriptionPlan(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=50)  # Basic, Pro, Enterprise
    max_branches = models.IntegerField(default=1, null=True,blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    duration_days = models.IntegerField(default=30)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# ==========================================
# 2. Owner Profile
# ==========================================
class OwnerProfile(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='owner_profile'
    )
    current_plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    business_name = models.CharField(max_length=255, blank=True, null=True)
    logo = models.ImageField(upload_to='owner_logos/', blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    is_verified = models.BooleanField(default=False)
    plan_expires_at = models.DateTimeField(null=True, blank=True)
    auto_renew = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.business_name or 'No Business'}"


# ==========================================
# 3. Payment Transactions
# ==========================================
class PaymentTransaction(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    owner = models.ForeignKey(OwnerProfile, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    merchant_order_id = models.CharField(max_length=100, unique=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, default='PENDING')  # PENDING, SUCCESS, FAILED
    paid_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.merchant_order_id} - {self.payment_status}"


# ==========================================
# 4. Subscription Renewal History
# ==========================================
class OwnerSubscriptionHistory(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    owner = models.ForeignKey(OwnerProfile, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    payment_transaction = models.ForeignKey(
        PaymentTransaction,
        on_delete=models.SET_NULL,
        null=True
    )
    transaction_type = models.CharField(max_length=20)  # NEW, RENEW, UPGRADE
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.owner.user.username} - {self.transaction_type} ({self.plan.name})"
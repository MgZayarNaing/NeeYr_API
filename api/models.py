import uuid
from django.db import models
from django.conf import settings
from accounts.models import OwnerProfile, SubscriptionPlan


# 1. Location & Metadata
class RegionState(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class City(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    region = models.ForeignKey(RegionState, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.region.name})"


class Category(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


# 2. Business Brand & Branch
class BusinessBrand(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    owner = models.ForeignKey(OwnerProfile, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='brand_logos/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Branch(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    brand = models.ForeignKey(BusinessBrand, on_delete=models.CASCADE, related_name='branches')
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    branch_name = models.CharField(max_length=255)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    opening_hours = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    views_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, default='ACTIVE')  # ACTIVE, DRAFT, HIDDEN
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand.name} ({self.branch_name})"


class BranchImage(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='branch_images/')

    def __str__(self):
        return f"Image for {self.branch.branch_name}"


class BranchSocialLink(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='social_links')
    platform_name = models.CharField(max_length=50)  # FACEBOOK, TELEGRAM, TIKTOK, VIBER
    url = models.URLField()

    def __str__(self):
        return f"{self.platform_name} - {self.branch.branch_name}"


# 3. Analytics Log
class BranchViewLog(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # 👈 Custom User Model/UUID ကို ညွှန်းခြင်း
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_name = self.user.username if self.user else "Anonymous"
        return f"{self.branch.branch_name} viewed by {user_name}"


# 4. Review & Feedback
class BranchReview(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # 👈 Custom User Model/UUID ကို ညွှန်းခြင်း
        on_delete=models.CASCADE
    )
    rating = models.IntegerField()
    comment = models.TextField(null=True, blank=True)
    owner_reply = models.TextField(null=True, blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} ({self.rating}★)"

class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class SavedPost(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='saved_posts'
    )
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='saved_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_user_saved_post')
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} saved {self.post_id}"

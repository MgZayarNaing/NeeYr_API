from zoneinfo import ZoneInfo
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    UUIDGroup,
    UUIDPermission,
    SubscriptionPlan, 
    OwnerProfile, 
    PaymentTransaction, 
    OwnerSubscriptionHistory
)

User = get_user_model()


# ==========================================
# 0. Authorization Serializers (Group & Permission)
# ==========================================
class UUIDPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UUIDPermission
        fields = ['id', 'name', 'codename', 'description']


class UUIDGroupSerializer(serializers.ModelSerializer):
    permissions = UUIDPermissionSerializer(many=True, read_only=True)

    class Meta:
        model = UUIDGroup
        fields = ['id', 'name', 'permissions']


# ==========================================
# 1. User Serializer
# ==========================================
class UserSerializer(serializers.ModelSerializer):
    is_owner = serializers.SerializerMethodField()
    date_joined = serializers.SerializerMethodField()
    last_login = serializers.SerializerMethodField()
    
    # Custom Group & Permission nested serializers
    groups = UUIDGroupSerializer(source='custom_groups', many=True, read_only=True)
    permissions = UUIDPermissionSerializer(source='custom_permissions', many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 
            'username', 
            'email', 
            'first_name', 
            'last_name', 
            'is_active', 
            'is_staff',
            'is_superuser',
            'is_owner', 
            'date_joined', 
            'last_login',
            'groups',
            'permissions'
        ]
        read_only_fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'is_staff',
            'is_superuser',
            'is_owner',
            'date_joined',
            'last_login',
            'groups',
            'permissions'
        ]

    def get_is_owner(self, obj):
        return hasattr(obj, 'owner_profile')

    def get_date_joined(self, obj):
        if obj.date_joined:
            mm_time = obj.date_joined.astimezone(ZoneInfo("Asia/Yangon"))
            return mm_time.strftime("%Y-%m-%d %I:%M:%S %p")
        return None

    def get_last_login(self, obj):
        if obj.last_login:
            mm_time = obj.last_login.astimezone(ZoneInfo("Asia/Yangon"))
            return mm_time.strftime("%Y-%m-%d %I:%M:%S %p")
        return None


# ==========================================
# 2. Subscription Plan Serializer
# ==========================================
class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id',
            'name',
            'max_branches',
            'price',
            'duration_days',
            'is_active'
        ]


# ==========================================
# 3. Owner Profile Serializer
# ==========================================
class OwnerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    current_plan = SubscriptionPlanSerializer(read_only=True)
    plan_expires_at = serializers.SerializerMethodField()

    class Meta:
        model = OwnerProfile
        fields = [
            'id',
            'user',
            'current_plan',
            'business_name',
            'logo',
            'phone_number',
            'is_verified',
            'plan_expires_at',
            'auto_renew'
        ]

    def get_plan_expires_at(self, obj):
        if obj.plan_expires_at:
            mm_time = obj.plan_expires_at.astimezone(ZoneInfo("Asia/Yangon"))
            return mm_time.strftime("%Y-%m-%d %I:%M:%S %p")
        return None


# ==========================================
# 4. Payment Transaction Serializer
# ==========================================
class PaymentTransactionSerializer(serializers.ModelSerializer):
    owner_detail = OwnerProfileSerializer(source='owner', read_only=True)
    plan_detail = SubscriptionPlanSerializer(source='plan', read_only=True)
    paid_at = serializers.SerializerMethodField()
    expires_at = serializers.SerializerMethodField()

    class Meta:
        model = PaymentTransaction
        fields = [
            'id',
            'owner',
            'owner_detail',
            'plan',
            'plan_detail',
            'merchant_order_id',
            'transaction_id',
            'amount',
            'payment_status',
            'paid_at',
            'expires_at'
        ]

    def get_paid_at(self, obj):
        if obj.paid_at:
            mm_time = obj.paid_at.astimezone(ZoneInfo("Asia/Yangon"))
            return mm_time.strftime("%Y-%m-%d %I:%M:%S %p")
        return None

    def get_expires_at(self, obj):
        if obj.expires_at:
            mm_time = obj.expires_at.astimezone(ZoneInfo("Asia/Yangon"))
            return mm_time.strftime("%Y-%m-%d %I:%M:%S %p")
        return None


# ==========================================
# 5. Owner Subscription History Serializer
# ==========================================
class OwnerSubscriptionHistorySerializer(serializers.ModelSerializer):
    owner_detail = OwnerProfileSerializer(source='owner', read_only=True)
    plan_detail = SubscriptionPlanSerializer(source='plan', read_only=True)
    payment_transaction_detail = PaymentTransactionSerializer(source='payment_transaction', read_only=True)
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = OwnerSubscriptionHistory
        fields = [
            'id',
            'owner',
            'owner_detail',
            'plan',
            'plan_detail',
            'payment_transaction',
            'payment_transaction_detail',
            'transaction_type',
            'start_date',
            'end_date',
            'amount_paid',
            'created_at'
        ]

    def get_start_date(self, obj):
        if obj.start_date:
            mm_time = obj.start_date.astimezone(ZoneInfo("Asia/Yangon"))
            return mm_time.strftime("%Y-%m-%d %I:%M:%S %p")
        return None

    def get_end_date(self, obj):
        if obj.end_date:
            mm_time = obj.end_date.astimezone(ZoneInfo("Asia/Yangon"))
            return mm_time.strftime("%Y-%m-%d %I:%M:%S %p")
        return None

    def get_created_at(self, obj):
        if obj.created_at:
            mm_time = obj.created_at.astimezone(ZoneInfo("Asia/Yangon"))
            return mm_time.strftime("%Y-%m-%d %I:%M:%S %p")
        return None
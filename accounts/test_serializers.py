import pytest
from model_bakery import baker

from accounts.models import (
    UUIDPermission,
    UUIDGroup,
    User,
    SubscriptionPlan,
    OwnerProfile,
    PaymentTransaction,
    OwnerSubscriptionHistory,
)

from accounts.serializers import (
    UUIDPermissionSerializer,
    UUIDGroupSerializer,
    UserSerializer,
    SubscriptionPlanSerializer,
    OwnerProfileSerializer,
    PaymentTransactionSerializer,
    OwnerSubscriptionHistorySerializer,
)


pytestmark = pytest.mark.django_db


# ============================================================
# UUIDPermissionSerializer
# ============================================================

def test_uuid_permission_serializer_valid():
    permission = baker.make(
        UUIDPermission,
        name="View Business",
        codename="view_business",
        description="Allows user to view businesses",
    )

    serializer = UUIDPermissionSerializer(instance=permission)

    assert serializer.data["name"] == "View Business"
    assert serializer.data["codename"] == "view_business"
    assert serializer.data["description"] == "Allows user to view businesses"


def test_uuid_permission_serializer_invalid():
    serializer = UUIDPermissionSerializer(
        data={
            "name": "View Business",
        }
    )

    assert serializer.is_valid() is False
    assert "codename" in serializer.errors


# ============================================================
# UUIDGroupSerializer
# ============================================================

def test_uuid_group_serializer_valid():
    permission = baker.make(
        UUIDPermission,
        name="View Business",
        codename="view_business",
    )

    group = baker.make(
        UUIDGroup,
        name="Business Owners",
    )

    group.permissions.add(permission)

    serializer = UUIDGroupSerializer(instance=group)

    assert serializer.data["name"] == "Business Owners"
    assert len(serializer.data["permissions"]) == 1
    assert serializer.data["permissions"][0]["codename"] == "view_business"


def test_uuid_group_serializer_invalid():
    serializer = UUIDGroupSerializer(data={})

    assert serializer.is_valid() is False
    assert "name" in serializer.errors


# ============================================================
# UserSerializer
# ============================================================

def test_user_serializer_valid():
    user = baker.make(
        User,
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
    )

    serializer = UserSerializer(instance=user)

    assert serializer.data["username"] == "testuser"
    assert serializer.data["email"] == "test@example.com"
    assert serializer.data["first_name"] == "Test"
    assert serializer.data["last_name"] == "User"
    assert serializer.data["is_owner"] is False


def test_user_serializer_invalid():
    # UserSerializer contains no required writable fields
    # because it is mainly a read-only representation.
    #
    # Therefore, an empty input is valid.
    serializer = UserSerializer(data={})

    assert serializer.is_valid() is True


# ============================================================
# SubscriptionPlanSerializer
# ============================================================

def test_subscription_plan_serializer_valid():
    plan = baker.make(
        SubscriptionPlan,
        name="Pro",
        max_branches=5,
        price=50000,
        duration_days=30,
        is_active=True,
    )

    serializer = SubscriptionPlanSerializer(instance=plan)

    assert serializer.data["name"] == "Pro"
    assert serializer.data["max_branches"] == 5
    assert serializer.data["price"] == "50000"
    assert serializer.data["duration_days"] == 30
    assert serializer.data["is_active"] is True


def test_subscription_plan_serializer_invalid():
    serializer = SubscriptionPlanSerializer(
        data={
            "name": "Pro",
            "max_branches": 5,
            "price": "invalid-price",
            "duration_days": 30,
            "is_active": True,
        }
    )

    assert serializer.is_valid() is False
    assert "price" in serializer.errors


# ============================================================
# OwnerProfileSerializer
# ============================================================

def test_owner_profile_serializer_valid():
    user = baker.make(
        User,
        username="owneruser",
    )

    plan = baker.make(
        SubscriptionPlan,
        name="Pro",
        price=50000,
    )

    owner = baker.make(
        OwnerProfile,
        user=user,
        current_plan=plan,
        business_name="Test Restaurant",
        phone_number="09123456789",
        is_verified=True,
        auto_renew=True,
    )

    serializer = OwnerProfileSerializer(instance=owner)

    assert serializer.data["business_name"] == "Test Restaurant"
    assert serializer.data["phone_number"] == "09123456789"
    assert serializer.data["is_verified"] is True
    assert serializer.data["auto_renew"] is True

    assert serializer.data["user"]["username"] == "owneruser"
    assert serializer.data["current_plan"]["name"] == "Pro"


def test_owner_profile_serializer_invalid():
    serializer = OwnerProfileSerializer(
        data={
            "business_name": "Test Restaurant",
        }
    )

    # user is read_only and phone_number is required
    assert serializer.is_valid() is False
    assert "phone_number" in serializer.errors


# ============================================================
# PaymentTransactionSerializer
# ============================================================

def test_payment_transaction_serializer_valid():
    user = baker.make(
        User,
        username="paymentowner",
    )

    owner = baker.make(
        OwnerProfile,
        user=user,
        phone_number="09123456789",
    )

    plan = baker.make(
        SubscriptionPlan,
        name="Basic",
        price=20000,
    )

    transaction = baker.make(
        PaymentTransaction,
        owner=owner,
        plan=plan,
        merchant_order_id="ORDER-001",
        transaction_id="TXN-001",
        amount=20000,
        payment_status="SUCCESS",
    )

    serializer = PaymentTransactionSerializer(instance=transaction)

    assert serializer.data["merchant_order_id"] == "ORDER-001"
    assert serializer.data["transaction_id"] == "TXN-001"
    assert serializer.data["amount"] == "20000.00"
    assert serializer.data["payment_status"] == "SUCCESS"

    assert serializer.data["owner_detail"]["user"]["username"] == "paymentowner"
    assert serializer.data["plan_detail"]["name"] == "Basic"


def test_payment_transaction_serializer_invalid():
    serializer = PaymentTransactionSerializer(
        data={
            "merchant_order_id": "ORDER-001",
            "transaction_id": "TXN-001",
            "amount": "not-a-number",
            "payment_status": "SUCCESS",
        }
    )

    assert serializer.is_valid() is False
    assert "amount" in serializer.errors


# ============================================================
# OwnerSubscriptionHistorySerializer
# ============================================================

def test_owner_subscription_history_serializer_valid():
    user = baker.make(
        User,
        username="historyowner",
    )

    owner = baker.make(
        OwnerProfile,
        user=user,
        phone_number="09123456789",
    )

    plan = baker.make(
        SubscriptionPlan,
        name="Enterprise",
        price=100000,
    )

    transaction = baker.make(
        PaymentTransaction,
        owner=owner,
        plan=plan,
        merchant_order_id="ORDER-HISTORY-001",
        amount=100000,
        payment_status="SUCCESS",
    )

    history = baker.make(
        OwnerSubscriptionHistory,
        owner=owner,
        plan=plan,
        payment_transaction=transaction,
        transaction_type="NEW",
        amount_paid=100000,
    )

    serializer = OwnerSubscriptionHistorySerializer(instance=history)

    assert serializer.data["transaction_type"] == "NEW"
    assert serializer.data["amount_paid"] == "100000.00"

    assert serializer.data["owner_detail"]["user"]["username"] == "historyowner"
    assert serializer.data["plan_detail"]["name"] == "Enterprise"

    assert (
        serializer.data["payment_transaction_detail"]["merchant_order_id"]
        == "ORDER-HISTORY-001"
    )


def test_owner_subscription_history_serializer_invalid():
    serializer = OwnerSubscriptionHistorySerializer(
        data={
            "transaction_type": "NEW",
            "amount_paid": "not-a-number",
        }
    )

    assert serializer.is_valid() is False
    assert "owner" in serializer.errors
    assert "plan" in serializer.errors
    assert "amount_paid" in serializer.errors
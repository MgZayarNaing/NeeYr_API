import pytest
from model_bakery import baker

from accounts.models import User
from api.models import (
    RegionState,
    City,
    Category,
    BusinessBrand,
    Branch,
    BranchImage,
    BranchSocialLink,
    BranchReview,
)

from api.serializers import (
    RegionStateSerializer,
    CitySerializer,
    CategorySerializer,
    BranchImageSerializer,
    BranchSocialLinkSerializer,
    BranchReviewSerializer,
    BranchSerializer,
    BusinessBrandSerializer,
)


pytestmark = pytest.mark.django_db


# ============================================================
# RegionStateSerializer
# ============================================================

def test_region_state_serializer_valid():
    region = baker.make(RegionState, name="Mandalay")

    serializer = RegionStateSerializer(instance=region)

    assert serializer.data["name"] == "Mandalay"
    assert "id" in serializer.data


def test_region_state_serializer_invalid():
    serializer = RegionStateSerializer(data={})

    assert serializer.is_valid() is False
    assert "name" in serializer.errors


# ============================================================
# CitySerializer
# ============================================================

def test_city_serializer_valid():
    region = baker.make(RegionState, name="Mandalay")
    city = baker.make(
        City,
        region=region,
        name="Mandalay City"
    )

    serializer = CitySerializer(instance=city)

    assert serializer.data["name"] == "Mandalay City"
    assert serializer.data["region"] == str(region.id)
    assert serializer.data["region_detail"]["name"] == "Mandalay"


def test_city_serializer_invalid():
    serializer = CitySerializer(data={})

    assert serializer.is_valid() is False
    assert "name" in serializer.errors
    assert "region" in serializer.errors


# ============================================================
# CategorySerializer
# ============================================================

def test_category_serializer_valid():
    category = baker.make(
        Category,
        name="Restaurant",
        icon="restaurant-icon"
    )

    serializer = CategorySerializer(instance=category)

    assert serializer.data["name"] == "Restaurant"
    assert serializer.data["icon"] == "restaurant-icon"


def test_category_serializer_invalid():
    serializer = CategorySerializer(data={})

    assert serializer.is_valid() is False
    assert "name" in serializer.errors


# ============================================================
# BranchImageSerializer
# ============================================================

def test_branch_image_serializer_valid():
    branch = baker.make(Branch)

    image = baker.make(
        BranchImage,
        branch=branch
    )

    serializer = BranchImageSerializer(instance=image)

    assert "id" in serializer.data
    assert "image" in serializer.data


def test_branch_image_serializer_invalid():
    serializer = BranchImageSerializer(data={})

    assert serializer.is_valid() is False
    assert "image" in serializer.errors


# ============================================================
# BranchSocialLinkSerializer
# ============================================================

def test_branch_social_link_serializer_valid():
    branch = baker.make(Branch)

    social_link = baker.make(
        BranchSocialLink,
        branch=branch,
        platform_name="FACEBOOK",
        url="https://facebook.com/example"
    )

    serializer = BranchSocialLinkSerializer(instance=social_link)

    assert serializer.data["platform_name"] == "FACEBOOK"
    assert serializer.data["url"] == "https://facebook.com/example"


def test_branch_social_link_serializer_invalid():
    branch = baker.make(Branch)

    serializer = BranchSocialLinkSerializer(
        data={
            "platform_name": "FACEBOOK",
            "url": "not-a-valid-url",
        }
    )

    assert serializer.is_valid() is False
    assert "url" in serializer.errors


# ============================================================
# BranchReviewSerializer
# ============================================================

def test_branch_review_serializer_valid():
    branch = baker.make(Branch)
    user = baker.make(
        User,
        username="testuser"
    )

    review = baker.make(
        BranchReview,
        branch=branch,
        user=user,
        rating=5,
        comment="Great restaurant!"
    )

    serializer = BranchReviewSerializer(instance=review)

    assert serializer.data["rating"] == 5
    assert serializer.data["comment"] == "Great restaurant!"
    assert serializer.data["username"] == "testuser"


def test_branch_review_serializer_invalid():
    serializer = BranchReviewSerializer(
        data={
            "rating": 6,
            "comment": "Great!"
        }
    )

    assert serializer.is_valid() is False
    assert "rating" in serializer.errors


# ============================================================
# BranchSerializer
# ============================================================

def test_branch_serializer_valid():
    branch = baker.make(Branch)

    serializer = BranchSerializer(instance=branch)

    assert serializer.data["branch_name"] == branch.branch_name
    assert serializer.data["brand_name"] == branch.brand.name
    assert "city_detail" in serializer.data
    assert "average_rating" in serializer.data
    assert "total_reviews" in serializer.data
    assert "images" in serializer.data
    assert "social_links" in serializer.data
    assert "created_at" in serializer.data


def test_branch_serializer_invalid():
    serializer = BranchSerializer(data={})

    assert serializer.is_valid() is False

    assert "brand" in serializer.errors
    assert "city" in serializer.errors
    assert "branch_name" in serializer.errors
    assert "address" in serializer.errors
    assert "phone_number" in serializer.errors
    assert "latitude" in serializer.errors
    assert "longitude" in serializer.errors


# ============================================================
# BusinessBrandSerializer
# ============================================================

def test_business_brand_serializer_valid():
    brand = baker.make(BusinessBrand)

    serializer = BusinessBrandSerializer(instance=brand)

    assert serializer.data["name"] == brand.name
    assert "category_detail" in serializer.data
    assert "branches" in serializer.data
    assert "created_at" in serializer.data


def test_business_brand_serializer_invalid():
    serializer = BusinessBrandSerializer(data={})

    assert serializer.is_valid() is False

    assert "owner" in serializer.errors
    assert "category" in serializer.errors
    assert "name" in serializer.errors
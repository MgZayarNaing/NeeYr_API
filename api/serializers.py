from zoneinfo import ZoneInfo
from rest_framework import serializers
from django.db.models import Avg

from .models import (
    RegionState,
    City,
    Category,
    BusinessBrand,
    Branch,
    BranchImage,
    BranchSocialLink,
    BranchReview
)


# 1. Location & Metadata Serializers
class RegionStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegionState
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    region_detail = RegionStateSerializer(source='region', read_only=True)

    class Meta:
        model = City
        fields = ['id', 'name', 'region', 'region_detail']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


# 2. Branch Sub-serializers
class BranchImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BranchImage
        fields = ['id', 'image']


class BranchSocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = BranchSocialLink
        fields = ['id', 'platform_name', 'url']


# 3. Review Serializer
class BranchReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    created_at = serializers.SerializerMethodField()
    replied_at = serializers.SerializerMethodField()

    class Meta:
        model = BranchReview
        fields = [
            'id',
            'branch',
            'user',
            'username',
            'rating',
            'comment',
            'owner_reply',
            'replied_at',
            'is_published',
            'created_at'
        ]
        read_only_fields = ['user', 'is_published']

    def get_created_at(self, obj):
        if obj.created_at:
            return obj.created_at.astimezone(ZoneInfo("Asia/Yangon")).strftime("%Y-%m-%d %I:%M:%S %p")
        return None

    def get_replied_at(self, obj):
        if obj.replied_at:
            return obj.replied_at.astimezone(ZoneInfo("Asia/Yangon")).strftime("%Y-%m-%d %I:%M:%S %p")
        return None


# 4. Main Branch Serializer
class BranchSerializer(serializers.ModelSerializer):
    images = BranchImageSerializer(many=True, read_only=True)
    social_links = BranchSocialLinkSerializer(many=True, read_only=True)
    city_detail = CitySerializer(source='city', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    created_at = serializers.SerializerMethodField()

    # Dynamic Fields for Rating Analytics
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()

    class Meta:
        model = Branch
        fields = [
            'id',
            'brand',
            'brand_name',
            'city',
            'city_detail',
            'branch_name',
            'address',
            'phone_number',
            'opening_hours',
            'latitude',
            'longitude',
            'views_count',
            'status',
            'average_rating',
            'total_reviews',
            'images',
            'social_links',
            'created_at'
        ]

    def get_created_at(self, obj):
        if obj.created_at:
            return obj.created_at.astimezone(ZoneInfo("Asia/Yangon")).strftime("%Y-%m-%d %I:%M:%S %p")
        return None

    def get_average_rating(self, obj):
        avg = obj.reviews.filter(is_published=True).aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0.0

    def get_total_reviews(self, obj):
        return obj.reviews.filter(is_published=True).count()


# 5. Business Brand Serializer
class BusinessBrandSerializer(serializers.ModelSerializer):
    branches = BranchSerializer(many=True, read_only=True)
    category_detail = CategorySerializer(source='category', read_only=True)
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = BusinessBrand
        fields = [
            'id',
            'owner',
            'category',
            'category_detail',
            'name',
            'logo',
            'description',
            'branches',
            'created_at'
        ]

    def get_created_at(self, obj):
        if obj.created_at:
            return obj.created_at.astimezone(ZoneInfo("Asia/Yangon")).strftime("%Y-%m-%d %I:%M:%S %p")
        return None
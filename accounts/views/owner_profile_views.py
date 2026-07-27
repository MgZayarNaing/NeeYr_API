from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth import get_user_model

from accounts.models import OwnerProfile
from accounts.serializers import OwnerProfileSerializer
from accounts.paginations import StandardResultsSetPagination

User = get_user_model()


# ==========================================
# 1. Owner List API (Admin Only) (GET)
# ==========================================
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def owner_list(request):
    """
    Get All Owners List (Super Admin Only)
    - Query Params: search (optional), is_verified (optional boolean), page (optional)
    """
    search_query = request.query_params.get('search', '').strip()
    is_verified_param = request.query_params.get('is_verified', None)

    owners = OwnerProfile.objects.select_related('user', 'current_plan').all().order_by('-id')

    # Search Logic
    if search_query:
        owners = owners.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(business_name__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )

    # Filter by Verification Status
    if is_verified_param is not None:
        is_verified_bool = is_verified_param.lower() in ['true', '1']
        owners = owners.filter(is_verified=is_verified_bool)

    # Pagination
    paginator = StandardResultsSetPagination()
    paginated_owners = paginator.paginate_queryset(owners, request)
    serializer = OwnerProfileSerializer(paginated_owners, many=True)

    return paginator.get_paginated_response(serializer.data)


# ==========================================
# 2. Owner Create API (POST)
# ==========================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def owner_create(request):
    """
    Create Owner Profile for Logged-in User (If not already created)
    - Body Params: business_name, phone_number, logo (optional image file)
    """
    user = request.user

    # Already Owner Profile ရှိပြီးသားလား စစ်ဆေးခြင်း
    if hasattr(user, 'owner_profile'):
        return Response(
            {"error": "ဤ User တွင် Business Owner Profile ရှိပြီးသား ဖြစ်ပါသည်။"},
            status=status.HTTP_400_BAD_REQUEST
        )

    data = request.data
    business_name = data.get('business_name', '').strip()
    phone_number = data.get('phone_number', '').strip()

    # မဖြစ်မနေ ဖြည့်ရမည့် Fields များ စစ်ဆေးခြင်း
    if not business_name or not phone_number:
        return Response(
            {"error": "Business Name နှင့် Phone Number တို့ကို မဖြစ်မနေ ဖြည့်စွက်ပေးရန် လိုအပ်ပါသည်။"},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = OwnerProfileSerializer(data=data, context={'request': request})
    
    if serializer.is_valid():
        # User ကို auto assign လုပ်၍ Save ခြင်း
        serializer.save(user=user)
        return Response({
            "message": "Owner profile အသစ်ကို အောင်မြင်စွာ ဖန်တီးပြီးပါပြီ။",
            "profile": serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ==========================================
# 3. Owner Detail API (GET)
# ==========================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def owner_detail(request, owner_id=None):
    """
    Get Owner Profile Detail
    - If Admin passes owner_id in URL, returns that specific owner.
    - If Normal Owner calls without ID, returns their own profile.
    """
    user = request.user

    # Admin က ID ပေးပြီး ဝင်ခေါ်လျှင်
    if owner_id:
        if not user.is_staff and not user.is_superuser:
            return Response(
                {"error": "ဤ အချက်အလက်ကို ကြည့်ရှုခွင့် မရှိပါ။ (Admin Only)"},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            owner = OwnerProfile.objects.select_related('user', 'current_plan').get(id=owner_id)
        except OwnerProfile.DoesNotExist:
            return Response(
                {"error": "ဤ Owner ID ဖြင့် Profile ရှာမတွေ့ပါ။"},
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        # ကိုယ့် Profile ကိုယ် ပြန်ကြည့်လျှင်
        try:
            owner = OwnerProfile.objects.select_related('user', 'current_plan').get(user=user)
        except OwnerProfile.DoesNotExist:
            return Response(
                {"error": "သင့်အတွက် Owner Profile မရှိသေးပါ။ Profile အသစ် ဖန်တီးပါ။"},
                status=status.HTTP_404_NOT_FOUND
            )

    serializer = OwnerProfileSerializer(owner)
    return Response({
        "message": "Owner အချက်အလက်များကို အောင်မြင်စွာ ရယူပြီးပါပြီ။",
        "owner": serializer.data
    }, status=status.HTTP_200_OK)


# ==========================================
# 4. Owner Update API (PUT / PATCH)
# ==========================================
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def owner_update(request, owner_id=None):
    """
    Update Owner Profile
    - Admin can update any owner by providing owner_id.
    - Owner can update their own profile.
    """
    user = request.user

    if owner_id:
        if not user.is_staff and not user.is_superuser:
            return Response(
                {"error": "ဤ Profile ကို ပြင်ဆင်ခွင့် မရှိပါ။ (Admin Only)"},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            owner = OwnerProfile.objects.get(id=owner_id)
        except OwnerProfile.DoesNotExist:
            return Response(
                {"error": "ဤ Owner ID ဖြင့် Profile ရှာမတွေ့ပါ။"},
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        try:
            owner = OwnerProfile.objects.get(user=user)
        except OwnerProfile.DoesNotExist:
            return Response(
                {"error": "သင့်အတွက် Owner Profile မရှိသေးပါ။"},
                status=status.HTTP_404_NOT_FOUND
            )

    serializer = OwnerProfileSerializer(
        owner,
        data=request.data,
        partial=(request.method == 'PATCH')
    )

    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Owner profile ကို အောင်မြင်စွာ ပြင်ဆင်ပြီးပါပြီ။",
            "owner": serializer.data
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 5. Owner Delete API (DELETE)
# ==========================================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def owner_delete(request, owner_id):
    """
    Delete Owner Profile (Admin Only)
    - Path Param: owner_id (UUID)
    """
    try:
        owner = OwnerProfile.objects.get(id=owner_id)
    except OwnerProfile.DoesNotExist:
        return Response(
            {"error": "ဤ Owner ID ဖြင့် Profile ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    owner.delete()
    return Response(
        {"message": "Owner profile ကို အောင်မြင်စွာ ဖျက်ဆီးပြီးပါပြီ။"},
        status=status.HTTP_200_OK
    )
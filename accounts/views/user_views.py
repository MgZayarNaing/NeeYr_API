from zoneinfo import ZoneInfo
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import update_last_login
from django.db import transaction
from django.db.models import Q

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from accounts.paginations import StandardResultsSetPagination
from accounts.models import OwnerProfile, SubscriptionPlan, UUIDGroup, UUIDPermission
# Simple JWT Import
from rest_framework_simplejwt.tokens import RefreshToken

# Models & Serializers Import
from accounts.models import OwnerProfile, SubscriptionPlan
from accounts.serializers import UserSerializer, OwnerProfileSerializer

# Custom User Model ကို ခေါ်ယူခြင်း (UUID Primary Key)
User = get_user_model()


def get_tokens_for_user(user):
    """
    User အတွက် Access Token နှင့် Refresh Token ထုတ်ပေးသည့် Helper Function
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    """
    User/Owner Login Function (JWT)
    - Request Body: username, password
    - Response: access/refresh tokens, user info
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {"error": "Username နှင့် Password ဖြည့်စွက်ရန် လိုအပ်ပါသည်။"},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)

    if user is not None:
        if not user.is_active:
            return Response(
                {"error": "ဤ အကောင့်သည် ပိတ်ထားခြင်းခံရပါသည်။ (Inactive Account)"},
                status=status.HTTP_403_FORBIDDEN
            )

        # 1. Database ထဲတွင် last_login အချိန်ကို Update လုပ်ခြင်း
        update_last_login(None, user)
        user.refresh_from_db()

        # 2. Simple JWT Tokens ထုတ်ယူခြင်း
        tokens = get_tokens_for_user(user)

        # 3. UserSerializer သုံး၍ Response Format ပြင်ဆင်ခြင်း
        user_serializer = UserSerializer(user)

        return Response({
            "message": "Login အဆင်ပြေစွာ အောင်မြင်ပါသည်။",
            "tokens": tokens,
            "user": user_serializer.data
        }, status=status.HTTP_200_OK)

    else:
        return Response(
            {"error": "Username သို့မဟုတ် Password မှားယွင်းနေပါသည်။"},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def user_register(request):
    """
    User/Owner Registration Function (JWT)
    - Request Body: username, email, password, is_owner (optional), phone_number (if is_owner)
    - Response: access/refresh tokens, user info
    """
    data = request.data
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    is_owner = data.get('is_owner', False)
    phone_number = data.get('phone_number', '')

    # Validation Checks
    if not username or not email or not password:
        return Response(
            {"error": "Username, Email နှင့် Password တို့ မဖြစ်မနေ ဖြည့်စွက်ပေးရန် လိုအပ်ပါသည်။"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "ဤ Username ကို အခြားသူ အသုံးပြုထားပြီး ဖြစ်ပါသည်။"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {"error": "ဤ Email ကို အခြားသူ အသုံးပြုထားပြီး ဖြစ်ပါသည်။"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if is_owner and not phone_number:
        return Response(
            {"error": "Business Owner အကောင့်ပြုလုပ်ရန် ဖုန်းနံပါတ် ဖြည့်စွက်ရန် လိုအပ်ပါသည်။"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Database Operation (Atomic Transaction)
    try:
        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            if is_owner:
                default_plan = SubscriptionPlan.objects.filter(is_active=True).first()

                OwnerProfile.objects.create(
                    user=user,
                    phone_number=phone_number,
                    current_plan=default_plan
                )

            tokens = get_tokens_for_user(user)
            user_serializer = UserSerializer(user)

            return Response({
                "message": "အကောင့်သစ် အောင်မြင်စွာ ဖွင့်လှစ်ပြီးပါပြီ။",
                "tokens": tokens,
                "user": user_serializer.data
            }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {"error": f"အကောင့်ပြုလုပ်ရာတွင် အမှားတစ်ခု ဖြစ်ပေါ်ခဲ့သည်: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_list(request):
    """
    User List API (Authenticated Users Only)
    - Query Params: search (optional), page (optional)
    """
    search_query = request.query_params.get('search', '').strip()

    # 🔹 Custom Groups နဲ့ Permissions များကို N+1 Query ဖြစ်မသွားစေရန် prefetch_related သုံးထားသည်
    users = User.objects.prefetch_related(
        'custom_groups__permissions', 
        'custom_permissions'
    ).all().order_by('-date_joined')

    # Search Logic
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) | 
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    # Pagination Logic
    paginator = StandardResultsSetPagination()
    paginated_users = paginator.paginate_queryset(users, request)

    # Serializer မှတစ်ဆင့် Groups & Permissions ပါဝင်သော Data ထုတ်ယူခြင်း
    serializer = UserSerializer(paginated_users, many=True)

    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_detail(request, user_id):
    """
    User Detail API (Authenticated Users Only)
    - Path Param: user_id (UUID string)
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {"error": "ဤ User ID ဖြင့် အကောင့် ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    user_serializer = UserSerializer(user)
    data = user_serializer.data

    # Owner Profile အချက်အလက်များပါ စစ်ဆေးပြီး ထည့်ပေးခြင်း
    if hasattr(user, 'owner_profile'):
        owner_serializer = OwnerProfileSerializer(user.owner_profile)
        data['owner_profile'] = owner_serializer.data

    return Response({
        "message": "User အချက်အလက်များကို အောင်မြင်စွာ ရယူပြီးပါပြီ။",
        "user": data
    }, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def get_user_update(request, user_id):
    """
    User Update API (PUT / PATCH)
    - Path Param: user_id (UUID)
    - Body Params: first_name, last_name, email, is_active, groups (list of UUIDs), permissions (list of UUIDs)
    """
    try:
        user = User.objects.prefetch_related(
            'custom_groups__permissions', 
            'custom_permissions'
        ).get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {"error": "ဤ User ID ဖြင့် အကောင့် ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    data = request.data

    # 1. Email ထပ်နေခြင်း ရှိ/မရှိ စစ်ဆေးခြင်း
    email = data.get('email', '').strip()
    if email and email != user.email:
        if User.objects.filter(email=email).exclude(id=user_id).exists():
            return Response(
                {"error": "ဤ Email ကို အခြား User အသုံးပြုထားပြီး ဖြစ်ပါသည်။"},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.email = email

    # 2. Basic Fields မ်ား Update လုပ်ခြင်း
    if 'first_name' in data:
        user.first_name = data.get('first_name', '').strip()
    if 'last_name' in data:
        user.last_name = data.get('last_name', '').strip()
    if 'is_active' in data:
        user.is_active = data.get('is_active')

    user.save()

    # 3. Groups Update လုပ်ခြင်း (form-data သို့မဟုတ် raw JSON နှစ်မျိုးလုံး အဆင်ပြေအောင် ယူထားသည်)
    if hasattr(data, 'getlist'):
        group_ids = data.getlist('groups') if 'groups' in data else data.get('groups', None)
    else:
        group_ids = data.get('groups', None)

    if isinstance(group_ids, str):
        group_ids = [group_ids]

    if group_ids is not None and isinstance(group_ids, list):
        valid_groups = UUIDGroup.objects.filter(id__in=group_ids)
        user.custom_groups.set(valid_groups)

    # 4. Direct Permissions Update လုပ်ခြင်း
    if hasattr(data, 'getlist'):
        permission_ids = data.getlist('permissions') if 'permissions' in data else data.get('permissions', None)
    else:
        permission_ids = data.get('permissions', None)

    if isinstance(permission_ids, str):
        permission_ids = [permission_ids]

    if permission_ids is not None and isinstance(permission_ids, list):
        valid_permissions = UUIDPermission.objects.filter(id__in=permission_ids)
        user.custom_permissions.set(valid_permissions)

    # 5. Updated Data ပြန်လည် Response ထုတ်ပေးခြင်း
    serializer = UserSerializer(user)
    return Response({
        "message": "User အချက်အလက်များကို အောင်မြင်စွာ ပြင်ဆင်ပြီးပါပြီ။",
        "user": serializer.data
    }, status=status.HTTP_200_OK)
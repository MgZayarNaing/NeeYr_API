from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db.models import Q

from accounts.models import UUIDGroup, UUIDPermission
from accounts.serializers import UUIDGroupSerializer
from accounts.paginations import StandardResultsSetPagination

# ==========================================
# 1. Group List API (GET)
# ==========================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def group_list(request):
    """
    Get All Groups (Supports Search & Pagination)
    - Query Params: search (optional), page (optional), page_size (optional)
    """
    search_query = request.query_params.get('search', '').strip()
    groups = UUIDGroup.objects.prefetch_related('permissions').all().order_by('name')

    # Search Filter
    if search_query:
        groups = groups.filter(name__icontains=search_query)

    # 🔹 Pagination Logic ထည့်သွင်းခြင်း
    paginator = StandardResultsSetPagination()
    paginated_groups = paginator.paginate_queryset(groups, request)

    # Serializer မှတစ်ဆင့် Clean Data ထုတ်ယူခြင်း
    serializer = UUIDGroupSerializer(paginated_groups, many=True)

    # Paginated Response Return ပြန်ခြင်း (count, next, previous, results တို့ပါဝင်ပါမည်)
    return paginator.get_paginated_response(serializer.data)


# ==========================================
# 2. Group Detail API (GET)
# ==========================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def group_detail(request, group_id):
    """
    Get Single Group Detail by UUID
    """
    try:
        group = UUIDGroup.objects.prefetch_related('permissions').get(id=group_id)
    except UUIDGroup.DoesNotExist:
        return Response(
            {"error": "ဤ Group ID ဖြင့် Group ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = UUIDGroupSerializer(group)
    return Response({
        "message": "Group အချက်အလက်များကို အောင်မြင်စွာ ရယူပြီးပါပြီ။",
        "group": serializer.data
    }, status=status.HTTP_200_OK)


# ==========================================
# 3. Group Create API (POST)
# ==========================================
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def group_create(request):
    """
    Create New Group
    - Body Params: name (required), permissions (optional list or single string of UUIDs)
    """
    name = request.data.get('name', '').strip()
    
    # 🔹 form-data သို့မဟုတ် raw json နှစ်မျိုးလုံးအတွက် getlist သို့မဟုတ် request.data မှ ယူခြင်း
    if hasattr(request.data, 'getlist'):
        permission_ids = request.data.getlist('permissions') or request.data.get('permissions', [])
    else:
        permission_ids = request.data.get('permissions', [])

    # အကယ်၍ Single String အဖြစ် ဝင်လာပါက List အဖြစ် ပြောင်းပေးခြင်း
    if isinstance(permission_ids, str):
        permission_ids = [permission_ids]

    if not name:
        return Response(
            {"error": "Group နာမည် (name) ထည့်သွင်းရန် လိုအပ်ပါသည်။"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if UUIDGroup.objects.filter(name__iexact=name).exists():
        return Response(
            {"error": "ဤ Group နာမည် ရှိပြီးသား ဖြစ်ပါသည်။"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 1. Group အသစ်ဆောက်ခြင်း
    group = UUIDGroup.objects.create(name=name)

    # 2. Permissions များ ပါရှိပါက တပါတည်း ချိတ်ဆက်ပေးခြင်း
    if permission_ids and isinstance(permission_ids, list):
        valid_permissions = UUIDPermission.objects.filter(id__in=permission_ids)
        group.permissions.set(valid_permissions)

    serializer = UUIDGroupSerializer(group)
    return Response({
        "message": "Group အသစ်ကို အောင်မြင်စွာ ဖန်တီးပြီးပါပြီ။",
        "group": serializer.data
    }, status=status.HTTP_201_CREATED)


# ==========================================
# 4. Group Update API (PUT / PATCH)
# ==========================================
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated, IsAdminUser])
def group_update(request, group_id):
    """
    Update Group Name or Permissions
    - Path Param: group_id (UUID)
    - Body Params: name (optional), permissions (optional list of UUIDs)
    """
    try:
        group = UUIDGroup.objects.get(id=group_id)
    except UUIDGroup.DoesNotExist:
        return Response(
            {"error": "ဤ Group ID ဖြင့် Group ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    name = request.data.get('name', '').strip()
    
    # 🔹 form-data သို့မဟုတ် raw JSON နှစ်မျိုးလုံးမှ permission_ids ကို ခွဲခြားရယူခြင်း
    if hasattr(request.data, 'getlist'):
        permission_ids = request.data.getlist('permissions') or request.data.get('permissions', None)
    else:
        permission_ids = request.data.get('permissions', None)

    # Single String အဖြစ် ဝင်လာပါက List အဖြစ် အော်တို ပြောင်းပေးခြင်း
    if isinstance(permission_ids, str):
        permission_ids = [permission_ids]

    # 1. Group Name ပြောင်းလဲခြင်း
    if name:
        if UUIDGroup.objects.filter(name__iexact=name).exclude(id=group_id).exists():
            return Response(
                {"error": "ဤ Group နာမည် အခြား Group တွင် ရှိပြီးသား ဖြစ်ပါသည်။"},
                status=status.HTTP_400_BAD_REQUEST
            )
        group.name = name
        group.save()

    # 2. Permissions များကို Update လုပ်ခြင်း
    if permission_ids is not None and isinstance(permission_ids, list):
        valid_permissions = UUIDPermission.objects.filter(id__in=permission_ids)
        group.permissions.set(valid_permissions)

    serializer = UUIDGroupSerializer(group)
    return Response({
        "message": "Group အချက်အလက်များကို အောင်မြင်စွာ ပြင်ဆင်ပြီးပါပြီ။",
        "group": serializer.data
    }, status=status.HTTP_200_OK)


# ==========================================
# 5. Group Delete API (DELETE)
# ==========================================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def group_delete(request, group_id):
    """
    Delete Group by UUID
    """
    try:
        group = UUIDGroup.objects.get(id=group_id)
    except UUIDGroup.DoesNotExist:
        return Response(
            {"error": "ဤ Group ID ဖြင့် Group ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    group_name = group.name
    group.delete()

    return Response({
        "message": f"'{group_name}' Group ကို အောင်မြင်စွာ ဖျက်ပစ်ပြီးပါပြီ။"
    }, status=status.HTTP_200_OK)
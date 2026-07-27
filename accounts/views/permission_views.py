from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import UUIDPermission
from accounts.serializers import UUIDPermissionSerializer


# ==========================================
# 1. Permission List API (GET)
# ==========================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def permission_list(request):
    """
    Get All Permissions
    - Query Params: search (optional)
    """
    search_query = request.query_params.get('search', '').strip()
    permissions = UUIDPermission.objects.all().order_by('name')

    # Search Logic (Name သို့မဟုတ် Codename ဖြင့် ရှာဖွေနိုင်ခြင်း)
    if search_query:
        permissions = permissions.filter(
            name__icontains=search_query
        ) | permissions.filter(
            codename__icontains=search_query
        )

    serializer = UUIDPermissionSerializer(permissions, many=True)
    
    return Response({
        "message": "Permission စာရင်းကို အောင်မြင်စွာ ရယူပြီးပါပြီ။",
        "count": permissions.count(),
        "permissions": serializer.data
    }, status=status.HTTP_200_OK)


# ==========================================
# 2. Permission Detail API (GET)
# ==========================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def permission_detail(request, permission_id):
    """
    Get Single Permission Detail by UUID
    """
    try:
        permission = UUIDPermission.objects.get(id=permission_id)
    except UUIDPermission.DoesNotExist:
        return Response(
            {"error": "ဤ Permission ID ဖြင့် ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = UUIDPermissionSerializer(permission)
    
    return Response({
        "message": "Permission အချက်အလက်များကို အောင်မြင်စွာ ရယူပြီးပါပြီ။",
        "permission": serializer.data
    }, status=status.HTTP_200_OK)
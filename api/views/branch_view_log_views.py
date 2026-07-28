from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.models import BranchViewLog, Branch
from api.serializers import serializers
from accounts.paginations import StandardResultsSetPagination


# ==========================================
# BranchViewLog Serializer (Local or inside serializers.py)
# ==========================================
class BranchViewLogSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.branch_name', read_only=True)
    username = serializers.SerializerMethodField()
    viewed_at = serializers.SerializerMethodField()

    class Meta:
        model = BranchViewLog
        fields = ['id', 'branch', 'branch_name', 'user', 'username', 'viewed_at']
        read_only_fields = ['user']

    def get_username(self, obj):
        if obj.user:
            return getattr(obj.user, 'username', str(obj.user))
        return "Anonymous"

    def get_viewed_at(self, obj):
        if obj.viewed_at:
            from zoneinfo import ZoneInfo
            return obj.viewed_at.astimezone(ZoneInfo("Asia/Yangon")).strftime("%Y-%m-%d %I:%M:%S %p")
        return None


# ==========================================
# 1. Get BranchViewLog List (GET)
# ==========================================
@api_view(['GET'])
@permission_classes([IsAuthenticated]) # Admin သို့မဟုတ် Owner များသာ ကြည့်ခွင့်ပြုရန်
def get_branch_view_log_list(request):
    """
    Branch View Log စာရင်းအားလုံးကို ရယူရန် (Branch အလိုက် သို့မဟုတ် User အလိုက် Filter နှင့် Pagination ပါဝင်သည်)
    """
    branch_id = request.query_params.get('branch_id', '').strip()
    user_id = request.query_params.get('user_id', '').strip()

    logs = BranchViewLog.objects.select_related('branch', 'user').all().order_by('-viewed_at')

    # Branch အလိုက် Filter လုပ်ရန်
    if branch_id:
        logs = logs.filter(branch_id=branch_id)

    # User အလိုက် Filter လုပ်ရန်
    if user_id:
        logs = logs.filter(user_id=user_id)

    paginator = StandardResultsSetPagination()
    paginated_data = paginator.paginate_queryset(logs, request)
    serializer = BranchViewLogSerializer(paginated_data, many=True)
    
    return paginator.get_paginated_response(serializer.data)


# ==========================================
# 2. Create BranchViewLog (POST) - (User က Branch တစ်ခုကို ဝင်ကြည့်လိုက်တိုင်း မှတ်တမ်းတင်ရန်)
# ==========================================
@api_view(['POST'])
@permission_classes([AllowAny]) # Login မဝင်ထားသူ (Anonymous) လည်း ဝင်ကြည့်နိုင်သဖြင့် AllowAny ပေးထားသည်
def get_branch_view_log_create(request):
    """
    Branch View Log အသစ် ဖန်တီးရန် (User ဝင်ကြည့်တိုင်း ခေါ်ရန်)
    - Body: { "branch": "uuid-string" }
    """
    serializer = BranchViewLogSerializer(data=request.data)
    if serializer.is_valid():
        # Login ဝင်ထားပါက User ကို ထည့်ပေးပြီး၊ မဝင်ထားလျှင် None (Anonymous) ဖြစ်စေသည်
        user = request.user if request.user.is_authenticated else None
        serializer.save(user=user)
        
        return Response({
            "message": "Branch view log recorded successfully.",
            "view_log": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        "error": "အချက်အလက်များ မမှန်ကန်ပါ။",
        "details": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 3. Get BranchViewLog Detail (GET)
# ==========================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_branch_view_log_detail(request, pk):
    """
    BranchViewLog အသေးစိတ် အချက်အလက် ရယူရန်
    """
    try:
        log_obj = BranchViewLog.objects.select_related('branch', 'user').get(pk=pk)
    except BranchViewLog.DoesNotExist:
        return Response(
            {"error": "ဤ ID ဖြင့် Branch View Log ကို ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = BranchViewLogSerializer(log_obj)
    return Response({
        "message": "Branch View Log အချက်အလက်များကို အောင်မြင်စွာ ရယူပြီးပါပြီ။",
        "view_log": serializer.data
    }, status=status.HTTP_200_OK)


# ==========================================
# 4. Delete BranchViewLog (DELETE)
# ==========================================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def get_branch_view_log_delete(request, pk):
    """
    BranchViewLog မှတ်တမ်းကို ဖျက်ရန်
    """
    try:
        log_obj = BranchViewLog.objects.get(pk=pk)
    except BranchViewLog.DoesNotExist:
        return Response(
            {"error": "ဤ ID ဖြင့် Branch View Log ကို ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    log_obj.delete()
    return Response({
        "message": "Branch View Log ကို အောင်မြင်စွာ ဖျက်လိုက်ပါပြီ။"
    }, status=status.HTTP_204_NO_CONTENT)
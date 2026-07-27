from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db.models import Q

from accounts.models import SubscriptionPlan
from accounts.serializers import SubscriptionPlanSerializer
from accounts.paginations import StandardResultsSetPagination


# ==========================================
# 1. Plan List API (GET)
# ==========================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def plan_list(request):
    """
    Get All Subscription Plans (Supports Search & Pagination)
    - Query Params: search (optional), active_only (optional boolean)
    """
    search_query = request.query_params.get('search', '').strip()
    active_only = request.query_params.get('active_only', None)

    plans = SubscriptionPlan.objects.all().order_by('price')

    # Search Logic (Name)
    if search_query:
        plans = plans.filter(name__icontains=search_query)

    # Filter only active plans if requested (e.g., for mobile/frontend checkout view)
    if active_only is not None:
        is_active_bool = active_only.lower() in ['true', '1']
        plans = plans.filter(is_active=is_active_bool)

    # Pagination
    paginator = StandardResultsSetPagination()
    paginated_plans = paginator.paginate_queryset(plans, request)
    serializer = SubscriptionPlanSerializer(paginated_plans, many=True)

    return paginator.get_paginated_response(serializer.data)


# ==========================================
# 2. Plan Detail API (GET)
# ==========================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def plan_detail(request, plan_id):
    """
    Get Single Subscription Plan Detail by UUID
    """
    try:
        plan = SubscriptionPlan.objects.get(id=plan_id)
    except SubscriptionPlan.DoesNotExist:
        return Response(
            {"error": "ဤ Subscription Plan ID ဖြင့် ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = SubscriptionPlanSerializer(plan)
    return Response({
        "message": "Plan အချက်အလက်များကို အောင်မြင်စွာ ရယူပြီးပါပြီ။",
        "plan": serializer.data
    }, status=status.HTTP_200_OK)


# ==========================================
# 3. Plan Create API (POST)
# ==========================================
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def plan_create(request):
    """
    Create New Subscription Plan (Admin Only)
    - Body Params: name, max_branches, price, duration_days, is_active (optional)
    """
    data = request.data
    name = data.get('name', '').strip()

    if not name:
        return Response(
            {"error": "Plan နာမည် (name) ထည့်သွင်းရန် လိုအပ်ပါသည်။"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if SubscriptionPlan.objects.filter(name__iexact=name).exists():
        return Response(
            {"error": "ဤ Plan နာမည် ရှိပြီးသား ဖြစ်ပါသည်။"},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = SubscriptionPlanSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Subscription Plan အသစ်ကို အောင်မြင်စွာ ဖန်တီးပြီးပါပြီ။",
            "plan": serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 4. Plan Update API (PUT / PATCH)
# ==========================================
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated, IsAdminUser])
def plan_update(request, plan_id):
    """
    Update Subscription Plan (Admin Only)
    - Path Param: plan_id (UUID)
    - Body Params: name, max_branches, price, duration_days, is_active
    """
    try:
        plan = SubscriptionPlan.objects.get(id=plan_id)
    except SubscriptionPlan.DoesNotExist:
        return Response(
            {"error": "ဤ Subscription Plan ID ဖြင့် ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    name = request.data.get('name', '').strip()
    if name and name.lower() != plan.name.lower():
        if SubscriptionPlan.objects.filter(name__iexact=name).exclude(id=plan_id).exists():
            return Response(
                {"error": "ဤ Plan နာမည် အခြား Plan တွင် ရှိပြီးသား ဖြစ်ပါသည်။"},
                status=status.HTTP_400_BAD_REQUEST
            )

    serializer = SubscriptionPlanSerializer(
        plan, 
        data=request.data, 
        partial=(request.method == 'PATCH')
    )
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Subscription Plan ကို အောင်မြင်စွာ ပြင်ဆင်ပြီးပါပြီ။",
            "plan": serializer.data
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 5. Plan Delete API (DELETE)
# ==========================================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def plan_delete(request, plan_id):
    """
    Delete Subscription Plan (Admin Only)
    """
    try:
        plan = SubscriptionPlan.objects.get(id=plan_id)
    except SubscriptionPlan.DoesNotExist:
        return Response(
            {"error": "ဤ Subscription Plan ID ဖြင့် ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Owner တွေ လက်ရှိ အသုံးပြုနေဆဲ Plan ဖြစ်ပါက Delete လုပ်ခွင့် မပေးဘဲ Inactive ပဲ လုပ်ခိုင်းခြင်း
    if plan.ownerprofile_set.exists():
        return Response(
            {"error": "ဤ Plan ကို အသုံးပြုထားသော Owner Profile များ ရှိနေပါသဖြင့် ဖျက်၍ မရပါ။ is_active ကို False ဖြင့်သာ ပြောင်းလဲပေးပါ။"},
            status=status.HTTP_400_BAD_REQUEST
        )

    plan.delete()
    return Response(
        {"message": "Subscription Plan ကို အောင်မြင်စွာ ဖျက်ကူးပြီးပါပြီ။"},
        status=status.HTTP_200_OK
    )
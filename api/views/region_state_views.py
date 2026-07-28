from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.models import RegionState
from api.serializers import RegionStateSerializer
from accounts.paginations import StandardResultsSetPagination


# ==========================================
# 1. Get RegionState List (GET)
# ==========================================
@api_view(['GET'])
@permission_classes([AllowAny]) # လိုအပ်ပါက IsAuthenticated သို့ ပြောင်းနိုင်ပါသည်
def get_region_state_list(request):
    """
    Region/State စာရင်းအားလုံးကို ရယူရန် (Search နှင့် Pagination ပါဝင်သည်)
    """
    search_query = request.query_params.get('search', '').strip()
    regions = RegionState.objects.all().order_by('name')

    # Search Logic (နာမည်ဖြင့် ရှာဖွေနိုင်ခြင်း)
    if search_query:
        regions = regions.filter(name__icontains=search_query)

    paginator = StandardResultsSetPagination()
    paginated_data = paginator.paginate_queryset(regions, request)
    serializer = RegionStateSerializer(paginated_data, many=True)
    
    return paginator.get_paginated_response(serializer.data)


# ==========================================
# 2. Create RegionState (POST)
# ==========================================
@api_view(['POST'])
@permission_classes([AllowAny])
def get_region_state_create(request):
    """
    Region/State အသစ် တစ်ခု ဖန်တီးရန်
    """
    serializer = RegionStateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Region/State ကို အောင်မြင်စွာ ဖန်တီးပြီးပါပြီ။",
            "region_state": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        "error": "အချက်အလက်များ မမှန်ကန်ပါ။",
        "details": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 3. Get RegionState Detail (GET)
# ==========================================
@api_view(['GET'])
@permission_classes([AllowAny])
def get_region_state_detail(request, pk):
    """
    Region/State အသေးစိတ် အချက်အလက် ရယူရန်
    """
    try:
        region = RegionState.objects.get(pk=pk)
    except RegionState.DoesNotExist:
        return Response(
            {"error": "ဤ ID ဖြင့် Region/State ကို ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = RegionStateSerializer(region)
    return Response({
        "message": "Region/State အချက်အလက်များကို အောင်မြင်စွာ ရယူပြီးပါပြီ။",
        "region_state": serializer.data
    }, status=status.HTTP_200_OK)


# ==========================================
# 4. Update RegionState (PUT)
# ==========================================
@api_view(['PUT'])
@permission_classes([AllowAny])
def get_region_state_update(request, pk):
    """
    Region/State အချက်အလက် ပြင်ဆင်ရန်
    """
    try:
        region = RegionState.objects.get(pk=pk)
    except RegionState.DoesNotExist:
        return Response(
            {"error": "ဤ ID ဖြင့် Region/State ကို ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = RegionStateSerializer(region, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Region/State အချက်အလက်များကို အောင်မြင်စွာ ပြင်ဆင်ပြီးပါပြီ။",
            "region_state": serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        "error": "ပြင်ဆင်၍ မရပါ။ အချက်အလက်များကို စစ်ဆေးပါ။",
        "details": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 5. Delete RegionState (DELETE)
# ==========================================
@api_view(['DELETE'])
@permission_classes([AllowAny])
def get_region_state_delete(request, pk):
    """
    Region/State ကို ဖျက်ရန်
    """
    try:
        region = RegionState.objects.get(pk=pk)
    except RegionState.DoesNotExist:
        return Response(
            {"error": "ဤ ID ဖြင့် Region/State ကို ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    region.delete()
    return Response({
        "message": "Region/State ကို အောင်မြင်စွာ ဖျက်လိုက်ပါပြီ။"
    }, status=status.HTTP_204_NO_CONTENT)
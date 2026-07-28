from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Avg

from api.models import Branch
from api.serializers import BranchSerializer
from accounts.paginations import StandardResultsSetPagination


# ==========================================
# 1. Get Branch List (GET)
# ==========================================
@api_view(['GET'])
@permission_classes([AllowAny])
def get_branch_list(request):
    """
    Branch စာရင်းအားလုံးကို ရယူရန် (Search, Brand, City, Status အလိုက် Filter နှင့် Pagination ပါဝင်သည်)
    """
    search_query = request.query_params.get('search', '').strip()
    brand_id = request.query_params.get('brand_id', '').strip()
    city_id = request.query_params.get('city_id', '').strip()
    status_filter = request.query_params.get('status', '').strip()

    branches = Branch.objects.select_related('brand', 'city').prefetch_related('images', 'social_links', 'reviews').all().order_by('-created_at')

    # Search Logic (Branch Name သို့မဟုတ် Address ဖြင့် ရှာဖွေခြင်း)
    if search_query:
        branches = branches.filter(branch_name__icontains=search_query) | branches.filter(address__icontains=search_query)

    # Brand အလိုက် Filter လုပ်ရန်
    if brand_id:
        branches = branches.filter(brand_id=brand_id)

    # City အလိုက် Filter လုပ်ရန်
    if city_id:
        branches = branches.filter(city_id=city_id)

    # Status အလိုက် Filter လုပ်ရန် (ဥပမာ: ACTIVE)
    if status_filter:
        branches = branches.filter(status=status_filter)

    paginator = StandardResultsSetPagination()
    paginated_data = paginator.paginate_queryset(branches, request)
    serializer = BranchSerializer(paginated_data, many=True, context={'request': request})
    
    return paginator.get_paginated_response(serializer.data)


# ==========================================
# 2. Create Branch (POST)
# ==========================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_branch_create(request):
    """
    Branch အသစ် တစ်ခု ဖန်တီးရန်
    """
    serializer = BranchSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Branch ကို အောင်မြင်စွာ ဖန်တီးပြီးပါပြီ။",
            "branch": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        "error": "အချက်အလက်များ မမှန်ကန်ပါ။",
        "details": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 3. Get Branch Detail (GET)
# ==========================================
@api_view(['GET'])
@permission_classes([AllowAny])
def get_branch_detail(request, pk):
    """
    Branch အသေးစိတ် အချက်အလက် ရယူရန် (ကြည့်ရှုသည့်အကြိမ်ရေ views_count ကိုပါ တစ်ခါတည်း တိုးပေးသည်)
    """
    try:
        branch = Branch.objects.select_related('brand', 'city').prefetch_related('images', 'social_links', 'reviews').get(pk=pk)
    except Branch.DoesNotExist:
        return Response(
            {"error": "ဤ ID ဖြင့် Branch ကို ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Views Count တိုးခြင်း
    branch.views_count += 1
    branch.save(update_fields=['views_count'])

    serializer = BranchSerializer(branch, context={'request': request})
    return Response({
        "message": "Branch အချက်အလက်များကို အောင်မြင်စွာ ရယူပြီးပါပြီ။",
        "branch": serializer.data
    }, status=status.HTTP_200_OK)


# ==========================================
# 4. Update Branch (PUT)
# ==========================================
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def get_branch_update(request, pk):
    """
    Branch အချက်အလက် ပြင်ဆင်ရန်
    """
    try:
        branch = Branch.objects.get(pk=pk)
    except Branch.DoesNotExist:
        return Response(
            {"error": "ဤ ID ဖြင့် Branch ကို ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = BranchSerializer(branch, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Branch အချက်အလက်များကို အောင်မြင်စွာ ပြင်ဆင်ပြီးပါပြီ။",
            "branch": serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        "error": "ပြင်ဆင်၍ မရပါ။ အချက်အလက်များကို စစ်ဆေးပါ။",
        "details": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 5. Delete Branch (DELETE)
# ==========================================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def get_branch_delete(request, pk):
    """
    Branch ကို ဖျက်ရန်
    """
    try:
        branch = Branch.objects.get(pk=pk)
    except Branch.DoesNotExist:
        return Response(
            {"error": "ဤ ID ဖြင့် Branch ကို ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    branch.delete()
    return Response({
        "message": "Branch ကို အောင်မြင်စွာ ဖျက်လိုက်ပါပြီ။"
    }, status=status.HTTP_204_NO_CONTENT)
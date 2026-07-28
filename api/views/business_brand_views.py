from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.models import BusinessBrand
from api.serializers import BusinessBrandSerializer
from accounts.paginations import StandardResultsSetPagination


# ==========================================
# 1. Get BusinessBrand List (GET)
# ==========================================
@api_view(['GET'])
@permission_classes([AllowAny])
def get_business_brand_list(request):
    """
    BusinessBrand စာရင်းအားလုံးကို ရယူရန် (Search, Category, Owner အလိုက် Filter နှင့် Pagination ပါဝင်သည်)
    """
    search_query = request.query_params.get('search', '').strip()
    category_id = request.query_params.get('category_id', '').strip()
    owner_id = request.query_params.get('owner_id', '').strip()

    brands = BusinessBrand.objects.select_related('owner', 'category').prefetch_related('branches').all().order_by('-created_at')

    # Search Logic (နာမည် သို့မဟုတ် ော်ဖော်ချက်ဖြင့် ရှာဖွေခြင်း)
    if search_query:
        brands = brands.filter(name__icontains=search_query)

    # Category အလိုက် Filter လုပ်ရန်
    if category_id:
        brands = brands.filter(category_id=category_id)

    # Owner အလိုက် Filter လုပ်ရန်
    if owner_id:
        brands = brands.filter(owner_id=owner_id)

    paginator = StandardResultsSetPagination()
    paginated_data = paginator.paginate_queryset(brands, request)
    serializer = BusinessBrandSerializer(paginated_data, many=True)
    
    return paginator.get_paginated_response(serializer.data)


# ==========================================
# 2. Create BusinessBrand (POST)
# ==========================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_business_brand_create(request):
    """
    BusinessBrand အသစ် တစ်ခု ဖန်တီးရန် (Image/Logo ပါဝင်နိုင်သဖြင့် request.data ကို အသုံးပြုသည်)
    """
    serializer = BusinessBrandSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Business Brand ကို အောင်မြင်စွာ ဖန်တီးပြီးပါပြီ။",
            "business_brand": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        "error": "အချက်အလက်များ မမှန်ကန်ပါ။",
        "details": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 3. Get BusinessBrand Detail (GET)
# ==========================================
@api_view(['GET'])
@permission_classes([AllowAny])
def get_business_brand_detail(request, pk):
    """
    BusinessBrand အသေးစိတ် အချက်အလက် ရယူရန်
    """
    try:
        brand = BusinessBrand.objects.select_related('owner', 'category').prefetch_related('branches').get(pk=pk)
    except BusinessBrand.DoesNotExist:
        return Response(
            {"error": "ဤ ID ဖြင့် Business Brand ကို ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = BusinessBrandSerializer(brand, context={'request': request})
    return Response({
        "message": "Business Brand အချက်အလက်များကို အောင်မြင်စွာ ရယူပြီးပါပြီ။",
        "business_brand": serializer.data
    }, status=status.HTTP_200_OK)


# ==========================================
# 4. Update BusinessBrand (PUT)
# ==========================================
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def get_business_brand_update(request, pk):
    """
    BusinessBrand အချက်အလက် ပြင်ဆင်ရန်
    """
    try:
        brand = BusinessBrand.objects.get(pk=pk)
    except BusinessBrand.DoesNotExist:
        return Response(
            {"error": "ဤ ID ဖြင့် Business Brand ကို ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = BusinessBrandSerializer(brand, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Business Brand အချက်အလက်များကို အောင်မြင်စွာ ပြင်ဆင်ပြီးပါပြီ။",
            "business_brand": serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        "error": "ပြင်ဆင်၍ မရပါ။ အချက်အလက်များကို စစ်ဆေးပါ။",
        "details": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 5. Delete BusinessBrand (DELETE)
# ==========================================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def get_business_brand_delete(request, pk):
    """
    BusinessBrand ကို ဖျက်ရန်
    """
    try:
        brand = BusinessBrand.objects.get(pk=pk)
    except BusinessBrand.DoesNotExist:
        return Response(
            {"error": "ဤ ID ဖြင့် Business Brand ကို ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    brand.delete()
    return Response({
        "message": "Business Brand ကို အောင်မြင်စွာ ဖျက်လိုက်ပါပြီ။"
    }, status=status.HTTP_204_NO_CONTENT)
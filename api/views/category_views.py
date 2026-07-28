from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.models import Category
from api.serializers import CategorySerializer
from accounts.paginations import StandardResultsSetPagination


# ==========================================
# 1. Get Category List (GET)
# ==========================================
@api_view(['GET'])
@permission_classes([AllowAny])
def get_category_list(request):
    """
    Category စာရင်းအားလုံးကို ရယူရန် (Search နှင့် Pagination ပါဝင်သည်)
    """
    search_query = request.query_params.get('search', '').strip()
    categories = Category.objects.all().order_by('name')

    # Search Logic (နာမည်ဖြင့် ရှာဖွေခြင်း)
    if search_query:
        categories = categories.filter(name__icontains=search_query)

    paginator = StandardResultsSetPagination()
    paginated_data = paginator.paginate_queryset(categories, request)
    serializer = CategorySerializer(paginated_data, many=True)
    
    return paginator.get_paginated_response(serializer.data)


# ==========================================
# 2. Create Category (POST)
# ==========================================
@api_view(['POST'])
@permission_classes([AllowAny])
def get_category_create(request):
    """
    Category အသစ် တစ်ခု ဖန်တီးရန်
    """
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Category ကို အောင်မြင်စွာ ဖန်တီးပြီးပါပြီ။",
            "category": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        "error": "အချက်အလက်များ မမှန်ကန်ပါ။",
        "details": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 3. Get Category Detail (GET)
# ==========================================
@api_view(['GET'])
@permission_classes([AllowAny])
def get_category_detail(request, pk):
    """
    Category အသေးစိတ် အချက်အလက် ရယူရန်
    """
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response(
            {"error": "ဤ ID ဖြင့် Category ကို ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = CategorySerializer(category)
    return Response({
        "message": "Category အချက်အလက်များကို အောင်မြင်စွာ ရယူပြီးပါပြီ။",
        "category": serializer.data
    }, status=status.HTTP_200_OK)


# ==========================================
# 4. Update Category (PUT)
# ==========================================
@api_view(['PUT'])
@permission_classes([AllowAny])
def get_category_update(request, pk):
    """
    Category အချက်အလက် ပြင်ဆင်ရန်
    """
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response(
            {"error": "ဤ ID ဖြင့် Category ကို ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = CategorySerializer(category, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Category အချက်အလက်များကို အောင်မြင်စွာ ပြင်ဆင်ပြီးပါပြီ။",
            "category": serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        "error": "ပြင်ဆင်၍ မရပါ။ အချက်အလက်များကို စစ်ဆေးပါ။",
        "details": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 5. Delete Category (DELETE)
# ==========================================
@api_view(['DELETE'])
@permission_classes([AllowAny])
def get_category_delete(request, pk):
    """
    Category ကို ဖျက်ရန်
    """
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response(
            {"error": "ဤ ID ဖြင့် Category ကို ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    category.delete()
    return Response({
        "message": "Category ကို အောင်မြင်စွာ ဖျက်လိုက်ပါပြီ။"
    }, status=status.HTTP_204_NO_CONTENT)
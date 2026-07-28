from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.models import City, RegionState
from api.serializers import CitySerializer
from accounts.paginations import StandardResultsSetPagination


# ==========================================
# 1. Get City List (GET)
# ==========================================
@api_view(['GET'])
@permission_classes([AllowAny])
def get_city_list(request):
    """
    City စာရင်းအားလုံးကို ရယူရန် (Search, Region အလိုက် Filter နှင့် Pagination ပါဝင်သည်)
    """
    search_query = request.query_params.get('search', '').strip()
    region_id = request.query_params.get('region_id', '').strip()
    
    cities = City.objects.select_related('region').all().order_by('name')

    # Search Logic (မြို့နာမည်ဖြင့် ရှာဖွေခြင်း)
    if search_query:
        cities = cities.filter(name__icontains=search_query)

    # Region အလိုက် Filter လုပ်လိုပါက
    if region_id:
        cities = cities.filter(region_id=region_id)

    paginator = StandardResultsSetPagination()
    paginated_data = paginator.paginate_queryset(cities, request)
    serializer = CitySerializer(paginated_data, many=True)
    
    return paginator.get_paginated_response(serializer.data)


# ==========================================
# 2. Create City (POST)
# ==========================================
@api_view(['POST'])
@permission_classes([AllowAny])
def get_city_create(request):
    """
    City အသစ် တစ်ခု ဖန်တီးရန်
    - Body: { "name": "Yangon", "region": "uuid-string" }
    """
    serializer = CitySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "City ကို အောင်မြင်စွာ ဖန်တီးပြီးပါပြီ။",
            "city": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        "error": "အချက်အလက်များ မမှန်ကန်ပါ။",
        "details": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 3. Get City Detail (GET)
# ==========================================
@api_view(['GET'])
@permission_classes([AllowAny])
def get_city_detail(request, pk):
    """
    City အသေးစိတ် အချက်အလက် ရယူရန်
    """
    try:
        city = City.objects.select_related('region').get(pk=pk)
    except City.DoesNotExist:
        return Response(
            {"error": "ဤ ID ဖြင့် City ကို ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = CitySerializer(city)
    return Response({
        "message": "City အချက်အလက်များကို အောင်မြင်စွာ ရယူပြီးပါပြီ။",
        "city": serializer.data
    }, status=status.HTTP_200_OK)


# ==========================================
# 4. Update City (PUT)
# ==========================================
@api_view(['PUT'])
@permission_classes([AllowAny])
def get_city_update(request, pk):
    """
    City အချက်အလက် ပြင်ဆင်ရန်
    """
    try:
        city = City.objects.get(pk=pk)
    except City.DoesNotExist:
        return Response(
            {"error": "ဤ ID ဖြင့် City ကို ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = CitySerializer(city, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "City အချက်အလက်များကို အောင်မြင်စွာ ပြင်ဆင်ပြီးပါပြီ။",
            "city": serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        "error": "ပြင်ဆင်၍ မရပါ။ အချက်အလက်များကို စစ်ဆေးပါ။",
        "details": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 5. Delete City (DELETE)
# ==========================================
@api_view(['DELETE'])
@permission_classes([AllowAny])
def get_city_delete(request, pk):
    """
    City ကို ဖျက်ရန်
    """
    try:
        city = City.objects.get(pk=pk)
    except City.DoesNotExist:
        return Response(
            {"error": "ဤ ID ဖြင့် City ကို ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    city.delete()
    return Response({
        "message": "City ကို အောင်မြင်စွာ ဖျက်လိုက်ပါပြီ။"
    }, status=status.HTTP_204_NO_CONTENT)
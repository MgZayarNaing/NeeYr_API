from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.models import BranchImage
from api.serializers import BranchImageSerializer
from accounts.paginations import StandardResultsSetPagination


# ==========================================
# 1. Get BranchImage List (GET)
# ==========================================
@api_view(['GET'])
@permission_classes([AllowAny])
def get_branch_image_list(request):
    """
    BranchImage စာရင်းအားလုံးကို ရယူရန် (Branch အလိုက် Filter နှင့် Pagination ပါဝင်သည်)
    """
    branch_id = request.query_params.get('branch_id', '').strip()
    images = BranchImage.objects.select_related('branch').all()

    # Branch အလိုက် Filter လုပ်ရန်
    if branch_id:
        images = images.filter(branch_id=branch_id)

    paginator = StandardResultsSetPagination()
    paginated_data = paginator.paginate_queryset(images, request)
    serializer = BranchImageSerializer(paginated_data, many=True, context={'request': request})
    
    return paginator.get_paginated_response(serializer.data)


# ==========================================
# 2. Create BranchImage (POST)
# ==========================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_branch_image_create(request):
    """
    BranchImage အသစ် တစ်ခု ဖန်တီးရန် (ပုံ တင်ခြင်းဖြစ်သဖြင့် request.data နှင့် request.FILES ကို အသုံးပြုသည်)
    """
    serializer = BranchImageSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Branch Image ကို အောင်မြင်စွာ ဖန်တီးပြီးပါပြီ။",
            "branch_image": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        "error": "အချက်အလက်များ မမှန်ကန်ပါ။",
        "details": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 3. Get BranchImage Detail (GET)
# ==========================================
@api_view(['GET'])
@permission_classes([AllowAny])
def get_branch_image_detail(request, pk):
    """
    BranchImage အသေးစိတ် အချက်အလက် ရယူရန်
    """
    try:
        image_obj = BranchImage.objects.select_related('branch').get(pk=pk)
    except BranchImage.DoesNotExist:
        return Response(
            {"error": "ဤ ID ဖြင့် Branch Image ကို ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = BranchImageSerializer(image_obj, context={'request': request})
    return Response({
        "message": "Branch Image အချက်အလက်များကို အောင်မြင်စွာ ရယူပြီးပါပြီ။",
        "branch_image": serializer.data
    }, status=status.HTTP_200_OK)


# ==========================================
# 4. Update BranchImage (PUT)
# ==========================================
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def get_branch_image_update(request, pk):
    """
    BranchImage အချက်အလက် ပြင်ဆင်ရန် (ပုံအသစ်ဖြင့် အစားထိုးရန်)
    """
    try:
        image_obj = BranchImage.objects.get(pk=pk)
    except BranchImage.DoesNotExist:
        return Response(
            {"error": "ဤ ID ဖြင့် Branch Image ကို ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = BranchImageSerializer(image_obj, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Branch Image အချက်အလက်များကို အောင်မြင်စွာ ပြင်ဆင်ပြီးပါပြီ။",
            "branch_image": serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        "error": "ပြင်ဆင်၍ မရပါ။ အချက်အလက်များကို စစ်ဆေးပါ။",
        "details": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 5. Delete BranchImage (DELETE)
# ==========================================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def get_branch_image_delete(request, pk):
    """
    BranchImage ကို ဖျက်ရန်
    """
    try:
        image_obj = BranchImage.objects.get(pk=pk)
    except BranchImage.DoesNotExist:
        return Response(
            {"error": "ဤ ID ဖြင့် Branch Image ကို ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    image_obj.delete()
    return Response({
        "message": "Branch Image ကို အောင်မြင်စွာ ဖျက်လိုက်ပါပြီ။"
    }, status=status.HTTP_204_NO_CONTENT)
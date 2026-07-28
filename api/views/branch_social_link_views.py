from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.models import BranchSocialLink
from api.serializers import BranchSocialLinkSerializer
from accounts.paginations import StandardResultsSetPagination


# ==========================================
# 1. Get BranchSocialLink List (GET)
# ==========================================
@api_view(['GET'])
@permission_classes([AllowAny])
def get_branch_social_link_list(request):
    """
    BranchSocialLink စာရင်းအားလုံးကို ရယူရန် (Branch အလိုက် သို့မဟုတ် Platform အလိုက် Filter နှင့် Pagination ပါဝင်သည်)
    """
    branch_id = request.query_params.get('branch_id', '').strip()
    platform_name = request.query_params.get('platform_name', '').strip()
    
    links = BranchSocialLink.objects.select_related('branch').all()

    # Branch အလိုက် Filter လုပ်ရန်
    if branch_id:
        links = links.filter(branch_id=branch_id)

    # Platform အလိုက် Filter လုပ်ရန် (ဥပမာ: FACEBOOK, TELEGRAM)
    if platform_name:
        links = links.filter(platform_name__iexact=platform_name)

    paginator = StandardResultsSetPagination()
    paginated_data = paginator.paginate_queryset(links, request)
    serializer = BranchSocialLinkSerializer(paginated_data, many=True)
    
    return paginator.get_paginated_response(serializer.data)


# ==========================================
# 2. Create BranchSocialLink (POST)
# ==========================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_branch_social_link_create(request):
    """
    BranchSocialLink အသစ် တစ်ခု ဖန်တီးရန်
    """
    serializer = BranchSocialLinkSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Branch Social Link ကို အောင်မြင်စွာ ဖန်တီးပြီးပါပြီ။",
            "social_link": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        "error": "အချက်အလက်များ မမှန်ကန်ပါ။",
        "details": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 3. Get BranchSocialLink Detail (GET)
# ==========================================
@api_view(['GET'])
@permission_classes([AllowAny])
def get_branch_social_link_detail(request, pk):
    """
    BranchSocialLink အသေးစိတ် အချက်အလက် ရယူရန်
    """
    try:
        link_obj = BranchSocialLink.objects.select_related('branch').get(pk=pk)
    except BranchSocialLink.DoesNotExist:
        return Response(
            {"error": "ဤ ID ဖြင့် Branch Social Link ကို ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = BranchSocialLinkSerializer(link_obj)
    return Response({
        "message": "Branch Social Link အချက်အလက်များကို အောင်မြင်စွာ ရယူပြီးပါပြီ။",
        "social_link": serializer.data
    }, status=status.HTTP_200_OK)


# ==========================================
# 4. Update BranchSocialLink (PUT)
# ==========================================
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def get_branch_social_link_update(request, pk):
    """
    BranchSocialLink အချက်အလက် ပြင်ဆင်ရန်
    """
    try:
        link_obj = BranchSocialLink.objects.get(pk=pk)
    except BranchSocialLink.DoesNotExist:
        return Response(
            {"error": "ဤ ID ဖြင့် Branch Social Link ကို ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = BranchSocialLinkSerializer(link_obj, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Branch Social Link အချက်အလက်များကို အောင်မြင်စွာ ပြင်ဆင်ပြီးပါပြီ။",
            "social_link": serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        "error": "ပြင်ဆင်၍ မရပါ။ အချက်အလက်များကို စစ်ဆေးပါ။",
        "details": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 5. Delete BranchSocialLink (DELETE)
# ==========================================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def get_branch_social_link_delete(request, pk):
    """
    BranchSocialLink ကို ဖျက်ရန်
    """
    try:
        link_obj = BranchSocialLink.objects.get(pk=pk)
    except BranchSocialLink.DoesNotExist:
        return Response(
            {"error": "ဤ ID ဖြင့် Branch Social Link ကို ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    link_obj.delete()
    return Response({
        "message": "Branch Social Link ကို အောင်မြင်စွာ ဖျက်လိုက်ပါပြီ။"
    }, status=status.HTTP_204_NO_CONTENT)
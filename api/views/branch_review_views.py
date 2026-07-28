from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone

from api.models import BranchReview
from api.serializers import BranchReviewSerializer
from accounts.paginations import StandardResultsSetPagination


# ==========================================
# 1. Get BranchReview List (GET)
# ==========================================
@api_view(['GET'])
@permission_classes([AllowAny])
def get_branch_review_list(request):
    """
    Branch Review စာရင်းအားလုံးကို ရယူရန် (Branch အလိုက်, User အလိုက် သို့မဟုတ် Rating အလိုက် Filter နှင့် Pagination ပါဝင်သည်)
    """
    branch_id = request.query_params.get('branch_id', '').strip()
    user_id = request.query_params.get('user_id', '').strip()
    rating = request.query_params.get('rating', '').strip()

    reviews = BranchReview.objects.select_related('branch', 'user').filter(is_published=True).order_by('-created_at')

    # Branch အလိုက် Filter လုပ်ရန်
    if branch_id:
        reviews = reviews.filter(branch_id=branch_id)

    # User အလိုက် Filter လုပ်ရန်
    if user_id:
        reviews = reviews.filter(user_id=user_id)

    # Rating အလိုက် Filter လုပ်ရန် (ဥပမာ: 5 ကြယ်ပွင့်များသာ)
    if rating:
        reviews = reviews.filter(rating=rating)

    paginator = StandardResultsSetPagination()
    paginated_data = paginator.paginate_queryset(reviews, request)
    serializer = BranchReviewSerializer(paginated_data, many=True, context={'request': request})
    
    return paginator.get_paginated_response(serializer.data)


# ==========================================
# 2. Create BranchReview (POST)
# ==========================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_branch_review_create(request):
    """
    Branch Review အသစ် တစ်ခု ဖန်တီးရန် (Login ဝင်ထားသော User ကို အလိုအလျောက် သတ်မှတ်ပေးသည်)
    """
    serializer = BranchReviewSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        # Review ပို့သူ User ကို request.user မှ ယူ၍ အလိုအလျောက် ထည့်သွင်းပေးခြင်း
        serializer.save(user=request.user)
        return Response({
            "message": "Review ကို အောင်မြင်စွာ တင်သွင်းပြီးပါပြီ။",
            "review": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        "error": "အချက်အလက်များ မမှန်ကန်ပါ။",
        "details": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 3. Get BranchReview Detail (GET)
# ==========================================
@api_view(['GET'])
@permission_classes([AllowAny])
def get_branch_review_detail(request, pk):
    """
    Branch Review အသေးစိတ် အချက်အလက် ရယူရန်
    """
    try:
        review = BranchReview.objects.select_related('branch', 'user').get(pk=pk)
    except BranchReview.DoesNotExist:
        return Response(
            {"error": "ဤ ID ဖြင့် Review ကို ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = BranchReviewSerializer(review, context={'request': request})
    return Response({
        "message": "Review အချက်အလက်များကို အောင်မြင်စွာ ရယူပြီးပါပြီ။",
        "review": serializer.data
    }, status=status.HTTP_200_OK)


# ==========================================
# 4. Update BranchReview / Owner Reply (PUT)
# ==========================================
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def get_branch_review_update(request, pk):
    """
    Review ပြင်ဆင်ခြင်း (သို့မဟုတ်) Business Owner မှ Reply ပြန်ခြင်း
    """
    try:
        review = BranchReview.objects.get(pk=pk)
    except BranchReview.DoesNotExist:
        return Response(
            {"error": "ဤ ID ဖြင့် Review ကို ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    # အကယ်၍ owner_reply ပါလာခဲ့လျှင် replied_at အချိန်ကို လက်ရှိအချိန်ဖြင့် အလိုအလျောက် မှတ်တမ်းတင်ပေးသည်
    data = request.data.copy()
    if 'owner_reply' in data and data['owner_reply']:
        data['replied_at'] = timezone.now()

    serializer = BranchReviewSerializer(review, data=data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Review အချက်အလက်များကို အောင်မြင်စွာ ပြင်ဆင်ပြီးပါပြီ။",
            "review": serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        "error": "ပြင်ဆင်၍ မရပါ။ အချက်အလက်များကို စစ်ဆေးပါ။",
        "details": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 5. Delete BranchReview (DELETE)
# ==========================================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def get_branch_review_delete(request, pk):
    """
    Branch Review ကို ဖျက်ရန်
    """
    try:
        review = BranchReview.objects.get(pk=pk)
    except BranchReview.DoesNotExist:
        return Response(
            {"error": "ဤ ID ဖြင့် Review ကို ရှာမတွေ့ပါ။"},
            status=status.HTTP_404_NOT_FOUND
        )

    # (Optional) Review တင်ခဲ့တဲ့ User ကိုယ်တိုင် (သို့မဟုတ်) Admin ဖြစ်မှ ဖျက်ခွင့်ပေးချင်ပါက ဤနေရာတွင် စစ်ဆေးနိုင်ပါသည်
    # if review.user != request.user and not request.user.is_staff:
    #     return Response({"error": "ဤ Review ကို ဖျက်ရန် ခွင့်ပြုချက်မရှိပါ။"}, status=status.HTTP_403_FORBIDDEN)

    review.delete()
    return Response({
        "message": "Review ကို အောင်မြင်စွာ ဖျက်လိုက်ပါပြီ။"
    }, status=status.HTTP_204_NO_CONTENT)
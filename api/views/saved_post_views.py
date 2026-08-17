from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.models import SavedPost
from api.serializers import SavedPostSerializer
from accounts.paginations import StandardResultsSetPagination


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_saved_post_list(request):
    user_id = request.query_params.get('user_id', '').strip()
    post_id = request.query_params.get('post_id', '').strip()

    saved_posts = SavedPost.objects.select_related('user', 'post').all().order_by('-created_at')

    if user_id:
        saved_posts = saved_posts.filter(user_id=user_id)
    if post_id:
        saved_posts = saved_posts.filter(post_id=post_id)

    paginator = StandardResultsSetPagination()
    paginated_data = paginator.paginate_queryset(saved_posts, request)
    serializer = SavedPostSerializer(paginated_data, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_saved_post_create(request):
    serializer = SavedPostSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response({
            "message": "Saved post created successfully.",
            "saved_post": serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response({
        "error": "Invalid data provided.",
        "details": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_saved_post_detail(request, pk):
    try:
        saved_post = SavedPost.objects.select_related('user', 'post').get(pk=pk)
    except SavedPost.DoesNotExist:
        return Response(
            {"error": "Saved post not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = SavedPostSerializer(saved_post, context={'request': request})
    return Response({
        "message": "Saved post retrieved successfully.",
        "saved_post": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def get_saved_post_delete(request, pk):
    try:
        saved_post = SavedPost.objects.get(pk=pk)
    except SavedPost.DoesNotExist:
        return Response(
            {"error": "Saved post not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    saved_post.delete()
    return Response({
        "message": "Saved post deleted successfully."
    }, status=status.HTTP_204_NO_CONTENT)

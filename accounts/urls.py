from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views.user_views import (
    user_login,
    user_register,
    get_user_list,
    get_user_detail,
    get_user_update
)


from accounts.views.permission_views import (
    permission_list,
    permission_detail
)

from accounts.views.group_views import (
    group_list,
    group_detail,
    group_create,
    group_update,
    group_delete
)

urlpatterns = [
    path('login/', user_login, name='user-login'),
    path('register/', user_register, name='user-register'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('users/', get_user_list, name='user-list'),
    path('users/<uuid:user_id>/', get_user_detail, name='get_user_detail'),
    path('users/<uuid:user_id>/update/', get_user_update, name='get_user_update'),

    # Permission Endpoints
    path('permissions/', permission_list, name='permission_list'),
    path('permissions/<uuid:permission_id>/', permission_detail, name='permission_detail'),

    # Group Endpoints
    path('groups/', group_list, name='group_list'),
    path('groups/create/', group_create, name='group_create'),
    path('groups/<uuid:group_id>/', group_detail, name='group_detail'),
    path('groups/<uuid:group_id>/update/', group_update, name='group_update'),
    path('groups/<uuid:group_id>/delete/', group_delete, name='group_delete'),
]
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

from accounts.views.subscription_plan_views import (
    plan_list,
    plan_detail,
    plan_create,
    plan_update,
    plan_delete,
)

from accounts.views.owner_profile_views import (
    owner_list,
    owner_create,
    owner_detail,
    owner_update,
    owner_delete,
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


    # Subscription Plan Endpoints
    path('plans/', plan_list, name='plan_list'),
    path('plans/create/', plan_create, name='plan_create'),
    path('plans/<uuid:plan_id>/', plan_detail, name='plan_detail'),
    path('plans/<uuid:plan_id>/update/', plan_update, name='plan_update'),
    path('plans/<uuid:plan_id>/delete/', plan_delete, name='plan_delete'),

    # Owner Self-Management Endpoints
    path('profile/', owner_detail, name='owner_profile_detail'),           # Get own profile
    path('profile/create/', owner_create, name='owner_profile_create'),     # Create own profile
    path('profile/update/', owner_update, name='owner_profile_update'),     # Update own profile

    # Admin Management Endpoints
    path('owners/', owner_list, name='owner_list'),                         # Get all owners list
    path('owners/<uuid:owner_id>/', owner_detail, name='owner_detail_admin'), # Get specific owner detail
    path('owners/<uuid:owner_id>/update/', owner_update, name='owner_update_admin'), # Update specific owner
    path('owners/<uuid:owner_id>/delete/', owner_delete, name='owner_delete'), # Delete owner
]
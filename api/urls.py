from django.urls import path
from api.views.region_state_views import (
    get_region_state_list,
    get_region_state_create,
    get_region_state_detail,
    get_region_state_update,
    get_region_state_delete
)

from api.views.city_views import (
    get_city_list,
    get_city_create,
    get_city_detail,
    get_city_update,
    get_city_delete
)

from api.views.category_views import (
    get_category_list,
    get_category_create,
    get_category_detail,
    get_category_update,
    get_category_delete
)

from api.views.business_brand_views import (
    get_business_brand_list,
    get_business_brand_create,
    get_business_brand_detail,
    get_business_brand_update,
    get_business_brand_delete
)

from api.views.branch_views import (
    get_branch_list,
    get_branch_create,
    get_branch_detail,
    get_branch_update,
    get_branch_delete
)

from api.views.branch_image_views import (
    get_branch_image_list,
    get_branch_image_create,
    get_branch_image_detail,
    get_branch_image_update,
    get_branch_image_delete
)

from api.views.branch_social_link_views import (
    get_branch_social_link_list,
    get_branch_social_link_create,
    get_branch_social_link_detail,
    get_branch_social_link_update,
    get_branch_social_link_delete
)

from api.views.branch_view_log_views import (
    get_branch_view_log_list,
    get_branch_view_log_create,
    get_branch_view_log_detail,
    get_branch_view_log_delete
)

from api.views.branch_review_views import (
    get_branch_review_list,
    get_branch_review_create,
    get_branch_review_detail,
    get_branch_review_update,
    get_branch_review_delete
)

from api.views.saved_post_views import (
    get_saved_post_list,
    get_saved_post_create,
    get_saved_post_detail,
    get_saved_post_delete
)

urlpatterns = [
    # Region State
    path('regions/', get_region_state_list, name='region-state-list'),
    path('regions/create/', get_region_state_create, name='region-state-create'),
    path('regions/<uuid:pk>/', get_region_state_detail, name='region-state-detail'),
    path('regions/<uuid:pk>/update/', get_region_state_update, name='region-state-update'),
    path('regions/<uuid:pk>/delete/', get_region_state_delete, name='region-state-delete'),

    path('cities/', get_city_list, name='city-list'),
    path('cities/create/', get_city_create, name='city-create'),
    path('cities/<uuid:pk>/', get_city_detail, name='city-detail'),
    path('cities/<uuid:pk>/update/', get_city_update, name='city-update'),
    path('cities/<uuid:pk>/delete/', get_city_delete, name='city-delete'),

    path('categories/', get_category_list, name='category-list'),
    path('categories/create/', get_category_create, name='category-create'),
    path('categories/<uuid:pk>/', get_category_detail, name='category-detail'),
    path('categories/<uuid:pk>/update/', get_category_update, name='category-update'),
    path('categories/<uuid:pk>/delete/', get_category_delete, name='category-delete'),

    path('business-brands/', get_business_brand_list, name='business-brand-list'),
    path('business-brands/create/', get_business_brand_create, name='business-brand-create'),
    path('business-brands/<uuid:pk>/', get_business_brand_detail, name='business-brand-detail'),
    path('business-brands/<uuid:pk>/update/', get_business_brand_update, name='business-brand-update'),
    path('business-brands/<uuid:pk>/delete/', get_business_brand_delete, name='business-brand-delete'),

    path('branches/', get_branch_list, name='branch-list'),
    path('branches/create/', get_branch_create, name='branch-create'),
    path('branches/<uuid:pk>/', get_branch_detail, name='branch-detail'),
    path('branches/<uuid:pk>/update/', get_branch_update, name='branch-update'),
    path('branches/<uuid:pk>/delete/', get_branch_delete, name='branch-delete'),

    path('branch-images/', get_branch_image_list, name='branch-image-list'),
    path('branch-images/create/', get_branch_image_create, name='branch-image-create'),
    path('branch-images/<uuid:pk>/', get_branch_image_detail, name='branch-image-detail'),
    path('branch-images/<uuid:pk>/update/', get_branch_image_update, name='branch-image-update'),
    path('branch-images/<uuid:pk>/delete/', get_branch_image_delete, name='branch-image-delete'),

    path('branch-social-links/', get_branch_social_link_list, name='branch-social-link-list'),
    path('branch-social-links/create/', get_branch_social_link_create, name='branch-social-link-create'),
    path('branch-social-links/<uuid:pk>/', get_branch_social_link_detail, name='branch-social-link-detail'),
    path('branch-social-links/<uuid:pk>/update/', get_branch_social_link_update, name='branch-social-link-update'),
    path('branch-social-links/<uuid:pk>/delete/', get_branch_social_link_delete, name='branch-social-link-delete'),

    path('branch-view-logs/', get_branch_view_log_list, name='branch-view-log-list'),
    path('branch-view-logs/create/', get_branch_view_log_create, name='branch-view-log-create'),
    path('branch-view-logs/<uuid:pk>/', get_branch_view_log_detail, name='branch-view-log-detail'),
    path('branch-view-logs/<uuid:pk>/delete/', get_branch_view_log_delete, name='branch-view-log-delete'),

    path('branch-reviews/', get_branch_review_list, name='branch-review-list'),
    path('branch-reviews/create/', get_branch_review_create, name='branch-review-create'),
    path('branch-reviews/<uuid:pk>/', get_branch_review_detail, name='branch-review-detail'),
    path('branch-reviews/<uuid:pk>/update/', get_branch_review_update, name='branch-review-update'),
    path('branch-reviews/<uuid:pk>/delete/', get_branch_review_delete, name='branch-review-delete'),

    path('save-posts/', get_saved_post_list, name='saved-post-list'),
    path('save-posts/create/', get_saved_post_create, name='saved-post-create'),
    path('save-posts/<uuid:pk>/', get_saved_post_detail, name='saved-post-detail'),
    path('save-posts/<uuid:pk>/delete/', get_saved_post_delete, name='saved-post-delete'),
]

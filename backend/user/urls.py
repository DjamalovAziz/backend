# backend\user\urls.py:

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings

#
from .views import UserViewSet, CustomTokenObtainPairView

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")

urlpatterns = [
    path("users/signin/", CustomTokenObtainPairView.as_view(), name="signin"),
    path("users/refresh_token/", TokenRefreshView.as_view(), name="refresh_token"),
    # Single Avatar scenario
    path(
        "users/my/avatar/",
        UserViewSet.as_view({"delete": "delete_my_avatar"}),
        name="delete_my_avatar",
    ),
    # Multiple Avatar scenario
    path(
        "users/my/avatars/",
        UserViewSet.as_view({"get": "get_my_avatars"}),
        name="get_my_avatars",
    ),
    path(
        "users/me/avatar/",
        UserViewSet.as_view({"post": "post_me_avatar"}),
        name="post_me_avatar",
    ),
    path(
        "users/me/avatars/<uuid:avatar_id>/",
        UserViewSet.as_view({"patch": "update_avatar", "delete": "delete_avatar"}),
        name="avatar_detail",
    ),
    path(
        "users/<uuid:pk>/avatars/",
        UserViewSet.as_view({"get": "get_user_avatars"}),
        name="user_avatars",
    ),
    path("", include(router.urls)),
]

# # Добавляем эндпоинты в зависимости от режима
# if settings.AVATAR_MULTIPLE_MODE:
#     # Multiple Avatar сценарий
#     urlpatterns += [
#         path(
#             "users/me/avatars/",
#             UserViewSet.as_view({"get": "get_my_avatars", "post": "post_me_avatar"}),
#             name="get_my_avatars",
#         ),
#         path(
#             "users/me/avatars/<uuid:avatar_id>/",
#             UserViewSet.as_view({"patch": "update_avatar", "delete": "delete_avatar"}),
#             name="avatar_detail",
#         ),
#         path(
#             "users/<uuid:pk>/avatars/",
#             UserViewSet.as_view({"get": "get_user_avatars"}),
#             name="user_avatars",
#         ),
#     ]
# else:
#     # Single Avatar сценарий
#     urlpatterns += [
#         path(
#             "users/my/avatar/",
#             UserViewSet.as_view({"delete": "delete_avatar"}),
#             name="delete_avatar",
#         ),
#     ]

# # Остальные URL
# urlpatterns += [
#     path("", include(router.urls)),
# ]

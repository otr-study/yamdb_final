from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (CategoriesViewSet, CommentViewSet, GenresViewSet,
                       ReviewViewSet, TitlesViewSet, UserViewSet, jwt_token,
                       registration_user)

router_v1 = DefaultRouter()

router_v1.register('genres', GenresViewSet)
router_v1.register('categories', CategoriesViewSet)
router_v1.register('titles', TitlesViewSet)
router_v1.register(
    r'titles/(?P<title_id>[\d]+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>[\d]+)/reviews/(?P<review_id>[\d]+)/comments',
    CommentViewSet,
    basename='comments'
)
router_v1.register('users', UserViewSet)


urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/', registration_user, name='registration'),
    path('v1/auth/token/', jwt_token, name='token')
]

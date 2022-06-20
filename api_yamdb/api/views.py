from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Categories, Genres, Review, Title, User

from .filters import TitleFilter
from .permissions import (AdminOrReadOnly, AuthorModeratorAdminOrReadOnly,
                          IsAdmin)
from .serializers import (CategoriesSerializer, CommentSerializer,
                          GenresSerializer, JwtTokenSerializer,
                          RegistrationUserSerializer, ReviewSerializer,
                          TitlesCreateSerializer, TitlesReadSerializer,
                          UserSerializer)


def generate_and_send_confirmation_code(user):
    """Генерация кода подтверждения и отправка по email."""
    confirmation_code = default_token_generator.make_token(user)
    user.confirmation_code = confirmation_code
    subject = 'Код подтверждения'
    message = f'Код подтверждения для регистрации: {confirmation_code}'
    sender_address = settings.YAMDB_SUPPORT_EMAIL
    receiver_address = [user.email]
    return send_mail(
        subject,
        message,
        sender_address,
        receiver_address,
        fail_silently=False,
    )


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def jwt_token(request):
    serializer = JwtTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    confirmation_code = serializer.validated_data['confirmation_code']
    user = get_object_or_404(User, username=username)
    if not default_token_generator.check_token(
        user,
        confirmation_code
    ) and user.confirmation_code != confirmation_code:
        return Response(
            {'confirmation_code': ['Ошибочный код подтверждения']},
            status=status.HTTP_400_BAD_REQUEST
        )

    token = RefreshToken.for_user(user)
    return Response(
        {'token': str(token.access_token)}, status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def registration_user(request):
    serializer = RegistrationUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    email = serializer.validated_data['email']
    try:
        user, created = User.objects.get_or_create(
            email=email, username=username
        )
    except Exception:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    generate_and_send_confirmation_code(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdmin,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_or_update_self(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)

        serializer = self.get_serializer(
            instance=request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        if (not user.is_admin
                and not user.is_moderator
                and 'role' in serializer.validated_data):
            serializer.validated_data.pop('role')
        serializer.save()
        return Response(serializer.data)


class ListCreateDeleteViewSet(mixins.ListModelMixin,
                              mixins.CreateModelMixin,
                              mixins.DestroyModelMixin,
                              viewsets.GenericViewSet):
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (AdminOrReadOnly,)
    lookup_field = 'slug'


class GenresViewSet(ListCreateDeleteViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer


class CategoriesViewSet(ListCreateDeleteViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('id')
    serializer_class = TitlesReadSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitlesReadSerializer
        return TitlesCreateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = (
        AuthorModeratorAdminOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly
    )

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    permission_classes = (
        AuthorModeratorAdminOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly
    )

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id')
        )
        serializer.save(author=self.request.user, review=review)

import datetime as dt

from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from reviews.models import Categories, Comment, Genres, Review, Title, User


class JwtTokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()


class RegistrationUserSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
    )
    email = serializers.EmailField(
        required=True,
        max_length=254,
    )

    class Meta:
        fields = ('email', 'username')
        model = User

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Использовать имя `me` в качестве username запрещено.'
            )
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        model = User


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ('name', 'slug')


class GenresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genres
        fields = ('name', 'slug')


class TitlesReadSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)
    genre = GenresSerializer(read_only=True, many=True)
    category = CategoriesSerializer(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'
        read_only_fields = ('__all__',)

    def validate_year(self, value):
        current_year = dt.date.today().year
        if current_year < value < 0:
            raise serializers.ValidationError(
                ('Год создания произведения не может быть меньше 0'
                 ' и больше текущего года')
            )
        return value


class TitlesCreateSerializer(serializers.ModelSerializer):
    genre = SlugRelatedField(
        slug_field='slug',
        queryset=Genres.objects.all(),
        many=True
    )
    category = SlugRelatedField(
        slug_field='slug',
        queryset=Categories.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = '__all__'
        model = Review
        read_only_fields = ('id', 'title', 'author', 'pub_date',)

    def validate_score(self, value):
        if not (1 <= value <= 10):
            raise serializers.ValidationError(
                'Поле "score" находится вне допустимого диапазона'
            )
        return value

    def validate(self, data):
        if (self.context['request'].method == 'POST'
            and Review.objects.filter(
                author=self.context['request'].user,
                title=self.context['view'].kwargs['title_id']).exists()):
            raise serializers.ValidationError(
                'Дублирование отзыва.'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = '__all__'
        model = Comment
        read_only_fields = ('id', 'review', 'author', 'pub_date',)

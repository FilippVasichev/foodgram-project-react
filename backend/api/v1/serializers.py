import base64
from pprint import pprint
from sqlite3 import IntegrityError

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.response import Response
from foodgram.models import FavoriteRecipe, ShoppingCart
from recipe.models import Ingredient, Tag, Recipe, IngredientQuantity, RecipeTag
from users.models import User, Follow


class CustomUserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(
        max_length=254,
        required=True
    )
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=150,
        required=True
    )
    first_name = serializers.CharField(
        max_length=150,
        required=True,
    )
    last_name = serializers.CharField(
        max_length=150,
        required=True,
    )
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Этот email уже занят.')
        return email

    def validate_username(self, username):
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError('Этот username уже занят.')
        return username


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )
        read_only_fields = ('is_subscribed',)

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Follow.objects.filter(
                user=user,
                author=author).exists()
        return False


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = IngredientQuantity
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = CustomUserSerializer()
    ingredients = IngredientAmountSerializer(
        many=True,
        source='recipe_ingredient'
    )
    tags = TagSerializer(many=True)
    image = serializers.SerializerMethodField()
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()
    class Meta:
        model = Recipe
        read_only_fields = (
            'is_favorited',
            'is_in_shopping_cart',
            'author',
            'tags',
            'image',
        )
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_image(self, recipe):
        if recipe.image:
            request = self.context.get('request')
            return request.build_absolute_uri(recipe.image.url)
        return None

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        if user.is_authenticated:
            return FavoriteRecipe.objects.filter(
                user=user,
                recipe = recipe).exists()
        return False

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=user,
                recipe=recipe).exists()
        return False


class CreateRecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    class Meta:
        model = IngredientQuantity
        fields = (
            'id',
            'amount',
        )


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            _format, imgstr = data.split(';base64,')
            ext = _format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'temp.{ext}')
        return super().to_internal_value(data)


class CreateUpdateRecipeSerializer(serializers.ModelSerializer):
    ingredients = CreateRecipeIngredientsSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance, context=self.context)
        return serializer.data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])
        recipe_author = self.context.get('request').user
        recipe = Recipe.objects.create(author=recipe_author, **validated_data)
        for ingredient_data in ingredients:
            ingredient_id = ingredient_data.pop('ingredient')
            amount = ingredient_data.pop('amount')
            IngredientQuantity.objects.create(
                recipe=recipe,
                ingredient=ingredient_id,
                amount=amount,
            )
        for tags_data in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tags_data)
        return recipe

    def update(self, recipe, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags', [])
        if tags_data:
            recipe.tags.set(tags_data)
        if ingredients_data:
            recipe.ingredients.clear()
            ingredient_quantities = [
                IngredientQuantity(
                    recipe=recipe,
                    ingredient=ingredient_data.get('ingredient'),
                    amount=ingredient_data.get('amount')
                )
                for ingredient_data in ingredients_data
            ]
            IngredientQuantity.objects.bulk_create(ingredient_quantities)
        return super().update(recipe, validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.SerializerMethodField(required=False)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')
    class Meta:
        model = FavoriteRecipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )

    def get_image(self, obj):
        recipe = Recipe.objects.get(pk=self.context.get('kwargs'))
        image_name = recipe.image.name if recipe.image else None
        if image_name:
            return self.context['request'].build_absolute_uri(image_name)
        return None

    def create(self, validated_data):
        recipe_id = self.context.get('kwargs')
        user = self.context.get('request').user
        favorite, created = FavoriteRecipe.objects.get_or_create(
            recipe_id=recipe_id,
            user=user
        )
        if not created:
            raise serializers.ValidationError({'errors': 'Рецепт уже добавлен в избранное'})
        return favorite


class SubscriptionAuthorRecipesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        read_only_fields = ['id', 'name', 'image', 'cooking_time']
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class UserSubscriptionSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    class Meta:
        model = Follow
        read_only_fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        ]
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes_count(self, follow):
        return follow.author.recipe.count()

    def get_recipes(self, follow):
        return SubscriptionAuthorRecipesSerializer(
            follow.author.recipe.all(),
            many=True
        ).data

    def get_is_subscribed(self, follow):
        return follow.user == self.context.get('request').user


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.SerializerMethodField(required=False)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')
    class Meta:
        model = ShoppingCart
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )

    def get_image(self, obj):
        recipe = Recipe.objects.get(pk=self.context.get('kwargs'))
        image_name = recipe.image.name if recipe.image else None
        if image_name:
            return self.context['request'].build_absolute_uri(image_name)
        return None

    def create(self, validated_data):
        user = self.context.get('request').user
        recipe_id = self.context.get('kwargs')
        cart, created = ShoppingCart.objects.get_or_create(
            user=user,
            recipe_id=recipe_id,
        )
        if not created:
            raise serializers.ValidationError(
                {'errors': 'Рецепт уже добавлен в корзину'})
        return cart

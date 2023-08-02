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


# from foodgram.models import FavoriteRecipe


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

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Этот email уже занят.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Этот username уже занят.")
        return value


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

    def get_is_subscribed(self, author):
        return Follow.objects.filter(
            user=self.context.get('request').user,
            author=author).exists()


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
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientQuantity
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(
        many=True,
        source='recipe_ingredient'
    )
    tags = TagSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField(read_only=True)
    name = serializers.ReadOnlyField(read_only=True)
    cooking_time = serializers.ReadOnlyField(read_only=True)
    class Meta:
        model = Recipe
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
        image_name = recipe.image.name if recipe.image else None
        if image_name:
            return self.context['request'].build_absolute_uri(image_name)
        return None

    def get_is_favorited(self, recipe):
        return FavoriteRecipe.objects.filter(
            user=self.context.get('request').user,
            recipe = recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        return ShoppingCart.objects.filter(
            user=self.context.get('request').user,
            recipe=recipe).exists()


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
        recipe.name = validated_data.get('name', recipe.name)
        recipe.text = validated_data.get('text', recipe.text)
        recipe.cooking_time = validated_data.get('cooking_time', recipe.cooking_time)
        recipe.image = validated_data.get('image', recipe.image)
        ingredients_data = validated_data.get('ingredients')
        tags_data = validated_data.get('tags')

        if tags_data:
            recipe_tags = list(recipe.tags.all())
            for tag in tags_data:
                recipe_tag, _ = RecipeTag.objects.update_or_create(
                    defaults={'tag': tag},
                    recipe=recipe,
                    tag=tag
                )
                recipe_tag.save()
                [RecipeTag.objects.filter(
                    recipe=recipe,
                    tag=recipe_tag).delete()
                 for recipe_tag in recipe_tags
                 if recipe_tag not in tags_data]

        if ingredients_data:
            recipe_ingredients = list(recipe.ingredients.all())
            for ingredient_data in ingredients_data:
                ingredient_amount = ingredient_data.get('amount')
                ingredient_name = ingredient_data.get('ingredient')
                ingredient_quantity, _ = IngredientQuantity.objects.update_or_create(
                    defaults={
                        'ingredient': ingredient_name,
                        'amount': ingredient_amount,
                    },
                    recipe=recipe,
                    ingredient=ingredient_name,
                )
                ingredient_quantity.save()
                [IngredientQuantity.objects.filter(
                        recipe=recipe,
                        ingredient=ingredient).delete()
                 for ingredient in recipe_ingredients
                 if ingredient != ingredient_name]

        return recipe

class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id', read_only=True)
    name = serializers.ReadOnlyField(source='recipe.name', read_only=True)
    image = serializers.SerializerMethodField(read_only=True, required=False)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time', read_only=True)
    class Meta:
        model = FavoriteRecipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )

    def get_image(self, recipe):
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

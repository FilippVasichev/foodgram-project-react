from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from foodgram import constants
from recipe.models import (FavoriteRecipe, Ingredient, IngredientQuantity,
                           Recipe, ShoppingCart, Tag)
from users.models import Follow


class CustomUserSerializer(UserSerializer):
    """
    Сериализатор для чтения пользователей.
    """
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
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and author.following.filter(user=request.user).exists())


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор только для чтения ингридиетов.
    """

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор только для чтения тэгов.
    """

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientAmountSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения Количества и единиц измерения
    ингридиентов в рецепте.
    """
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
    """
    Сериализатор для чтения рецептов.
    Предоставляет полную информацию о рецепте:
    - Тэги рецепта.
    - Автора рецепта.
    - Список ингредиентов и их количество.
    - Поле, указывающее, добавлен ли рецепт в избранное у юзера.
    - Поле, указывающее, есть ли рецепт в списке покупок у юзера.
    - Название рецепта.
    - Картинку рецепта.
    - Описание рецепта.
    - Время приготовления рецепта.
    """
    author = CustomUserSerializer()
    ingredients = IngredientAmountSerializer(
        many=True,
        source='recipe_ingredient'
    )
    tags = TagSerializer(many=True)
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)

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


class CreateRecipeIngredientsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания связи Рецепта и Количества ингредиента.

    - id: Поле связи с ингредиентом по его ID.
    - amount: Количество ингредиента в рецепте.
    """
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        min_value=constants.MIN_INGREDIENT_AMOUNT,
        max_value=constants.MAX_INGREDIENT_AMOUNT,
    )

    class Meta:
        model = IngredientQuantity
        fields = (
            'id',
            'amount',
        )


class CreateUpdateRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления Рецепта.
    """
    ingredients = CreateRecipeIngredientsSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    image = Base64ImageField(required=True)
    cooking_time = serializers.IntegerField(
        min_value=constants.MIN_COOKING_TIME,
        max_value=constants.MAX_COOKING_TIME,
    )

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
        """
        Преобразует объект рецепта в данные для сериализации.
        """
        return RecipeSerializer(instance, context=self.context).data

    @staticmethod
    def recipe_ingredients_tags_save(recipe, ingredients=None, tags=None):
        recipe.tags.set(tags)
        ingredient_quantities = [
            IngredientQuantity(
                recipe=recipe,
                ingredient=ingredient.get('ingredient'),
                amount=ingredient.get('amount')
            )
            for ingredient in sorted(
                ingredients,
                key=lambda x: x['ingredient'].name,
            )
        ]
        IngredientQuantity.objects.bulk_create(ingredient_quantities)

    def create(self, validated_data):
        """
        Метод для создания нового рецепта.
        """
        ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])
        recipe_author = self.context.get('request').user
        recipe = Recipe.objects.create(author=recipe_author, **validated_data)
        self.recipe_ingredients_tags_save(recipe, ingredients, tags)
        return recipe

    def update(self, recipe, validated_data):
        """
        Метод обновляет существующий рецепт.
        """
        ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])
        recipe.ingredients.clear()
        self.recipe_ingredients_tags_save(recipe, ingredients, tags)
        return super().update(recipe, validated_data)

    def validate(self, recipe):
        ingredients = recipe['ingredients']
        tags = recipe['tags']
        if not tags:
            raise serializers.ValidationError('Тэги не указаны!')
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError('Тэги должны быть уникальны!')
        if not ingredients:
            raise serializers.ValidationError('Ингридиенты не указаны!')
        if len(ingredients) != len(
                {ingredient['ingredient'] for ingredient in ingredients}
        ):
            raise serializers.ValidationError(
                'Ингридиенты должны быть уникальны!'
            )
        return recipe


class SubscriptionAuthorRecipesSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения Подписки на Автора рецепта
    """

    class Meta:
        model = Recipe
        read_only_fields = ['id', 'name', 'image', 'cooking_time']
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения и добавления рецепта в избранное.
    """

    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe',)

    def validate(self, attrs):
        if FavoriteRecipe.objects.filter(**attrs).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже в избранном.')
        return attrs

    def to_representation(self, instance):
        return SubscriptionAuthorRecipesSerializer(
            instance.recipe,
            context=self.context
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения и создания Корзины покупок юзера.
    """

    class Meta:
        model = ShoppingCart
        fields = ('recipe', 'user')

    def validate(self, attrs):
        if ShoppingCart.objects.filter(**attrs).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже в корзине.')
        return attrs

    def to_representation(self, instance):
        return SubscriptionAuthorRecipesSerializer(
            instance.recipe,
            context=self.context
        ).data


class UserSubscriptionSerializer(CustomUserSerializer):
    """
    Сериализатор для чтения подписок Юзера.
    """
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipe.count')

    class Meta(CustomUserSerializer.Meta):
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

    def get_recipes(self, user):
        """
        Метод отдает все рецепты Автора
        на которого подписан юзер.

        Recipes_limit: ограничение кол-ва
        рецептов автора в выдаче.
        """
        request = self.context.get('request')
        try:
            recipes_limit = int(request.GET.get('recipes_limit', 0))
        except (ValueError, TypeError) as error:
            raise error
        queryset = user.recipe.all()
        return SubscriptionAuthorRecipesSerializer(
            queryset[:recipes_limit] if recipes_limit else queryset,
            many=True,
        ).data


class CreateUserSubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ('user', 'author')

    def validate(self, attrs):
        if Follow.objects.filter(**attrs).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого автора.')
        if attrs['user'] == attrs['author']:
            raise serializers.ValidationError(
                'Нельзя подписаться на себя.')
        return attrs

    def to_representation(self, instance):
        return UserSubscriptionSerializer(
            instance.author,
            context=self.context,
        ).data

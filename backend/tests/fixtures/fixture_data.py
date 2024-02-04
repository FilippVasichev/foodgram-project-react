from recipe.models import Ingredient, Tag

import pytest


@pytest.fixture
def tag_1():
    return Tag.objects.create(
        name='Tag1',
        slug='testTag1',
        color='#E26C2D'
    )


@pytest.fixture
def tag_2():
    return Tag.objects.create(
        name='Tag2',
        slug='testTag2',
        color='#FF5733'
    )


@pytest.fixture
def ingredient_1():
    return Ingredient.objects.create(
        name='Ingredient1',
        measurement_unit='unit1',
    )


@pytest.fixture
def ingredient_2():
    return Ingredient.objects.create(
        name='Ingredient2',
        measurement_unit='unit2',
    )

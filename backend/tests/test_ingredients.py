import pytest
from django.urls import reverse
from http import HTTPStatus
from recipe.models import Ingredient
from tests.check_response_fields import check_fields


@pytest.mark.django_db(transaction=True)
class TestIngredientsAPI:
    ingredients_urls = reverse('ingredients-list')

    def test_ingredients_urls(self, client):
        """
        Проверка существования эндпоинта tags/
        и доступа к нему не авторизованного пользователя.
        """
        try:
            response = client.get(self.ingredients_urls)
        except Exception as e:
            assert False, (
                f'Страница "{self.tags_urls}"  не работает. Ошибка: "{e}"'
            )
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Страница `{self.tags_urls}` не найдена,'
            f' проверьте этот адрес в *urls.py*'
        )
        assert response.status_code == HTTPStatus.OK, (
            f'Ошибка {response.status_code} при открытиии '
            f'`{self.tags_urls}`. Проверьте ее view-функцию'
        )

    def test_ingredients_objects_response(self, client, ingredient_1):
        """
        Проверка работоспособности эндпоинта tags/.
        """
        response_json = client.get(self.ingredients_urls).json()
        assert isinstance(response_json, list), (
            f'Убедитесь что в ответ на GET-запрос'
            f' к "{self.ingredients_urls}" ингредиенты представлены списком'
        )
        assert len(response_json) == Ingredient.objects.count(), (
            f'Убедитесь что в ответ на GET-запрос к "{self.ingredients_urls}"'
            f'приходит список со всеми ингредиентами.'
        )
        ingredient_fields = {
            'id': ingredient_1.id,
            'name': ingredient_1.name,
            'measurement_unit': ingredient_1.measurement_unit,
        }
        check_fields(ingredient_fields, response_json[0], self.ingredients_urls)

    def test_access_not_authenticated_ingredients_detail(
            self,
            client,
            ingredient_1,
    ):
        """
        Проверка существования эндпоинта tags/{id}
        и доступа не авторизованного пользователя к нему.
        """
        ingredient_detail_url = reverse(
            'ingredients-detail',
            kwargs={'pk': ingredient_1.id}
        )
        response = client.get(ingredient_detail_url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Страница `{ingredient_detail_url}` не найдена,'
            f' проверьте этот адрес в *urls.py*'
        )
        assert response.status_code == HTTPStatus.OK, (
            f'Ошибка {response.status_code} при открытии '
            f'`{ingredient_detail_url}`. Проверьте ее view-функцию'
        )

    def test_ingredients_detail(self, client, ingredient_1):
        response_json = client.get(
            reverse('ingredients-detail', kwargs={'pk': ingredient_1.id})
        ).json()
        ingredient_fields = {
            'id': ingredient_1.id,
            'name': ingredient_1.name,
            'measurement_unit': ingredient_1.measurement_unit,
        }
        check_fields(
            ingredient_fields,
            response_json,
            reverse('ingredients-detail', kwargs={'pk': ingredient_1.id})
        )
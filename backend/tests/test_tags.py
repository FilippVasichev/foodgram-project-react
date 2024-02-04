from http import HTTPStatus

import pytest
from django.urls import reverse

from recipe.models import Tag
from tests.check_response_fields import check_fields


@pytest.mark.django_db(transaction=True)
class TestTagsAPI:
    tags_urls = reverse('tags-list')

    def test_tags_urls(self, client):
        """
        Проверка существования эндпоинта tags/
        и доступа к нему не авторизованного пользователя.
        """
        try:
            response = client.get(self.tags_urls)
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

    def test_tags_objects_response(self, client, tag_1):
        """
        Проверка работоспособности эндпоинта tags/.
        """
        response_json = client.get(self.tags_urls).json()
        assert isinstance(response_json, list), (
            f'Убедитесь что в ответ на GET-запрос'
            f' к "{self.tags_urls}" тэги представлены списком'
        )
        assert len(response_json) == Tag.objects.count(), (
            f'Убедитесь что в ответ на GET-запрос к "{self.tags_urls}"'
            f'приходит список со всеми тэгами.'
        )

        tag_fields = {
            'id': tag_1.id,
            'name': tag_1.name,
            'slug': tag_1.slug,
            'color': tag_1.color,
        }

        check_fields(tag_fields, response_json[0], self.tags_urls)

    def test_acces_not_authenticated_tags_detail(self, client, tag_1):
        """
        Проверка существования эндпоинта tags/{id}
        и доступа не авторизованного пользователя к нему.
        """
        tag_detail_url = reverse('tags-detail', kwargs={'pk': tag_1.id})
        response = client.get(tag_detail_url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Страница `{tag_detail_url}` не найдена,'
            f' проверьте этот адрес в *urls.py*'
        )
        assert response.status_code == HTTPStatus.OK, (
            f'Ошибка {response.status_code} при открытиии '
            f'`{tag_detail_url}`. Проверьте ее view-функцию'
        )

    def test_tags_detail(self, client, tag_1):
        response_json = client.get(
            reverse('tags-detail', kwargs={'pk': tag_1.id},)
        ).json()
        tag_fields = {
            'id': tag_1.id,
            'name': tag_1.name,
            'slug': tag_1.slug,
            'color': tag_1.color,
        }
        check_fields(
            tag_fields,
            response_json,
            reverse('tags-detail', kwargs={'pk': tag_1.id})
        )

from http import HTTPStatus


def check_only_save_methods_allowed(user_client, url):
    responses = [
        user_client.post(url),
        user_client.patch(url),
        user_client.put(url),
        user_client.delete(url),
    ]
    for response in responses:
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            f'Убедитесь, что в ответ на небезопасные методы '
            f'к {url} возвращаеться статус 405.'
        )

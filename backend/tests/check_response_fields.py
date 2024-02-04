def check_fields(fields, response, url):
    """
    Проверяет корректность полей в ответах.
    """
    for field in fields:
        assert field in response, (
            f'Убедитесь что в ответе на запрос к "{url}"'
            f' содержится поле {field}'
        )
        assert response[field] == fields[field], (
            f'Убедитесь, что в ответ на запрос к "{url}"'
            f' верно отображается поле "{field}"'
        )

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPaginator(PageNumberPagination):
    """
    Кастомный пагинатор с встроенными параметрами
    limit и recipes_limit
    """
    page_size_query_param = 'limit'
    page_size = 6

    def get_paginated_response(self, data):
        """
        Ограничивает список рецептов в выдаче
        при наличии параметра recipes_limit в url.
        """
        recipes_limit = self.request.GET.get('recipes_limit')
        if recipes_limit:
            data = data[:int(recipes_limit)]
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

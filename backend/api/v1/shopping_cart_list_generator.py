from io import BytesIO

from django.http import FileResponse


def generate_shopping_cart_file(queryset):
    cart_list = BytesIO()
    for ingredient in queryset:
        line = (
            f'{ingredient["ingredient__name"]}: '
            f'{ingredient["amount"]}'
            f'{ingredient["ingredient__measurement_unit"]}\n'
        )
        cart_list.write(line.encode('utf-8'))
    cart_list.seek(0)
    return FileResponse(
        cart_list, content_type='text/plain', filename='your_shopping_list.txt'
    )

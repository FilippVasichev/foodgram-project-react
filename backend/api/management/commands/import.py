import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipe.models import Ingredient, Tag

csv_path = os.path.join(settings.BASE_DIR, 'data', 'ingredients.csv')

tags = {
    'Завтрак': ('#00FF00', 'breakfast'),
    'Обед': ('#FF0000', 'lunch'),
    'Ужин': ('#800080', 'dinner')
}


class Command(BaseCommand):
    """
    Импортирует данные моделей из .csv файлов.
    """
    def handle(self, *args, **options):
        for name, (color, slug) in tags.items():
            Tag.objects.get_or_create(
                name=name,
                color=color,
                slug=slug,
            )
        self.stdout.write(
            self.style.SUCCESS('Записи тэгов созданы.')
        )
        try:
            with open(csv_path, encoding='utf-8', newline='') as f:
                reader = csv.reader(f)
                for name, unit in reader:
                    Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=unit,
                    )
                self.stdout.write(
                    self.style.SUCCESS('Записи ингридиентов созданы.')
                )
        except FileNotFoundError:
            return 'Файл не найден.'
        except csv.Error as err:
            return f'Ошибка чтения CSV: {err}'

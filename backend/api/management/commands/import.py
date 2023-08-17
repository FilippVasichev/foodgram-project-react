import csv

from recipe.models import Ingredient, Tag
from users.models import User

from django.conf import settings
from django.core.management.base import BaseCommand

CSV_FILES = {
    'ingredients': Ingredient,
    'users': User,
    'tags': Tag,
}

CONTENT_DIR = settings.BASE_DIR / 'static/data'


class Command(BaseCommand):
    """
    Импортирует данные для конкретных моделей из .csv файлов.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete-existing',
            action='store_true',
            dest='delete_existing',
            default=False,
            help='Удаляет существующие данные конкретной Модели',
        )

    def handle(self, *args, **options):
        try:
            for file, model in CSV_FILES.items():
                with open(
                        CONTENT_DIR / f'{file}.csv',
                        encoding='utf-8',
                        newline=''
                ) as f:
                    reader = csv.DictReader(f)
                    if options["delete_existing"]:
                        model.objects.all().delete()
                    self.stdout.write(self.style.SUCCESS(
                        f'Удалены старые записи {file.capitalize()}.'))
                    for row in reader:
                        model.objects.create(**row)
                        self.stdout.write(self.style.SUCCESS(
                            f'Записи {file.capitalize()} созданы.'))
                self.stdout.write(self.style.SUCCESS(
                    'Поздравляем! Ваша БД наполнена!. '))
        except Exception as err:
            print('Произошла ошибка:', err)

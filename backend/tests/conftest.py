import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

MANAGE_PATH = os.path.join(BASE_DIR)
project_dir_content = os.listdir(MANAGE_PATH)
FILENAME = 'manage.py'

if FILENAME not in project_dir_content:
    assert False, (
        f'В директории `{MANAGE_PATH}` не найден файл `{FILENAME}`. '
        'Убедитесь, что у вас верная структура проекта.'
    )

pytest_plugins = [
    'tests.fixtures.fixture_data',
    'tests.fixtures.fixture_user',
]

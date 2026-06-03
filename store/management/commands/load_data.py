"""
Command для загрузки данных из фикстуры.
Используется при деплое на Render для восстановления данных БД.
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
import os


class Command(BaseCommand):
    help = 'Загрузка данных из фикстуры (JSON)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fixture',
            type=str,
            default='initial_data.json',
            help='Имя файла фикстуры (по умолчанию: initial_data.json)'
        )

    def handle(self, *args, **options):
        fixture = options['fixture']
        fixture_path = os.path.join('fixtures', fixture)
        
        if os.path.exists(fixture_path):
            self.stdout.write(f'Загрузка данных из {fixture_path}...')
            call_command('loaddata', fixture_path)
            self.stdout.write(self.style.SUCCESS('✅ Данные загружены успешно!'))
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Фикстура {fixture_path} не найдена. Пропускаем.')
            )

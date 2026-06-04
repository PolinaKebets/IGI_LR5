"""
Команда для добавления графика работы пунктов выдачи.
Запускается на Render после деплоя для добавления календаря.

Использование:
    python manage.py add_working_hours
"""
from django.core.management.base import BaseCommand
from store.models import PickupPoint


class Command(BaseCommand):
    help = 'Добавляет график работы для пунктов выдачи'

    def handle(self, *args, **options):
        # График работы для каждого пункта
        working_hours_data = {
            1: 'Пн-Пт: 09:00-20:00, Сб: 10:00-18:00, Вс: выходной',
            2: 'Пн-Пт: 08:00-21:00, Сб-Вс: 09:00-20:00',
            3: 'Пн-Вс: 10:00-22:00 (без выходных)',
            4: 'Пн-Пт: 09:00-19:00, Сб: 10:00-16:00, Вс: выходной',
        }

        updated = 0
        for pk, hours in working_hours_data.items():
            try:
                point = PickupPoint.objects.get(pk=pk)
                point.working_hours = hours
                point.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {point.city}: {hours}')
                )
                updated += 1
            except PickupPoint.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Пункт #{pk} не найден')
                )

        if updated == 0:
            self.stdout.write(
                self.style.WARNING('⚠️  Пункты выдачи не найдены. Запустите seed_data.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Обновлено {updated} пунктов выдачи')
            )

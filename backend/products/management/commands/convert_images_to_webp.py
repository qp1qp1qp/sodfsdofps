from django.core.management.base import BaseCommand
from products.models import Product, ProductImage, HeroImage, GalleryImage
from products.signals import convert_to_webp, MAX_WIDTH, MAX_PRODUCT
import logging

logger = logging.getLogger('products')


class Command(BaseCommand):
    help = 'Конвертирует все существующие изображения в WebP формат'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать что будет конвертировано, без реальной конвертации',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        total = 0
        converted = 0
        skipped = 0
        errors = 0

        tasks = [
            ('Product.imageUrl',   Product.objects.exclude(imageUrl=''),          'imageUrl',  MAX_PRODUCT),
            ('ProductImage.image', ProductImage.objects.exclude(image=''),         'image',     MAX_PRODUCT),
            ('HeroImage.image',    HeroImage.objects.all(),                        'image',     MAX_WIDTH),
            ('GalleryImage.image', GalleryImage.objects.all(),                     'image',     MAX_WIDTH),
        ]

        for label, queryset, field_name, max_w in tasks:
            count = queryset.count()
            self.stdout.write(f'\n{label}: {count} объектов')

            for obj in queryset:
                img_field = getattr(obj, field_name)
                if not img_field or not img_field.name:
                    skipped += 1
                    continue

                if img_field.name.lower().endswith('.webp'):
                    self.stdout.write(f'  ⏭  Пропуск (уже WebP): {img_field.name}')
                    skipped += 1
                    continue

                total += 1
                self.stdout.write(f'  → {img_field.name}')

                if dry_run:
                    self.stdout.write('    [dry-run] Будет конвертировано')
                    continue

                try:
                    ok = convert_to_webp(img_field, max_width=max_w)
                    if ok:
                        # Сохраняем новое имя в БД
                        type(obj).objects.filter(pk=obj.pk).update(**{field_name: img_field.name})
                        self.stdout.write(self.style.SUCCESS(f'    ✓ → {img_field.name}'))
                        converted += 1
                    else:
                        skipped += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'    ✗ Ошибка: {e}'))
                    errors += 1

        self.stdout.write('\n' + '─' * 40)
        self.stdout.write(self.style.SUCCESS(
            f'Итого: конвертировано {converted}, пропущено {skipped}, ошибок {errors} (из {total} файлов)'
        ))
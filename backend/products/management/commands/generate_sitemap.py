from django.core.management.base import BaseCommand
from products.models import Product, ProductType
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Генерирует sitemap.xml'

    def handle(self, *args, **options):
        base_url = 'https://wooddon.ru'
        
        static_urls = [
            ('/', '1.0', 'weekly'),
            ('/all-products', '0.9', 'daily'),
            ('/delivery', '0.7', 'monthly'),
            ('/about', '0.6', 'monthly'),
            ('/contacts', '0.6', 'monthly'),
            ('/faq', '0.5', 'monthly'),
        ]

        urls = []
        
        # Статические страницы
        for path, priority, changefreq in static_urls:
            urls.append(f"""  <url>
    <loc>{base_url}{path}</loc>
    <priority>{priority}</priority>
    <changefreq>{changefreq}</changefreq>
  </url>""")

        # Все товары
        products = Product.objects.select_related('product_type').filter(
            is_available=True,
            custom_url__isnull=False
        ).exclude(custom_url='')
        
        for product in products:
            if product.product_type and product.custom_url:
                path = f'/all-products/{product.product_type.slug}/{product.custom_url}'
                urls.append(f"""  <url>
    <loc>{base_url}{path}</loc>
    <priority>0.8</priority>
    <changefreq>weekly</changefreq>
  </url>""")

        # Категории товаров
        for ptype in ProductType.objects.all():
            urls.append(f"""  <url>
    <loc>{base_url}/all-products/{ptype.slug}</loc>
    <priority>0.85</priority>
    <changefreq>daily</changefreq>
  </url>""")

        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        xml += '\n'.join(urls)
        xml += '\n</urlset>'

        # Сохраняем в папку фронтенда (dist) и static
        output_path = os.path.join(settings.BASE_DIR, '..', 'dist', 'sitemap.xml')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml)

        self.stdout.write(self.style.SUCCESS(
            f'Готово: {len(urls)} URL записано в sitemap.xml'
        ))
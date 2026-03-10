# Generated manually

from django.db import migrations, models
import products.models

class Migration(migrations.Migration):

    dependencies = [
        ('products', 'add_unit_dimensions'),  # Ссылка на предыдущую миграцию
    ]

    operations = [
        # Добавляем значение по умолчанию для поля imageUrl
        migrations.AlterField(
            model_name='product',
            name='imageUrl',
            field=models.ImageField(default=products.models.get_default_product_image, upload_to=products.models.product_image_path),
        ),
        
        # Обновление существующих записей для установки изображения по умолчанию
        migrations.RunSQL(
            """
            UPDATE products_product 
            SET "imageUrl" = 'product_images/1569685356.jpg' 
            WHERE "imageUrl" IS NULL OR "imageUrl" = '';
            """,
            reverse_sql="""
            -- No reverse operation needed
            """
        ),
    ] 
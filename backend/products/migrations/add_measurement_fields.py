# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', 'add_default_image'),  # Необходимо заменить на последнюю миграцию
    ]

    operations = [
        # Добавляем новые поля для хранения объемов/площадей/длин
        migrations.AddField(
            model_name='product',
            name='volume_per_unit',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True, verbose_name='Объем в 1 шт. (м³)'),
        ),
        migrations.AddField(
            model_name='product',
            name='area_per_unit',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True, verbose_name='Площадь в 1 шт. (м²)'),
        ),
        migrations.AddField(
            model_name='product',
            name='linear_meters_per_unit',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Длина в 1 шт. (п.м)'),
        ),
        
        # Обновляем verbose_name для существующих полей
        migrations.AlterField(
            model_name='product',
            name='primary_unit',
            field=models.CharField(choices=[('piece', 'Штука'), ('cubic', 'Кубический метр'), ('square', 'Квадратный метр'), ('linear', 'Погонный метр')], default='piece', max_length=10, verbose_name='Единица измерения'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена за единицу измерения'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price_per_unit',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена за штуку'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price_per_cubic_meter',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Цена за м³'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price_per_square_meter',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Цена за м²'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price_per_linear_meter',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Цена за погонный метр'),
        ),
        migrations.AlterField(
            model_name='product',
            name='length',
            field=models.DecimalField(blank=True, decimal_places=3, help_text='Длина в метрах', max_digits=8, null=True, verbose_name='Длина (м)'),
        ),
        migrations.AlterField(
            model_name='product',
            name='width',
            field=models.DecimalField(blank=True, decimal_places=3, help_text='Ширина в метрах', max_digits=8, null=True, verbose_name='Ширина (м)'),
        ),
        migrations.AlterField(
            model_name='product',
            name='thickness',
            field=models.DecimalField(blank=True, decimal_places=3, help_text='Толщина в метрах', max_digits=8, null=True, verbose_name='Толщина (м)'),
        ),
    ] 
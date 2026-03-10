# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),  # Замените на последнюю миграцию в вашем проекте
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='primary_unit',
            field=models.CharField(choices=[('piece', 'Штука'), ('cubic', 'Кубический метр'), ('square', 'Квадратный метр'), ('linear', 'Погонный метр')], default='piece', max_length=10),
        ),
        migrations.AddField(
            model_name='product',
            name='length',
            field=models.DecimalField(blank=True, decimal_places=3, help_text='Длина в метрах', max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='width',
            field=models.DecimalField(blank=True, decimal_places=3, help_text='Ширина в метрах', max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='thickness',
            field=models.DecimalField(blank=True, decimal_places=3, help_text='Толщина в метрах', max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='price_per_square_meter',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ] 
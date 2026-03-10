from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0018_errorlog_useractivitylog'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuizLead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('name', models.CharField(max_length=150, verbose_name='Имя')),
                ('phone', models.CharField(max_length=30, verbose_name='Телефон')),
                ('structure', models.CharField(blank=True, max_length=100, verbose_name='Тип строения')),
                ('material', models.CharField(blank=True, max_length=100, verbose_name='Материал')),
                ('volume', models.CharField(blank=True, max_length=100, verbose_name='Объём')),
                ('timing', models.CharField(blank=True, max_length=100, verbose_name='Сроки')),
                ('recommended', models.CharField(blank=True, max_length=255, verbose_name='Рекомендации')),
                ('is_processed', models.BooleanField(default=False, verbose_name='Обработан')),
                ('manager_note', models.TextField(blank=True, verbose_name='Заметка менеджера')),
            ],
            options={
                'verbose_name': 'Заявка с квиза',
                'verbose_name_plural': 'Заявки с квиза',
                'ordering': ['-created_at'],
            },
        ),
    ]
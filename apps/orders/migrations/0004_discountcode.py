from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0003_alter_order_status_alter_orderitem_size'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiscountCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True, verbose_name='Mã giảm giá')),
                ('name', models.CharField(blank=True, max_length=120, null=True, verbose_name='Tên chương trình')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Mô tả')),
                ('discount_percent', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Phần trăm giảm')),
                ('min_order_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Giá trị đơn tối thiểu')),
                ('max_discount_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Giảm tối đa')),
                ('valid_from', models.DateTimeField(blank=True, null=True, verbose_name='Hiệu lực từ')),
                ('valid_to', models.DateTimeField(blank=True, null=True, verbose_name='Hiệu lực đến')),
                ('is_active', models.BooleanField(default=True, verbose_name='Đang hoạt động')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')),
            ],
            options={
                'verbose_name': 'Mã giảm giá',
                'verbose_name_plural': 'Mã giảm giá',
                'db_table': 'discount_codes',
                'ordering': ['-created_at'],
            },
        ),
    ]

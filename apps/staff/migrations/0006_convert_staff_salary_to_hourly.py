from decimal import Decimal, ROUND_HALF_UP

from django.db import migrations, models


def monthly_to_hourly(apps, schema_editor):
    Staff = apps.get_model('staff', 'Staff')
    divisor = Decimal('208')

    for staff in Staff.objects.exclude(salary__isnull=True):
        monthly_salary = Decimal(str(staff.salary))
        if monthly_salary <= 0:
            continue
        hourly_salary = (monthly_salary / divisor).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        staff.salary = hourly_salary
        staff.save(update_fields=['salary'])


def hourly_to_monthly(apps, schema_editor):
    Staff = apps.get_model('staff', 'Staff')
    multiplier = Decimal('208')

    for staff in Staff.objects.exclude(salary__isnull=True):
        hourly_salary = Decimal(str(staff.salary))
        if hourly_salary <= 0:
            continue
        monthly_salary = (hourly_salary * multiplier).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        staff.salary = monthly_salary
        staff.save(update_fields=['salary'])


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0005_shiftrule_and_indexes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='salary',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=10,
                null=True,
                verbose_name='Lương/giờ',
            ),
        ),
        migrations.RunPython(monthly_to_hourly, reverse_code=hourly_to_monthly),
    ]

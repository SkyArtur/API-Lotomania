from django.db import migrations


def seed_numbers(apps, schema_editor) -> None:
    Number = apps.get_model('core', 'Number')
    numbers = [n for n in range(0, 100)]
    registered_numbers = Number.objects.values_list('value', flat=True)
    new_numbers = [Number(value=n) for n in set(numbers).difference(registered_numbers)]
    Number.objects.bulk_create(new_numbers)
    return None


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_numbers, migrations.RunPython.noop),
    ]

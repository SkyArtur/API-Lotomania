from django.db import migrations


def seed_numeros(apps, schema_editor) -> None:
    Numero = apps.get_model('core', 'Numero')
    numeros = [n for n in range(0, 100)]
    numeros_registrados = Numero.objects.values_list('valor', flat=True)
    novos_numeros = [Numero(valor=n) for n in set(numeros).difference(numeros_registrados)]
    Numero.objects.bulk_create(novos_numeros)
    return None


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_numeros, migrations.RunPython.noop),
    ]
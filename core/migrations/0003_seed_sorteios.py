from django.db import migrations, transaction

from core.data import dados_sorteios_lotomania


def seed_sorteios(apps, schema_editor) -> None:

    sorteios_do_arquivo = dados_sorteios_lotomania()

    with transaction.atomic():

        if sorteios_do_arquivo:

            Numero = apps.get_model('core', 'Numero')
            Sorteio = apps.get_model('core', 'Sorteio')
            SorteioNumero = apps.get_model('core', 'SorteioNumero')
            SorteioPremio = apps.get_model('core', 'SorteioPremio')

            referencias_registradas = Sorteio.objects.values_list('referencia', flat=True)
            novos_sorteios = [
                sorteio
                for sorteio in sorteios_do_arquivo
                if sorteio['sorteio']['referencia'] not in referencias_registradas
            ]

            Sorteio.objects.bulk_create(
                [
                    Sorteio(**sorteio['sorteio'])
                    for sorteio in novos_sorteios
                ],
                ignore_conflicts=True
            )
            novas_referencias = [
                sorteio['sorteio']['referencia']
                for sorteio in novos_sorteios
            ]
            map_sorteios = {
                sorteio.referencia: sorteio
                for sorteio in Sorteio.objects.filter(referencia__in=novas_referencias)
            }
            map_numeros = {
                numero.valor: numero
                for numero in Numero.objects.all()
            }

            sorteio_numero, sorteio_premio = [], []

            for item in novos_sorteios:
                payload = map_sorteios[item['sorteio']['referencia']]
                if payload:
                    for numero in item['numeros']:
                        sorteio_numero.append(SorteioNumero(sorteio=payload, numero=map_numeros[numero]))
                    for premio in item['premios']:
                        if premio['ganhadores'] > 0:
                            sorteio_premio.append(SorteioPremio(sorteio=payload, **premio))

            SorteioNumero.objects.bulk_create(sorteio_numero, ignore_conflicts=True)
            SorteioPremio.objects.bulk_create(sorteio_premio, ignore_conflicts=True)

    return None

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0002_seed_numeros'),
    ]

    operations = [
        migrations.RunPython(seed_sorteios, migrations.RunPython.noop),
    ]

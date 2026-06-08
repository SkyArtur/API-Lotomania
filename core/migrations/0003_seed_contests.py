from django.db import migrations

from core.utils import extract_contests


def seed_contests(apps, schema_editor) -> None:
    CONTEST_DATA = extract_contests()
    if CONTEST_DATA:
        Number = apps.get_model('core', 'Number')
        Contest = apps.get_model('core', 'Contest')
        ContestNumber = apps.get_model('core', 'ContestNumber')
        ContestPrize = apps.get_model('core', 'ContestPrize')
        registered_contests = Contest.objects.values_list('reference', flat=True)
        new_contests = [c for c in CONTEST_DATA if c['contest']['reference'] not in registered_contests]
        Contest.objects.bulk_create([Contest(**c['contest']) for c in new_contests], ignore_conflicts=True)
        references = [c['contest']['reference'] for c in new_contests]
        map_contests = {c.reference: c for c in Contest.objects.filter(reference__in=references)}
        map_numbers = {n.value: n for n in Number.objects.all()}
        contest_number, contest_prize = [], []
        for item in new_contests:
            payload = map_contests[item['contest']['reference']]
            if payload:
                for num in item['numbers']:
                    contest_number.append(ContestNumber(contest=payload, number=map_numbers[num]))
                for prize in item['prizes']:
                    if prize['winners'] > 0:
                        contest_prize.append(ContestPrize(contest=payload, **prize))
        ContestNumber.objects.bulk_create(contest_number, ignore_conflicts=True)
        ContestPrize.objects.bulk_create(contest_prize, ignore_conflicts=True)
    return None

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0002_seed_numbers'),
    ]

    operations = [
        migrations.RunPython(seed_contests, migrations.RunPython.noop),
    ]

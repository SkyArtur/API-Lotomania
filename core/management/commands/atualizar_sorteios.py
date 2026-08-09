from django.core.management.base import BaseCommand, CommandError

from core.services import atualizar_sorteios


class Command(BaseCommand):
    help = (
        'Sincroniza os sorteios da Lotomania a partir de core/data/file/lotomania.csv '
        'e atualiza (ApostaSorteio, ApostaResultado, ApostaPremio) as apostas afetadas.'
    )

    def handle(self, *args, **options):
        resultado = atualizar_sorteios()

        if not resultado.criado and not resultado.falhou:
            self.stdout.write('Nenhum sorteio novo encontrado em lotomania.csv.')
            return

        for sorteio in resultado.criado:
            self.stdout.write(self.style.SUCCESS(f'Sorteio {sorteio.referencia:04d} importado.'))

        if resultado.falhou:
            for referencia, erro in resultado.falhou:
                self.stderr.write(self.style.ERROR(f'Sorteio {referencia:04d} falhou: {erro}'))
            raise CommandError(f'Falha ao importar {len(resultado.falhou)} sorteio(s).')

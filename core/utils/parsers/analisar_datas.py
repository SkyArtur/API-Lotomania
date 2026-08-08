import re
from datetime import date
from typing import Optional

__all__ = ['analisar_datas']


def analisar_datas(data: str, *, formato_iso: bool = False) -> Optional[date]:
    """
    Converte uma data em texto (padrão `dd/mm/aaaa` ou, se `formato_iso=True`,
    `aaaa-mm-dd`) em um `date`. Retorna `None` se o texto não bater com o
    formato esperado ou não for uma data válida.
    """
    try:

        padrao = r'^(\d{4})[/-]?(\d{2})[/-](\d{2})$' if formato_iso else r'^(\d{2})[/-]?(\d{2})[/-](\d{4})$'
        correspondencia = re.match(padrao, data)

        if not correspondencia:
            return None

        return date.fromisoformat(
            ''.join(
                correspondencia.groups()
                if formato_iso
                else correspondencia.groups()[::-1]
            )
        )

    except (TypeError, AttributeError, ValueError):
        return None

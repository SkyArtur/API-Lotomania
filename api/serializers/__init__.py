from .numero import NumeroSerializer
from .apostador import (
    ApostadorSerializer,
    ApostadorRegistroSerializer,
    ApostadorPerfilSerializer,
    ApostadorAlterarSenhaSerializer,
)
from .sorteio import (
    SorteioPremioSerializer,
    SorteioSerializer,
    SorteioModelSerializer,
    SorteioListSerializer,
    SorteioDetalheModelSerializer,
    SorteioCreateSerializer,
    SorteioNumeroListSerializer
)
from .aposta import (
    ApostaResultadoSerializer,
    ApostaPremioSerializer,
    ApostaModelSerializer,
    ApostaSerializer,
    ApostaNumeroListSerializer,
    ApostaListSerializer,
    ApostaDetalheSerializer,
    ApostaCreateSerializer
)


__all__ = [
    'NumeroSerializer',

    'ApostadorSerializer',
    'ApostadorRegistroSerializer',
    'ApostadorPerfilSerializer',
    'ApostadorAlterarSenhaSerializer',

    'SorteioPremioSerializer',
    'SorteioSerializer',
    'SorteioModelSerializer',
    'SorteioListSerializer',
    'SorteioDetalheModelSerializer',
    'SorteioCreateSerializer',
    'SorteioNumeroListSerializer',

    'ApostaResultadoSerializer',
    'ApostaPremioSerializer',
    'ApostaModelSerializer',
    'ApostaSerializer',
    'ApostaNumeroListSerializer',
    'ApostaListSerializer',
    'ApostaDetalheSerializer',
    'ApostaCreateSerializer',
]
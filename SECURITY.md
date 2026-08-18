# Política de Segurança

## Sobre este projeto

O **API-Lotomania** é um projeto pessoal e didático, mantido por uma única pessoa, sem SLA formal de resposta
nem programa de recompensa (*bug bounty*). Ainda assim, relatos de vulnerabilidade são levados a sério e
tratados com prioridade, na medida do tempo disponível.

## Versões suportadas

Por estar em desenvolvimento ativo (`0.x`, conforme [SemVer](https://semver.org/lang/pt-BR/)), apenas a versão
mais recente publicada recebe correções de segurança. Versões anteriores ficam registradas no histórico de
[tags](../../tags) por motivo de reprodutibilidade, mas não são corrigidas retroativamente.

| Versão   | Suportada          |
| -------- | ------------------- |
| 0.3.0    | :white_check_mark:  |
| < 0.3.0  | :x: (superada pela 0.3.0 — veja o [changelog](../../releases)) |

## Reportando uma vulnerabilidade

**Não abra uma Issue pública** para relatar uma vulnerabilidade — isso exporia o problema antes de existir uma
correção.

Use o recurso de [Private Vulnerability Reporting](../../security/advisories/new) do GitHub (aba **Security** →
**Report a vulnerability**, ou o link acima). O relato é privado, visível só para o mantenedor, e cria um espaço
de discussão dedicado até a correção ser publicada.

Ao reportar, inclua, se possível:

- Descrição do problema e o impacto potencial (ex.: exposição de dados de outro apostador, bypass de
  autenticação, injeção de SQL).
- Passos para reproduzir (endpoint, payload, headers relevantes).
- Versão/commit afetado.

## O que esperar depois do relato

Como é um projeto solo, não há prazo contratual de resposta, mas o objetivo é:

1. Confirmar o recebimento do relato o quanto antes.
2. Investigar e validar a vulnerabilidade.
3. Publicar uma correção em uma nova versão de patch (ex.: `0.1.1` → `0.1.2`).
4. Dar crédito a quem reportou (se desejado) nas notas da release correspondente.

## Escopo

Esta política cobre o código deste repositório (API Django REST Framework e sua containerização via Docker).
Não cobre vulnerabilidades em dependências de terceiros (Django, DRF, Celery, PostgreSQL, Redis, etc.) — essas
devem ser reportadas diretamente aos respectivos projetos. Vulnerabilidades de dependências já são monitoradas
neste repositório via Dependabot.

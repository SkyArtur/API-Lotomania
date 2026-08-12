# 🎲 API Lotomania

API REST construída com Django REST Framework para registro de apostas da Lotomania e acompanhamento dos sorteios
oficiais. Projeto de finalidade didática, voltado a uso pessoal e ao estudo prático do framework.

## 🛠️ Stack

- Django 6 + Django REST Framework
- PostgreSQL (produção) / SQLite (desenvolvimento)
- Autenticação via JWT (`djangorestframework-simplejwt`)
- Celery + Redis, para sincronização agendada dos sorteios
- drf-spectacular, para documentação OpenAPI/Swagger
- Docker Compose, para execução containerizada

## ⚙️ Funcionamento

O domínio da API gira em torno de quatro entidades principais:

- **Apostador** — usuário da aplicação. Autentica-se via JWT e é o único capaz de ver e gerenciar as próprias apostas.
- **Aposta** — uma aposta: 50 números escolhidos, intervalo de concursos válidos (`inicial`/`final`) e indicação de
  aposta espelhada (`espelho`). Toda aposta pertence a um único `Apostador` e só é visível para ele.
- **Sorteio** — um sorteio oficial da Lotomania: referência, data, os 20 números sorteados e a tabela de prêmios
  por faixa de pontos. O cadastro de novos sorteios só pode ser feito por um apostador autenticado; a consulta é
  pública.
- **Numero** — os números válidos de 0 a 99, usados tanto em apostas quanto em concursos. Não podem ser alterados
  pelo usuário — são criados automaticamente pelas migrações do app `core`.

Quando um sorteio novo é sincronizado, a API verifica automaticamente todas as apostas cujo intervalo
(`inicial`/`final`) cobre a referência daquele sorteio e recalcula, para cada uma delas, os acertos (`ApostaResultado`)
e as premiações correspondentes (`ApostaPremio`), vinculando a aposta ao sorteio (`ApostaSorteio`). Isso vale tanto para
sorteios importados via CSV quanto para sorteios cadastrados manualmente pela API.

### 🔐 Autenticação e principais endpoints

Prefixo comum a todos os endpoints: `/api-lotomania/`. A regra geral de acesso é "leitura pública, escrita
autenticada" (`IsAuthenticatedOrReadOnly`), mas cada view pode restringir isso conforme a sua necessidade — por
isso vale conferir a coluna **Acesso** de cada endpoint, e não assumir a regra geral por padrão.

| Método | Endpoint                   | Descrição                                          | Acesso         |
|--------|----------------------------|----------------------------------------------------|----------------|
| POST   | `token/`                   | Login — retorna `access`/`refresh` JWT             | 🔓 Público     |
| POST   | `token/refresh/`           | Renova o `access` token                            | 🔓 Público     |
| POST   | `apostador/`               | Cadastro de um novo usuário                        | 🔓 Público     |
| PATCH  | `apostador/senha/`         | Atualiza a senha do usuário autenticado            | 🔒 Autenticado |
| GET    | `apostador/perfil/`        | Dados do usuário autenticado                       | 🔒 Autenticado |
| POST   | `apostas/`                 | Cria uma nova aposta para o usuário autenticado    | 🔒 Autenticado |
| GET    | `apostas/`                 | Lista as apostas do usuário autenticado            | 🔒 Autenticado |
| GET    | `apostas/{id}/`            | Detalha uma aposta (somente do próprio usuário)    | 🔒 Autenticado |
| DELETE | `apostas/{id}/`            | Remove uma aposta (somente do próprio usuário)     | 🔒 Autenticado |
| GET    | `apostas/ultima-aposta/`   | Última aposta do usuário autenticado               | 🔒 Autenticado |
| GET    | `apostas/detalhadas/`      | Lista detalhada das apostas do usuário autenticado | 🔒 Autenticado |
| POST   | `sorteios/`                | Cadastra um sorteio manualmente                    | 🔒 Autenticado |
| GET    | `sorteios/`                | Lista os sorteios cadastrados                      | 🔓 Público     |
| GET    | `sorteios/ultimo-sorteio/` | Último sorteio cadastrado                          | 🔓 Público     |
| GET    | `sorteios/detalhados/`     | Lista de sorteios em detalhes                      | 🔓 Público     |
| GET    | `numeros/`                 | Lista os números válidos (0–99)                    | 🔓 Público     |
| GET    | `docs/`                    | Swagger UI                                         | 🔓 Público     |
| GET    | `docs/redoc/`              | Redoc UI                                           | 🔓 Público     |
| GET    | `schema/`                  | Especificação OpenAPI                              | 🔓 Público     |

> **📌 Importante:** `apostas/` é a exceção à regra "leitura pública" — todos os seus endpoints, inclusive os de
> `GET`, exigem autenticação, já que uma aposta só pode ser vista por quem a fez. Já `apostador/` inverte a lógica
> de escrita: o cadastro (`POST`) é o único endpoint de escrita público de toda a API, pois é assim que um novo
> apostador passa a existir.

## 💻 Execução local (sem Docker)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.exemple .env               # ajuste os valores conforme necessário

python manage.py migrate
python manage.py runserver
```

Por padrão (`DJANGO_ENV=development`), o banco usado é SQLite e não é necessário subir Postgres/Redis para a API
web responder. Para exercitar Celery localmente, é preciso um Redis acessível e as variáveis `CELERY_BROKER_URL`/
`CELERY_RESULT_BACKEND` apontando para ele.

## 🐳 Containerização

Os arquivos de Docker ficam em `/docker/`. O Compose deve ser executado a partir da raiz da API
(`API-Lotomania`), apontando para o arquivo dentro de `docker/`:

```bash
docker compose -f docker/docker-compose.yml up -d --build
```

Isso sobe cinco serviços: `db` (PostgreSQL), `redis`, `api` (Gunicorn, porta `8080`), `worker` e `beat` (Celery). 
A API fica disponível em `http://localhost:8085/api-lotomania/`.

> **📌 Importante:** as migrações não rodam automaticamente — aplique-as manualmente após o primeiro `up`:

```bash
docker compose -f docker/docker-compose.yml exec api python manage.py migrate
```

Outros comandos úteis:

```bash
docker compose -f docker/docker-compose.yml logs -f api      # logs da API
docker compose -f docker/docker-compose.yml exec api python manage.py createsuperuser
docker compose -f docker/docker-compose.yml down             # para os containers
docker compose -f docker/docker-compose.yml down -v          # para e remove os volumes (apaga o banco)
```

## 🔄 Atualização dos sorteios (`lotomania.csv`)

> **📌 Importante:** a API nunca busca resultados em nenhum serviço externo — nem ao vivo, nem em segundo plano.
> Os dados sempre chegam por um destes dois caminhos:

1. **Cadastro manual de um sorteio**, via `POST /api-lotomania/sorteios/` (endpoint que será usado futuramente
   pelo APP).
2. **Sincronização a partir do arquivo `core/data/file/lotomania.csv`**, descrita abaixo.

O fluxo do arquivo é inteiramente manual e fora do repositório: baixe a planilha oficial da Lotomania (`.xlsx`) no
site da Caixa, corrija/converta para `.csv` com sua própria ferramenta de linha de comando e substitua o arquivo em
`API-Lotomania/core/data/file/lotomania.csv`. Em produção (Docker), esse diretório é montado como volume somente leitura
nos serviços `api` e `worker`, então basta sobrescrever o arquivo no host — sem precisar reconstruir a imagem.

A partir daí, a sincronização com o banco acontece de duas formas, que podem ser usadas juntas sem conflito
(a operação é idempotente — sorteios já importados nunca são duplicados):

- **Automática** — o `beat` do Celery dispara a sincronização toda terça, quinta e sábado, às 21h
  (`America/Sao_Paulo`).
- **Sob demanda**, logo após substituir o arquivo, para não esperar o próximo ciclo agendado:

```bash
# via Docker
docker compose -f docker/docker-compose.yml exec api python manage.py atualizar_sorteios

# execução local (sem Docker)
python manage.py atualizar_sorteios
```

O comando reporta os concursos importados e, se algum registro do CSV falhar, os demais continuam sendo
processados normalmente — a falha é reportada ao final sem interromper o lote.

## ✅ Testes

```bash
python manage.py test core.tests api.tests
```

## 📄 Licença

Distribuído sob a licença MIT — veja [LICENSE](LICENSE).

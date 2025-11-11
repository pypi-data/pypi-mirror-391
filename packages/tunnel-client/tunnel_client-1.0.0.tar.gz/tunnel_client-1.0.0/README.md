# Tunnel System

## Клиент: установка и запуск

### Вариант 1. Установка из PyPI (рекомендуется)

После каждого изменения в `client/` пакет автоматически публикуется в PyPI.

```bash
pipx install tunnel-client
# или
pip install tunnel-client
```

### Вариант 2. Установка из GitLab Package Registry

После каждого изменения в `client/` пакет также публикуется в GitLab Package Registry.

**Для публичного проекта:**
```bash
pipx install tunnel-client \
  --index-url https://gitlab.com/api/v4/projects/PROJECT_ID/packages/pypi/simple \
  --extra-index-url https://pypi.org/simple
```

**Для приватного проекта:**
1. Создайте Personal Access Token с правами `read_api` и `read_repository`
2. Установите:
```bash
pipx install tunnel-client \
  --index-url https://__token__:YOUR_TOKEN@gitlab.com/api/v4/projects/PROJECT_ID/packages/pypi/simple \
  --extra-index-url https://pypi.org/simple
```

### Вариант 3. Установка из артефакта (wheel)
1. После пуша в `main/master` с изменениями в `client/` скачайте wheel из артефактов job `build_client`
2. Установите:
   ```bash
   pipx install dist/tunnel_client-*.whl
   ```

### Вариант 4. Установка из исходников
```bash
pip install .
# или в editable-режиме для разработки
pip install -e .
```

### Запуск клиента
```bash
tunnel-client --port 3000
```
Сервер по умолчанию: `wss://tunnel.tunneloon.online` (можно переопределить через `--server`)

## Сервер: деплой в Docker

### Автоматический деплой

При каждом изменении в `server_/` или `shared/`:
1. Автоматически собирается Docker образ
2. Образ пушится в GitLab Container Registry
3. Автоматически деплоится на сервер (перезапускается контейнер)

**Требуется настройка:**
- GitLab CI/CD Variables: `SSH_PRIVATE_KEY`, `SSH_USER`, `SERVER_HOST`
- На сервере должны быть созданы директории: `/opt/tunnel-server/{config.yaml,data,certs}`

### Ручной запуск контейнера
```bash
docker run -d \
  --name tunnel-server \
  --restart unless-stopped \
  --network host \
  -v /opt/tunnel-server/config.yaml:/app/config.yaml:ro \
  -v /opt/tunnel-server/certs:/app/certs:ro \
  -v /opt/tunnel-server/data:/app/data \
  -e SERVER_CONFIG=/app/config.yaml \
  registry.gitlab.com/YOUR_PROJECT/server:latest
```

## CI/CD (GitLab)

### Автоматические процессы:

**При изменении `server_/` или `shared/`:**
- `build_server_image` — сборка Docker образа
- `deploy_server_docker` — автоматический деплой на сервер

**При изменении `client/`, `shared/`, `setup.py` или `MANIFEST.in`:**
- `build_client` — сборка wheel + sdist (артефакты)
- `publish_client_gitlab` — автоматическая публикация в GitLab Package Registry
- `publish_client_pypi` — автоматическая публикация в PyPI

### Переменные для деплоя сервера
Задайте в GitLab → Settings → CI/CD → Variables:
- `SSH_PRIVATE_KEY` — приватный ключ для SSH
- `SSH_USER` — пользователь на сервере
- `SERVER_HOST` — адрес сервера
- (опц.) `SERVER_CONFIG_REMOTE`, `SERVER_CERTS_REMOTE`, `SERVER_DATA_REMOTE`, `SERVER_CONTAINER_NAME`, `SERVER_PORT_HTTP`, `SSH_PORT`

### Переменные для публикации в PyPI
Задайте в GitLab → Settings → CI/CD → Variables:
- `PYPI_USERNAME` — должно быть `__token__` (буквально так)
- `PYPI_PASSWORD` — ваш PyPI API token (создайте на https://pypi.org/manage/account/token/)

## Разработка
```bash
make install-dev       # инструменты разработки (ruff, black, mypy, build)
make pre-commit-install
make lint              # ruff
make fmt               # black
make build-client      # сборка пакета клиента
```

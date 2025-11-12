# imgctl

Консольная утилита для управления контейнерной платформой «Imagenarium».

## Описание

imgctl представляет собой консольную утилиту для управления контейнерной платформой «Imagenarium».

## Содержание

- [Описание](#описание)
- [Установка](#установка)
- [Быстрый старт](#быстрый-старт)
- [Конфигурация](#конфигурация)
- [Параметры подключения](#параметры-подключения)
- [Команды](#команды)
- [Заголовок консоли](#заголовок-консоли)
- [Использование в CI/CD](#использование-в-cicd)
- [Кэширование](#кэширование)
- [Управление колонками](#управление-колонками)
- [Форматы вывода](#форматы-вывода)
- [Фильтрация данных](#фильтрация-данных)
- [Безопасность](#безопасность)
- [Устранение неполадок](#устранение-неполадок)
- [Bash Completion](#bash-completion)

## Установка

### Системные требования

Для корректной работы imgctl необходимо обеспечить выполнение следующих системных требований:

- **Python**: версия 3.8 или выше (для установки через pip)
- **Сетевое подключение**: доступ к API-эндпоинтам «Imagenarium»
- **Операционная система**: Linux, macOS, Windows

### Способы установки

#### 1. Установка Windows Executable

Скачайте Windows executable из раздела релиза в GitLab или используйте прямую ссылку на Generic Packages:

```powershell
# Скачать Windows executable (замените 3.0.15 на нужную версию)
Invoke-WebRequest -Uri "https://gitlab.com/api/v4/projects/koden8%2Fimgctl/packages/generic/imgctl/3.0.15/imgctl.exe" -OutFile "imgctl.exe"

# Добавить в PATH (опционально)
# Переместите imgctl.exe в папку, которая уже в PATH, или добавьте текущую папку в PATH
$env:Path += ";$PWD"
```

#### 2. Установка через Homebrew (macOS)

```bash
# Добавить tap
brew tap koden8/homebrew-imgctl https://gitlab.com/koden8/homebrew-imgctl.git

# Установить imgctl
brew install imgctl

# Обновить
brew upgrade imgctl
```

#### 3. Установка через Docker

```bash
# Запуск последней версии
docker run --rm -it registry.gitlab.com/koden8/imgctl:latest

# Запуск конкретной версии
docker run --rm -it registry.gitlab.com/koden8/imgctl:3.0.15

# Создать алиас для удобства
alias imgctl='docker run --rm -it -v ~/.config/imgctl:/home/imgctl/.config/imgctl registry.gitlab.com/koden8/imgctl:latest'
```

**Примечание:** В Docker контейнерах imgctl автоматически использует `PlaintextKeyring` из `keyrings.alt.file` для сохранения паролей, так как системный keyring недоступен. Пароли хранятся в `~/.config/imgctl/keyring_pass.cfg` с правами доступа 600. Работает полностью автоматически без запросов пароля.

#### 4. Установка через pip (рекомендуется)

**С PyPI:**
```bash
# Обновить pip
pip install --upgrade pip

# Установить последнюю версию с PyPI
pip install imgctl

# Или установить конкретную версию
pip install imgctl==3.0.15
```

**Из исходников GitLab:**
```bash
# Скачать и установить из архивов GitLab
pip install https://gitlab.com/koden8/imgctl/-/archive/main/imgctl-main.tar.gz

# Или из релизов
pip install https://gitlab.com/koden8/imgctl/-/archive/v3.0.15/imgctl-v3.0.15.tar.gz
```

**Установка bash completion после установки через pip:**

```bash
# Найти и установить bash completion
COMPLETION_FILE=$(python3 -c "import os, imgctl; print(os.path.join(os.path.dirname(imgctl.__file__), 'imgctl-completion.bash'))")
bash "$COMPLETION_FILE" install

# Перезагрузите bash или выполните:
source ~/.bashrc
```

Или добавьте вручную в `~/.bashrc`:

```bash
# Добавить в ~/.bashrc
source $(python3 -c "import os, imgctl; print(os.path.join(os.path.dirname(imgctl.__file__), 'imgctl-completion.bash'))")
```

### Проверка установки

После завершения установки выполните проверку корректности установки:

```bash
# Проверка доступности команд
imgctl --help
```

### Устранение проблем установки

В случае возникновения проблем при установке:

1. **Проверьте версию Python**: `python3 --version` (требуется 3.8+)
2. **Обновите pip**: `pip install --upgrade pip`
3. **Установите зависимости вручную**: `pip install -e .`

#### Решение проблем с установкой

**Проблема: "No module named 'imgctl'"**
```bash
# Решение: переустановите пакет
pip uninstall imgctl
pip install --no-cache-dir imgctl
```

**Проблема: "Permission denied" при установке**
```bash
# Решение: используйте флаг --user
pip install --user imgctl
```

**Проблема: Устаревшая версия**
```bash
# Решение: обновите до последней версии
pip install --upgrade imgctl
```

## Быстрый старт

Данный раздел содержит пошаговое руководство по началу работы с imgctl.

### Этап 1: Настройка серверного подключения

Первоначальная настройка включает добавление сервера «Imagenarium» и настройку подключения:

```bash
# Добавление сервера с указанием параметров подключения
imgctl servers add dev \
  --url http://your-server:5555 \
  --username admin \
  --password your-password \
  --description "Development environment"

# Установка сервера по умолчанию для упрощения работы
imgctl servers set-default dev
```

### Этап 2: Проверка подключения и доступности ресурсов

После настройки сервера выполните проверку подключения и доступности ресурсов:

```bash
# Проверка подключения к серверу
imgctl servers test dev

# Получение списка доступных узлов
imgctl nodes list

# Проверка статуса реестров
imgctl registries list
```

### Этап 3: Управление компонентами и стеками

```bash
# Список всех компонентов
imgctl components list

# Детальная информация о компоненте
imgctl components get my-component

# Просмотр логов
imgctl logs my-component --follow
```

## Конфигурация

imgctl поддерживает несколько способов определения сервера (в порядке приоритета):

1. **Параметры командной строки** (высший приоритет): `--server`, `--username`, `--password`
2. **Переменные окружения**: `IMG_SERVER`, `IMG_USERNAME`, `IMG_PASSWORD`
3. **Файл конфигурации**: стандартный путь или через `--config`
4. **Сервер по умолчанию** из сохраненных серверов

### Примеры использования

```bash
# Через параметры командной строки (высший приоритет)
imgctl --server dev components list
imgctl --server http://server:5555 --username admin --password pass components list

# Через переменные окружения
IMG_SERVER=dev imgctl components list
IMG_SERVER=http://server:5555 IMG_USERNAME=admin IMG_PASSWORD=pass imgctl components list

# Через файл конфигурации
imgctl --config /path/to/config.yaml components list

# Через сервер по умолчанию (низший приоритет)
imgctl components list
```

### Пути к файлу конфигурации

imgctl автоматически ищет файл конфигурации в следующих местах:

| ОС | Путь | Пример полного пути |
|----|------|---------------------|
| **Linux** | `~/.config/imgctl/config.yaml` | `/home/username/.config/imgctl/config.yaml` |
| **macOS** | `~/.config/imgctl/config.yaml` | `/Users/username/.config/imgctl/config.yaml` |
| **Windows** | `%APPDATA%/imgctl/config.yaml` | `C:\Users\username\AppData\Roaming\imgctl\config.yaml` |

### Пример содержимого файла конфигурации

```yaml
server: "http://your-imagenarium-server:5555"
username: "your-username"
password: "your-password"
timeout: 30
verify_ssl: true
```

## Параметры подключения

### Параметры командной строки

| Параметр | Короткая форма | Описание | Пример |
|----------|----------------|----------|---------|
| `--server` | `-s` | Имя сервера или URL для подключения | `--server dev` или `--server http://server:5555` |
| `--username` | `-u` | Имя пользователя (для прямого подключения) | `--username admin` |
| `--password` | `-p` | Пароль (для прямого подключения) | `--password secret` |
| `--config` | `-c` | Путь к файлу конфигурации | `--config /path/to/config.yml` |
| `--verbose` | `-v` | Подробный вывод | `--verbose` |

### Переменные окружения

| Переменная | Описание | Пример |
|------------|----------|---------|
| `IMG_SERVER` | Имя сервера или URL для подключения | `IMG_SERVER=dev` или `IMG_SERVER=http://server:5555` |
| `IMG_USERNAME` | Имя пользователя (для прямого подключения) | `IMG_USERNAME=admin` |
| `IMG_PASSWORD` | Пароль (для прямого подключения) | `IMG_PASSWORD=secret` |

### Правила использования

1. **Приоритет**: Параметры командной строки имеют приоритет над переменными окружения
2. **URL vs имя сервера**: 
   - Если `IMG_SERVER` или `--server` содержит URL (начинается с `http://` или `https://`), то требуются `IMG_USERNAME` и `IMG_PASSWORD`
   - Если это имя сервера, то используются сохраненные учетные данные
3. **Безопасность**: Пароли в переменных окружения более безопасны, чем в командной строке

### Примеры конфигурации

```bash
# Использование имени сервера (используются сохраненные учетные данные)
imgctl --server dev components list
IMG_SERVER=dev imgctl components list

# Прямое подключение через URL
imgctl --server http://server:5555 --username admin --password secret components list
IMG_SERVER=http://server:5555 IMG_USERNAME=admin IMG_PASSWORD=secret imgctl components list

# Смешанное использование (сервер из переменной, учетные данные из параметров)
IMG_SERVER=http://server:5555 imgctl --username admin --password secret components list
```

## Команды

- `imgctl servers` - управление серверами
- `imgctl nodes` - управление нодами
- `imgctl stacks` - управление стеками
- `imgctl components` - управление компонентами
- `imgctl logs` - просмотр логов компонентов
- `imgctl registries` - управление реестрами
- `imgctl repositories` - управление репозиториями
- `imgctl shell` - интерактивная оболочка (REPL режим)

### Управление серверами

Команды для управления настройками серверов подключения.

#### Доступные команды

- `imgctl servers list` - список серверов
- `imgctl servers add <name>` - добавить новый сервер
- `imgctl servers get <name>` - информация о сервере
- `imgctl servers update <name>` - обновить настройки сервера
- `imgctl servers remove <name>` - удалить сервер
- `imgctl servers set-default <name>` - установить сервер по умолчанию
- `imgctl servers test <name>` - тестировать подключение

#### Доступные столбцы для `list`

- **NAME**: Имя сервера
- **URL**: URL сервера
- **USERNAME**: Имя пользователя
- **DESCRIPTION**: Описание сервера
- **DEFAULT**: Отметка сервера по умолчанию (✓)
- **PASSWORD**: Пароль (только с --show-passwords)

По умолчанию: NAME, URL, USERNAME, DESCRIPTION, DEFAULT

#### Параметры `servers list`

- `--columns <COLUMNS>` - список столбцов для отображения
- `--filter <FILTER>` - фильтр данных
- `--no-headers` - не показывать заголовки
- `--show-passwords` - показать пароли (не рекомендуется)
- `--output <FORMAT>` - формат вывода (table, json, yaml, tsv)

#### Примеры

```bash
# Список серверов
imgctl servers list

# Список с дополнительными столбцами
imgctl servers list --columns "NAME,URL,USERNAME,DESCRIPTION"

# Фильтр по имени
imgctl servers list --filter NAME=dev

# Фильтр по URL (регулярное выражение)
imgctl servers list --filter URL~registry

# Показать пароли (не рекомендуется)
imgctl servers list --show-passwords

# Добавление нового сервера
imgctl servers add dev --url http://dev.example.com:5555 --username admin --password secret

# Добавление сервера с настройками TTL
imgctl servers add prod \
  --url http://prod.example.com:5555 \
  --username admin \
  --password secret \
  --description "Production environment" \
  --ttl /deployments/list:10 \
  --ttl /deployments/tags:60

# Просмотр информации о сервере
imgctl servers get dev

# Просмотр с настройками TTL
imgctl servers get prod --format json

# Установка сервера по умолчанию
imgctl servers set-default dev

# Обновление сервера с новыми настройками TTL
imgctl servers update prod \
  --description "Updated production environment" \
  --ttl /api/v3/nodes:5 \
  --ttl /deployments/list:15

# Тестирование подключения
imgctl servers test dev

# Удаление сервера
imgctl servers remove dev
```

### Управление нодами

Команды для управления нодами (узлами) кластера.

#### Доступные команды

- `imgctl nodes list` - список нод
- `imgctl nodes get <name>` - детальная информация о ноде

#### Доступные столбцы для `list`

- **NAME**: Имя ноды
- **IP**: IP адрес  
- **ROLE**: Роль (manager/worker)
- **AVAILABILITY**: Доступность (ACTIVE/DRAIN/PAUSE)
- **STATUS**: Статус (READY/UNHEALTHY)
- **DC**: Дата-центр
- **DOCKER_VERSION**: Версия Docker
- **TOTAL_MEMORY**: Общий объем памяти (GB)
- **SSH_PORT**: SSH порт
- **SSH_USER**: SSH пользователь
- **EXTERNAL_URL**: Внешний URL
- **ID**: Уникальный идентификатор

По умолчанию: NAME, IP, ROLE, AVAILABILITY, STATUS

#### Параметры `nodes list`

- `--columns <COLUMNS>` - список столбцов для отображения
- `--filter <FILTER>` - фильтр данных  
- `--no-headers` - не показывать заголовки
- `--output <FORMAT>` - формат вывода (table, json, yaml, tsv)
- `--limit <N>` - ограничить количество записей

#### Примеры

```bash
# Список нод
imgctl nodes list

# Список нод с дополнительными столбцами
imgctl nodes list --columns "NAME,IP,DC,DOCKER_VERSION,TOTAL_MEMORY"

# Добавить/удалить столбцы
imgctl nodes list --columns "+TOTAL_MEMORY,-ID"

# Фильтр по статусу
imgctl nodes list --filter STATUS=READY

# Фильтр по роли
imgctl nodes list --filter ROLE=manager

# Фильтр по IP (регулярное выражение)
imgctl nodes list --filter IP~10.9

# Вывод без заголовков
imgctl nodes list --no-headers

# Детальная информация о ноде
imgctl nodes get node-01

# Обновление ноды
imgctl nodes update node-01 --role worker --availability drain
```

### Управление стеками

Команды для управления стеками развертываний.

#### Формат имен

Все имена стеков отображаются в формате `stack@namespace`:
- `database@production` - стек database в namespace production
- `web-api@staging` - стек web-api в namespace staging

Имена имеют цветовую подсветку: имя стека отображается белым, а `@namespace` - серым цветом для лучшей читаемости.

#### Доступные команды

- `imgctl stacks list` - список стеков
- `imgctl stacks get <stack>@<namespace>` - детальная информация о стеке
- `imgctl stacks template <stack>` - просмотр шаблонов стека
- `imgctl stacks diff <stack1> <stack2>` - сравнение шаблонов

#### Доступные столбцы для `list`

- **NAME**: Название стека (в формате stack@namespace)
- **NAMESPACE**: Пространство имен
- **VERSION**: Версия стека
- **STATUS**: Статус стека
- **REPO**: Репозиторий
- **COMMIT**: Git коммит
- **TIME**: Время развертывания
- **TAG**: Тег версии
- **PARAMETERS**: Параметры
- **COMPONENTS**: Компоненты

По умолчанию: NAME, NAMESPACE, VERSION, STATUS

#### Параметры `stacks list`

- `--columns <COLUMNS>` - список столбцов для отображения
- `--filter <FILTER>` - фильтр данных
- `--no-headers` - не показывать заголовки
- `--output <FORMAT>` - формат вывода (table, json, yaml, tsv)
- `--limit <N>` - ограничить количество записей

#### Примеры

```bash
# Список стеков
imgctl stacks list

# Список с дополнительными столбцами
imgctl stacks list --columns "NAME,NAMESPACE,VERSION,STATUS,REPO,COMMIT,TIME,TAG"

# Фильтр по статусу
imgctl stacks list --filter STATUS=deployed

# Фильтр по namespace
imgctl stacks list --filter NAMESPACE=production

# Фильтр по имени (регулярное выражение)
imgctl stacks list --filter NAME~database

# Вывод без заголовков
imgctl stacks list --no-headers

# Детальная информация о стеке
imgctl stacks get database@production
```

### Управление компонентами

Команды для управления компонентами развертываний.

#### Формат имен

Компоненты связаны со стеками в формате `stack@namespace`. В поле **STACK** отображается идентификатор стека в этом формате.

#### Доступные команды

- `imgctl components list` - список компонентов
- `imgctl components get <name>` - детальная информация о компоненте
- `imgctl components start <name>` - запуск компонента
- `imgctl components stop <name>` - остановка компонента
- `imgctl components upgrade` - обновление компонентов
- `imgctl components tags <name>` - список тегов компонента
- `imgctl components logs <name>` - просмотр логов

#### Доступные столбцы для `list`

- **NAME**: Имя компонента
- **NAMESPACE**: Пространство имен
- **STACK**: ID стека (в формате stack@namespace)
- **IMAGE**: Образ Docker
- **TAG**: Тег образа
- **STACK_VERSION**: Версия стека
- **STATUS**: Статус компонента
- **REPLICAS**: Количество реплик
- **PORTS**: Маппинг портов
- **UPDATED**: Дата обновления
- **CREATED**: Дата создания
- **REPO**: Репозиторий
- **COMMIT**: Git коммит
- **ADMIN_MODE**: Режим администратора
- **RUN_APP**: Запуск приложения
- **SHOW_ADMIN_MODE**: Показ режима администратора
- **OFF**: Выключен
- **NETWORKS**: Сетевые подключения

По умолчанию: NAME, NAMESPACE, IMAGE, TAG, UPDATED, STATUS

#### Статусы компонентов

- **RUNNING**: Компонент работает (все реплики запущены) - зеленый
- **STOPPED**: Компонент остановлен - серый
- **STARTING**: Компонент запускается - желтый
- **PARTIAL**: Частично работает (запущено меньше реплик чем желается) - желтый
- **OFF**: Компонент выключен - серый
- **BROKEN**: Компонент сломан (несоответствие версий между component и task) - желтый
- **CANCELED**: Операция отменена - красный

#### Параметры `components list`

- `--columns <COLUMNS>` - список столбцов для отображения
- `--filter <FILTER>` - фильтр данных
- `--no-headers` - не показывать заголовки
- `--output <FORMAT>` - формат вывода (table, json, yaml, tsv)
- `--limit <N>` - ограничить количество записей
- `--no-cache` - не использовать кэш

#### Параметры `components upgrade`

- `<component>[:tag]` - имена компонентов для обновления (по умолчанию обновляются все)
- `--filter <FILTER>` - фильтр компонентов для обновления
- `--to-tag <TAG>` - обновить до указанного тега
- `--from-file <FILE>` - загрузить список обновлений из файла
- `--check` - показать план обновления без выполнения
- `--dry-run` - предварительный просмотр без выполнения
- `--confirm` - подтвердить обновления без запроса (только с фильтрами)
- `--force` - принудительное обновление без проверки доступности тега
- `--no-cache` - не использовать кэш
- `--export-current` - экспорт текущих версий
- `--export-latest` - экспорт последних версий
- `--export-upgradable` - экспорт компонентов для обновления
- `--verbose` - подробный вывод HTTP запросов

#### Примеры

```bash
# Список компонентов
imgctl components list

# Список с дополнительными столбцами
imgctl components list --custom-columns "NAME,NAMESPACE,STACK,CREATED,REPO,COMMIT,PORTS"

# Фильтр по имени
imgctl components list --filter NAME~web-api-

# Фильтр по namespace
imgctl components list --filter NAMESPACE=production

# Фильтр по статусу
imgctl components list --filter STATUS=RUNNING

# Детальная информация о компоненте
imgctl components get web-api-staging

# Детальная информация без кэша
imgctl components get web-api-staging --no-cache

# Запуск компонента
imgctl components start web-api-staging

# Остановка компонента
imgctl components stop web-api-staging

# Обновление всех компонентов до последних тегов (по умолчанию)
imgctl components upgrade

# Обновление одного компонента до последнего тега
imgctl components upgrade web-api-staging

# Обновление до конкретного тега
imgctl components upgrade web-api-staging:v1.2.3

# Обновление нескольких компонентов
imgctl components upgrade web-api-staging db-staging:latest

# Обновление из файла (tab-separated формат)
imgctl components upgrade --from-file upgrades.txt

# Массовое обновление с фильтрами
imgctl components upgrade --filter NAME~^web-api- --to-tag v1.2.3

# Обновление всех компонентов в namespace staging до latest
imgctl components upgrade --filter NAMESPACE=staging --to-tag latest

# Обновление всех RUNNING компонентов
imgctl components upgrade --filter STATUS=RUNNING --to-tag v1.2.3

# Проверка плана обновления без выполнения
imgctl components upgrade --filter NAME~^web-api- --to-tag v1.2.3 --check

# Предварительный просмотр (dry-run)
imgctl components upgrade --filter NAMESPACE=production --to-tag latest --dry-run

# Подтверждение без интерактивного запроса
imgctl components upgrade web-api-staging --confirm
imgctl components upgrade --filter STATUS=RUNNING --to-tag v1.2.3 --confirm

# Принудительное обновление без проверки доступности тега
imgctl components upgrade --filter NAME~^web-api- --to-tag v1.2.3 --force

# Экспорт текущих версий
imgctl components upgrade --export-current

# Экспорт последних версий
imgctl components upgrade --export-latest

# Экспорт компонентов для обновления
imgctl components upgrade --export-upgradable
```

### Просмотр логов

Команда для просмотра логов компонентов.

#### Доступные команды

- `imgctl logs <component_name>` - просмотр логов компонента

#### Параметры

- `component_name` - имя компонента
- `--browser`, `-b` - открыть логи в браузере
- `--follow`, `-f` - следить за логами в реальном времени
- `--lines`, `-n <N>` - количество строк логов (по умолчанию: 50)
- `--tail`, `-t <N>` - количество последних записей для показа
- `--no-cache` - отключить кэширование
- `--no-headers` - не показывать заголовок консоли
- `--verbose`, `-v` - подробный вывод HTTP запросов

#### Примеры

```bash
# Показать последние 50 строк логов
imgctl logs web-service-production

# Открыть логи в браузере
imgctl logs web-service-production --browser

# Показать последние 100 строк
imgctl logs web-service-production --lines 100

# Следить за логами в реальном времени
imgctl logs web-service-production --follow

# Показать последние 20 записей
imgctl logs web-service-production --tail 20

# Просмотр логов без кэша
imgctl logs web-service-production --no-cache
```

### Управление реестрами

Команды для управления реестрами образов.

#### Доступные команды

- `imgctl registries list` - список реестров

#### Параметры `registries list`

- `--no-headers` - не показывать заголовки
- `--output <FORMAT>` - формат вывода (table, json, yaml, tsv)

#### Примеры

```bash
# Список реестров
imgctl registries list

# Список реестров без заголовков
imgctl registries list --no-headers
```

### Управление репозиториями

Команды для управления репозиториями образов.

#### Доступные команды

- `imgctl repositories list` - список репозиториев

#### Параметры `repositories list`

- `--no-headers` - не показывать заголовки
- `--output <FORMAT>` - формат вывода (table, json, yaml, tsv)

#### Примеры

```bash
# Список репозиториев
imgctl repositories list

# Список репозиториев без заголовков
imgctl repositories list --no-headers
```

### Управление тегами развертываний

Команда для просмотра доступных тегов для компонента.

#### Доступные команды

- `imgctl components tags <name>` - список тегов компонента

#### Параметры

- `<name>` - имя компонента (например, "web-api-staging")
- `--limit <N>` - ограничить количество записей
- `--no-cache` - не использовать кеш

#### Примеры

```bash
# Список тегов развертываний для компонента
imgctl components tags web-api-staging

# Список тегов с ограничением количества
imgctl components tags web-api-staging --limit 10

# Список тегов без кэша (принудительное обновление)
imgctl components tags web-api-staging --no-cache
```

Команда автоматически извлекает репозиторий и образ из информации о компоненте. Используется двухуровневое кэширование: информация о компоненте кэшируется на 1 час, теги на 5 минут.

### Интерактивная оболочка (REPL)

Команда для запуска интерактивной оболочки imgctl (REPL режим).

#### Доступные команды

- `imgctl shell` - запустить интерактивную оболочку
- `imgctl shell <server>` - запустить с указанием сервера

#### Возможности shell

- **Автодополнение**: полное автодополнение команд, опций и имен ресурсов по Tab
- **История команд**: сохранение истории между сессиями в `~/.imgctl_history`
- **Цветовой промпт**: динамический промпт с именем консоли и цветом из конфигурации
- **Фоновое обновление кэша**: автоматическое обновление кэша в фоне для быстрого автодополнения
- **Быстрые команды**: `exit`, `quit`, `help`, `clear`
- **Сохранение контекста**: все команды выполняются в контексте shell

#### Параметры

- `<server>` - имя сервера для использования (опционально)
- Свертывающееся меню автодополнения не отображается
- История команд работает между сессиями

#### Примеры

```bash
# Запуск shell с текущим сервером
imgctl shell

# Запуск shell с указанием сервера dev
imgctl shell dev

# Запуск shell с сервером stage
imgctl shell stage
```

#### Использование внутри shell

```bash
# Вход в shell (промпт содержит имя консоли из конфигурации)
$ imgctl shell
dev> 

# Выполнение команд внутри shell
dev> components list
dev> components get web-api-staging
dev> nodes list --filter STATUS=READY

# Использование автодополнения (Tab)
dev> components get web-api-<TAB>
# → web-api-staging web-api-production

# Быстрые команды
dev> help          # Показать справку
dev> clear         # Очистить экран
dev> exit          # Выйти из shell
dev> quit          # Выйти из shell
```

#### Особенности

- **Без выпадающего меню**: автодополнение по Tab без визуального меню
- **Цветовой промпт**: показывает имя консоли из конфигурации сервера
- **Фоновое обновление**: кэш компонентов обновляется в фоне для актуального автодополнения
- **История команд**: используйте стрелки вверх/вниз для навигации по истории
- **Контекст сервера**: при указании сервера все команды выполняются в его контексте

#### Кэширование в shell

- Компоненты кэшируются на 5 минут для быстрого автодополнения
- Кэш автоматически обновляется в фоне
- Принудительное обновление: используйте `--no-cache` внутри команд

## Заголовок консоли

imgctl автоматически отображает персонализированный заголовок консоли для визуальной идентификации сервера. Заголовок содержит название консоли и версию системы, отображается цветом, настроенным в конфигурации сервера.

### Формат заголовка

```
᪣ Imagenarium: NEW PRE-PROD                                             v3.2.1
```

- **Левая часть**: `᪣ Imagenarium: {consoleName}` - название консоли из конфигурации
- **Правая часть**: `v{version}` - версия системы
- **Цвет**: Заливка цветом `consoleColor` из конфигурации сервера
- **Адаптивность**: Цвет текста автоматически адаптируется под фон терминала (черный для светлых терминалов, белый для темных)
- **Ширина**: Растягивается на всю ширину терминала
- **Совместимость**: Автоматически определяет тип терминала и его цветовую схему

### Управление отображением

Заголовок автоматически скрывается в следующих случаях:

```bash
# Отключение заголовка и заголовков колонок
imgctl components list --no-headers

# Программный вывод (JSON, YAML, TSV)
imgctl components list --output json
imgctl components list --output yaml
imgctl components list --output tsv

# Комбинированное использование
imgctl components list --no-headers --output json
```

### Кэширование конфигурации

- **Конфиг консоли**: Кэшируется на 24 часа для оптимизации производительности
- **Версия системы**: Кэшируется на 1 час, но в заголовке консоли всегда получается актуальная версия
- **Fallback**: При ошибках отображается заголовок по умолчанию

## Использование в CI/CD

### Docker образ для CI/CD

imgctl предоставляет готовый Docker образ для использования в CI/CD пайплайнах, что позволяет выполнять операции управления компонентами без установки Python окружения.

#### Получение Docker образа

```bash
# Официальный образ из GitLab Container Registry
docker pull registry.gitlab.com/koden8/imgctl:latest

# Или с Docker Hub (если опубликован)
docker pull your-org/imgctl:latest
```

### GitLab CI/CD пример

#### Обновление компонентов в production

```yaml
# .gitlab-ci.yml
stages:
  - deploy

deploy_production:
  stage: deploy
  image: registry.gitlab.com/koden8/imgctl:latest
  variables:
    IMG_SERVER: production
    IMG_USERNAME: $CI_DEPLOY_USER
    IMG_PASSWORD: $CI_DEPLOY_PASSWORD
  script:
    # Обновление компонента до новой версии
    - imgctl components upgrade my-app --to-tag $CI_COMMIT_TAG
  only:
    - tags
  when: manual
```

### Переменные окружения

```bash
# Подключение к серверу
IMG_SERVER=production                    # Имя сервера или URL
IMG_USERNAME=ci-user                     # Пользователь для CI
IMG_PASSWORD=secure-password             # Пароль (используйте GitLab Variables)
```

### Безопасность

Используйте GitLab Variables для хранения паролей:
- `IMG_PASSWORD`: secure-password (Masked)
- `IMG_USERNAME`: ci-user (Protected)

## Кэширование

imgctl использует кэширование для ускорения работы:

### Стратегия кэширования:

- **`components list`** - TTL 5 секунд (быстрое обновление данных)
- **`components get`** - TTL 5 секунд (быстрое обновление данных)  
- **`components start`** - поиск ID кэшируется на 1 час
- **`components tags`** - информация о компоненте кэшируется на 1 час, теги на 5 минут
- **`logs`** - поиск ID компонента кэшируется на 1 час
- **`nodes`, `repositories`, `registries`** - без кэша (всегда свежие данные)

### Параметр `--no-cache`:

Все команды, использующие кэш, поддерживают параметр `--no-cache` для принудительной инвалидации кэша и загрузки свежих данных:

```bash
# Принудительно загрузить свежие данные
imgctl components list --no-cache
imgctl components get web-api-staging --no-cache
imgctl components start web-api-staging --no-cache
imgctl components tags web-api-staging --no-cache
imgctl logs web-api-staging --no-cache
```

### Управление кэшем:

Кэш автоматически управляется системой. Для принудительного обновления данных используйте параметр `--no-cache` в соответствующих командах.

## Управление колонками

imgctl предоставляет гибкую систему управления отображаемыми колонками для всех команд `list`. Вы можете явно указать нужные колонки или модифицировать набор колонок по умолчанию.

### Способы указания колонок

#### 1. Явное указание (замена набором по умолчанию)

Указываете полный список колонок через запятую:

```bash
# Показать только имя и статус
imgctl components list --columns "NAME,STATUS"

# Несколько колонок
imgctl nodes list --columns "NAME,IP,ROLE,STATUS"
imgctl stacks list --columns "NAME,NAMESPACE,VERSION,STATUS,REPO"
```

#### 2. Добавление/удаление колонок относительно набора по умолчанию

Используйте префиксы `+` для добавления и `-` для удаления:

```bash
# Добавить колонку REPLICAS к набору по умолчанию
imgctl components list --columns "+REPLICAS"

# Удалить колонку NAMESPACE из набора по умолчанию
imgctl components list --columns "-NAMESPACE"

# Добавить несколько колонок
imgctl components list --columns "+REPLICAS,+PORTS"

# Удалить несколько колонок
imgctl components list --columns "-UPDATED,-TAG"

# Комбинированное: добавить REPLICAS и удалить NAMESPACE
imgctl components list --columns "+REPLICAS,-NAMESPACE"

# Добавить STACK и REPLICAS
imgctl components list --columns "+STACK,+REPLICAS"

# Убрать UPDATED и STATUS
imgctl components list --columns "-UPDATED,-STATUS"
```

### Доступные колонки по командам

#### Components

**Колонки по умолчанию:** NAME, NAMESPACE, IMAGE, TAG, UPDATED, STATUS

**Доступные колонки:**
- NAME, NAMESPACE, STACK, IMAGE, TAG, STACK_VERSION
- STATUS, REPLICAS, PORTS, UPDATED, CREATED
- REPO, COMMIT, ADMIN_MODE, RUN_APP
- SHOW_ADMIN_MODE, OFF, NETWORKS, ENV
- ENV.<переменная> (динамические переменные окружения)

#### Nodes

**Колонки по умолчанию:** NAME, IP, ROLE, AVAILABILITY, STATUS

**Доступные колонки:**
- NAME, IP, ROLE, AVAILABILITY, STATUS
- DC, DOCKER_VERSION, TOTAL_MEMORY
- SSH_PORT, SSH_USER, EXTERNAL_URL, ID

#### Stacks

**Колонки по умолчанию:** NAME, NAMESPACE, VERSION, STATUS

**Доступные колонки:**
- NAME, NAMESPACE, VERSION, STATUS
- REPO, COMMIT, TIME, TAG, PARAMS
- COMPONENTS, PARAMS.<параметр> (динамические параметры)

#### Servers

**Колонки по умолчанию:** NAME, URL, USERNAME, DESCRIPTION, DEFAULT

**Доступные колонки:**
- NAME, URL, USERNAME, DESCRIPTION, DEFAULT, PASSWORD

### Примеры использования

```bash
# Только имя и статус для быстрого просмотра
imgctl components list --columns "NAME,STATUS"

# Расширенный набор колонок
imgctl components list --columns "NAME,NAMESPACE,IMAGE,TAG,STATUS,REPLICAS,PORTS"

# Добавить REPLICAS к набору по умолчанию
imgctl components list --columns "+REPLICAS"

# Убрать TAG и NAMESPACE, оставить остальное
imgctl components list --columns "-TAG,-NAMESPACE"

# Полный набор для детального анализа
imgctl components list --columns "NAME,NAMESPACE,STACK,IMAGE,TAG,STATUS,REPLICAS,PORTS,UPDATED"

# Строки вывода без лишних деталей
imgctl components list --columns "NAME,IMAGE,TAG"
imgctl nodes list --columns "NAME,IP,STATUS"
imgctl stacks list --columns "NAME,NAMESPACE,STATUS"

# Показать переменные окружения для компонентов
imgctl components list --columns "+ENV"

# Показать конкретную переменную окружения
imgctl components list --columns "+ENV.DB_HOST,+ENV.DB_PORT"
```

### Динамические колонки

#### Переменные окружения (ENV)

Компоненты могут иметь динамические переменные окружения, доступные как отдельные колонки:

```bash
# Показать все переменные окружения
imgctl components list --columns "+ENV"

# Показать конкретные переменные
imgctl components list --columns "NAME,STATUS,+ENV.DB_HOST,+ENV.DB_PORT,+ENV.APP_NAME"

# Фильтрация по переменным окружения
imgctl components list --filter ENV.DB_HOST=localhost --columns "+ENV.DB_HOST"
```

#### Параметры стека (PARAMS)

Стеки могут содержать динамические параметры:

```bash
# Показать все параметры
imgctl stacks list --columns "+PARAMS"

# Показать конкретные параметры
imgctl stacks list --columns "NAME,VERSION,+PARAMS.database,+PARAMS.version"
```

### Сочетание с другими опциями

Колонки можно комбинировать с фильтрацией, форматами вывода и другими опциями:

```bash
# Фильтр + выбор колонок
imgctl components list --filter STATUS=RUNNING --columns "NAME,STATUS,REPLICAS"

# Выбор колонок + JSON
imgctl components list --columns "NAME,STATUS" --output json

# Ограничение + колонки + фильтр
imgctl components list --limit 5 --columns "NAME,STATUS" --filter NAMESPACE=production

# Без заголовков + выбор колонок
imgctl components list --columns "NAME,STATUS" --no-headers

# YAML + выбор колонок
imgctl stacks list --columns "NAME,NAMESPACE,VERSION" --output yaml
```

### Советы по использованию

1. **Быстрый просмотр**: Используйте `--columns "NAME,STATUS"` для компактного вывода
2. **Добавление деталей**: Используйте префикс `+` для добавления колонок к набору по умолчанию
3. **Минималистичный вывод**: Используйте `--columns "-TAG,-UPDATED"` для упрощения
4. **Автоматизация**: Комбинируйте с `--no-headers --output json` для скриптов
5. **Экспорт**: Для программной обработки используйте фиксированный набор колонок

**Примечание:** Компоненты, начинающиеся с "monitor-", автоматически исключаются из вывода для упрощения отображения.

## Форматы вывода

imgctl предоставляет комплексную систему форматирования вывода данных, обеспечивающую интеграцию с различными инструментами и системами.

### Обзор поддерживаемых форматов

Система поддерживает следующие форматы вывода, оптимизированные для различных сценариев использования:

| Формат | Назначение | Особенности |
|--------|------------|-------------|
| `table` | Интерактивный просмотр | Цветовое кодирование, адаптивная ширина |
| `json` | Программная обработка | Атрибуты в lowercase, структурированные данные |
| `yaml` | Конфигурационные файлы | Человекочитаемый формат, атрибуты в lowercase |
| `tsv` | Экспорт без заголовков колонок | Табуляция как разделитель, без заголовков |
| `"{COLUMN}..."` | Пользовательские шаблоны | Гибкое форматирование, синтаксис `{NAME}` |

### Детальное описание форматов

#### Табличный формат (по умолчанию)
- **Назначение**: Интерактивный просмотр и анализ данных
- **Особенности**: 
  - Цветовое кодирование статусов и состояний
  - Адаптивная ширина под размер терминала
  - Визуальное выделение совпадений при фильтрации
  - Форматирование заголовков

#### JSON формат
- **Назначение**: Программная обработка и интеграция с API
- **Особенности**:
  - Атрибуты в lowercase для соответствия стандартам JSON
  - Полное удаление Rich markup для чистых данных
  - Структурированный формат для автоматизированной обработки
  - Совместимость с инструментами типа jq, yq

#### YAML формат
- **Назначение**: Конфигурационные файлы и документирование
- **Особенности**:
  - Человекочитаемый формат с отступами
  - Атрибуты в lowercase для стандартизации
  - Поддержка Unicode и специальных символов
  - Идеален для версионирования конфигураций

#### TSV формат
- **Назначение**: Экспорт без заголовков колонок для автоматизированной обработки
- **Особенности**:
  - Без заголовков колонок (только данные)
  - Табуляция как разделитель
  - Идеален для скриптов и автоматизации
  - Поддержка импорта в Google Sheets, LibreOffice

#### Пользовательские шаблоны
- **Назначение**: Гибкое форматирование под специфические требования
- **Особенности**:
  - Синтаксис `{COLUMN}` для простоты использования
  - Поддержка многострочных шаблонов с `\n`
  - UPPERCASE имена столбцов для консистентности
  - Полное удаление Rich markup в выводе

### Практические примеры использования

#### Сценарий 1: Программная обработка данных
```bash
# Получение данных в JSON формате для автоматизированной обработки
imgctl components list --output json --limit 5

# Фильтрация и обработка с помощью jq
imgctl components list --output json | jq '.[] | select(.status=="RUNNING")'

# Экспорт в файл для дальнейшего анализа
imgctl components list --output json > components.json
```

#### Сценарий 2: Конфигурационное управление
```bash
# Генерация YAML конфигурации для систем управления
imgctl stacks list --output yaml

# Создание конфигурационных файлов
imgctl servers list --output yaml > servers-config.yaml
```

#### Сценарий 3: Отчетность и аналитика
```bash
# Экспорт данных в TSV для автоматизированной обработки
imgctl nodes list --output tsv > infrastructure-report.tsv

# Создание отчетов с фильтрацией
imgctl components list --filter STATUS=RUNNING --output tsv > running-components.tsv
```

#### Сценарий 4: Пользовательские форматы вывода
```bash
# Простое форматирование для скриптов
imgctl components list --output "{NAME} - {STATUS}"

# Многострочные шаблоны для детальной информации
imgctl servers list --output "Server: {NAME}\nURL: {URL}\nDefault: {DEFAULT}"

# Комбинирование с фильтрацией
imgctl components list --filter NAMESPACE=production --output "{NAME}: {STATUS}"
```

#### Сценарий 5: Интеграция с системами
```bash
# Комбинирование фильтрации и форматирования
imgctl components list --filter STATUS=RUNNING --output json
imgctl stacks list --filter NAMESPACE=production --output yaml
imgctl nodes list --columns "NAME,IP,STATUS" --output tsv
```

### Шаблоны (template формат):

Шаблоны используют синтаксис `{COLUMN}`, где `COLUMN` - имя столбца в UPPERCASE:

```bash
# Простой шаблон
--output "{NAME}: {STATUS}"

# Многострочный шаблон
--output "Component: {NAME}\nNamespace: {NAMESPACE}\nImage: {IMAGE}:{TAG}"

# С дополнительным текстом
--output "Component {NAME} in {NAMESPACE} is {STATUS}"
```

## Фильтрация данных

Система фильтрации поддерживает следующие возможности:

- **Множественные фильтры**: возможность применения нескольких условий одновременно
- **Визуальное выделение**: автоматическая подсветка совпадающих результатов
- **Гибкие операторы**: поддержка различных типов сравнения
- **Регулярные выражения**: продвинутый поиск по шаблонам
- **Типизированные сравнения**: автоматическое определение типов данных

### Поддерживаемые операторы фильтрации

| Оператор | Описание | Пример использования |
|----------|----------|---------------------|
| `=` | Точное совпадение | `STATUS=RUNNING` |
| `!=` | Не равно | `NAMESPACE!=test` |
| `~` | Регулярное выражение | `NAME~database` |
| `>` | Больше (для дат/чисел) | `REPLICAS>1` |
| `<` | Меньше (для дат/чисел) | `UPDATED<2025-01-01` |
| `>=` | Больше или равно | `REPLICAS>=2` |
| `<=` | Меньше или равно | `UPDATED<=2025-12-31` |

### Система визуального выделения совпадений

При использовании фильтров в табличном выводе система автоматически применяет визуальное выделение:

- **Оператор точного совпадения (`=`)**: выделяет весь текст при полном соответствии
- **Оператор регулярного выражения (`~`)**: выделяет только совпадающие фрагменты
- **Универсальность**: работает со всеми типами столбцов (NAME, STATUS, NAMESPACE и др.) для всех команд (components, stacks, nodes и др.)
- **Цветовое кодирование**: использует желтый цвет для оптимальной видимости
- **Сохранение базовой подсветки**: основная подсветка статусов и имен сохраняется, совпадения фильтров подсвечиваются дополнительно

### Примеры использования:

```bash
# Простые фильтры
imgctl components list --filter STATUS=RUNNING
imgctl components list --filter NAMESPACE=production
imgctl components list --filter NAME~database

# Исключение тестовых namespace
imgctl components list --filter NAMESPACE!=test

# Множественные фильтры
imgctl components list --filter STATUS=RUNNING --filter NAMESPACE=production

# Поиск по прокси (proxy компоненты)
imgctl components list --filter NAME~proxy

# Фильтрация по датам
imgctl components list --filter UPDATED>2025-01-01

# Фильтрация по числовым значениям
imgctl components list --filter REPLICAS>1

# Комбинирование с другими опциями
imgctl components list --filter STATUS=RUNNING --columns "NAME,STATUS" --limit 5

# Практические сценарии
imgctl components list --filter NAMESPACE=production --filter STATUS=RUNNING  # Все работающие компоненты в production
imgctl components list --filter NAME~api --filter NAMESPACE=production        # API компоненты в production
imgctl components list --filter STATUS=OFF                                 # Остановленные компоненты

# Примеры с подсветкой совпадений (в табличном выводе)
imgctl components list --filter NAME=database-production --columns NAME       # Подсветит "database-production"
imgctl components list --filter NAME~database --columns NAME               # Подсветит "database" в именах
imgctl components list --filter STATUS=RUNNING --columns NAME,STATUS       # Подсветит "RUNNING" в статусах
imgctl stacks list --filter NAME~api --columns NAME                        # Подсветит "api" в именах стеков
imgctl stacks list --filter STATUS=deployed --columns NAME,STATUS          # Подсветит "deployed" в статусах
```

### Доступные колонки для фильтрации:

Список доступных колонок для фильтрации см. в разделе [Управление колонками](#управление-колонками).

## TTL кэширования

imgctl использует кэширование для ускорения работы:

### TTL для команд:

- **`components list`** - TTL 5 секунд (быстрое обновление данных)
- **`components get`** - TTL 5 секунд (быстрое обновление данных)  
- **`components start`** - поиск ID кэшируется на 1 час
- **`components tags`** - информация о компоненте кэшируется на 1 час, теги на 5 минут
- **`logs`** - поиск ID компонента кэшируется на 1 час
- **`nodes`, `repositories`, `registries`** - без кэша (всегда свежие данные)

### Параметр `--no-cache`:

Все команды, использующие кэш, поддерживают параметр `--no-cache` для принудительной инвалидации кэша и загрузки свежих данных:

```bash
# Принудительно загрузить свежие данные
imgctl components list --no-cache
imgctl components get web-api-staging --no-cache
imgctl components start web-api-staging --no-cache
imgctl components tags web-api-staging --no-cache
imgctl logs web-api-staging --no-cache
```

### Управление кэшем:

Кэш автоматически управляется системой. Для принудительного обновления данных используйте параметр `--no-cache` в соответствующих командах.

## Безопасность

imgctl реализует комплексные меры безопасности для защиты чувствительных данных и обеспечения безопасной работы с контейнерной платформой «Imagenarium».

### Обзор безопасности

imgctl обрабатывает чувствительные данные, включая:
- **Cookies сессий** для аутентификации
- **Кеш API запросов** с потенциально чувствительной информацией
- **Конфигурацию серверов** с учетными данными
- **Пароли** для доступа к серверам

Все эти данные защищены многоуровневой системой безопасности.

### Защита файлов данных

#### Расположение файлов

imgctl хранит данные в стандартных директориях согласно канонам операционных систем:

**Linux/macOS:**
- Конфигурация: `~/.config/imgctl/`
- Кеш: `~/.cache/imgctl/`

**Windows:**
- Конфигурация: `%APPDATA%/imgctl/`
- Кеш: `%LOCALAPPDATA%/imgctl/cache/`

#### Типы защищаемых файлов

| Файл | Содержимое | Защита |
|------|------------|--------|
| `servers.json` | Конфигурация серверов | Права доступа + атомарная запись |
| `cookies.json` | Cookies сессий | Права доступа + атомарная запись |
| `cache.json` | Кеш API запросов | Права доступа + атомарная запись |
| `cache_config.json` | Настройки кеширования | Права доступа + атомарная запись |

### Меры безопасности

#### Права доступа к файлам

**Директории:**
- `0o700` (rwx------) - только владелец может читать/писать/выполнять

**Файлы:**
- `0o600` (rw-------) - только владелец может читать/писать

#### Атомарная запись файлов

- **Предотвращение повреждения** файлов при сбоях
- **Исключение race conditions** при одновременном доступе
- **Обеспечение консистентности** данных
- **Использование временных файлов** с последующим атомарным перемещением

#### Шифрование чувствительных данных

- **PBKDF2** с SHA-256 для генерации ключей
- **Fernet** (AES 128 в CBC режиме) для симметричного шифрования
- **100,000 итераций** PBKDF2 для защиты от атак перебора
- **Уникальные ключи** на основе данных пользователя и машины

#### Безопасное хранение паролей

- **Системный keyring** для хранения паролей (macOS Keychain, Windows Credential Manager, SecretService) - используется автоматически если доступен
- **Автоматическое переключение** на `PlaintextKeyring` из `keyrings.alt.file` при недоступности системного keyring
- **В контейнерах и окружениях без GUI:**
  - Автоматически используется `PlaintextKeyring` (без пароля, без запросов)
  - Пароли хранятся в файле `~/.config/imgctl/keyring_pass.cfg` (права доступа 600)
  - Защита обеспечивается правами файловой системы
  - Пароли сохраняются в base64-кодированном виде
- **Простота и надежность:**
  - Минимальная зависимость от внешних библиотек
  - Автоматическое определение и использование доступного бэкенда
  - Работает везде: локально, в контейнерах, без дополнительных настроек

### Рекомендации по безопасности

#### Для пользователей

1. **Регулярно обновляйте** imgctl до последней версии
2. **Не передавайте** файлы конфигурации другим пользователям
3. **Используйте сильные пароли** для серверов
4. **Используйте параметр `--no-cache`** при работе на общих машинах для принудительного обновления данных:
   ```bash
   imgctl components list --no-cache
   imgctl components get web-api-staging --no-cache
   ```

#### Для системных администраторов

1. **Мониторьте права доступа** к директориям imgctl
2. **Настройте ротацию логов** для отслеживания доступа
3. **Используйте SELinux/AppArmor** для дополнительной защиты
4. **Регулярно проверяйте** целостность файлов конфигурации

### Проверка прав доступа

```bash
# Проверка прав доступа к директории кеша
ls -la ~/.cache/imgctl/
# drwx------ 2 user user 4096 Jan 15 10:00 .

# Проверка прав доступа к файлам
ls -la ~/.cache/imgctl/cache.json
# -rw------- 1 user user 1024 Jan 15 10:00 cache.json
```

### Устранение проблем безопасности

#### Неправильные права доступа

**Симптомы:**
- Ошибки доступа к файлам
- Предупреждения о небезопасных правах

**Решение:**
```bash
# Исправление прав доступа к директории
chmod 700 ~/.cache/imgctl
chmod 700 ~/.config/imgctl

# Исправление прав доступа к файлам
chmod 600 ~/.cache/imgctl/*.json
chmod 600 ~/.config/imgctl/*.json
```

#### Поврежденные файлы

**Симптомы:**
- Ошибки при загрузке конфигурации
- Некорректная работа кеша

**Решение:**
```bash
# Удаление поврежденных файлов
rm ~/.cache/imgctl/cache.json
rm ~/.config/imgctl/servers.json

# Пересоздание конфигурации
imgctl servers add my-server --url https://example.com --username admin --password secret
```

### Отладка проблем безопасности

```bash
# Включение подробного вывода для отладки
imgctl --verbose components list

# Проверка прав доступа
ls -la ~/.cache/imgctl/ ~/.config/imgctl/

# Проверка содержимого файлов (осторожно!)
file ~/.cache/imgctl/cache.json
```

## Устранение неполадок

### Проблемы с подключением

**Ошибка: "Не удалось определить конфигурацию сервера"**
```bash
# Решение: добавьте сервер
imgctl servers add dev --url http://your-server:5555 --username admin --password your-password
imgctl servers set-default dev
```

**Ошибка: "Ошибка API: 401 Unauthorized"**
```bash
# Решение: проверьте учетные данные
imgctl servers test dev
# Или обновите пароль
imgctl servers add dev --url http://your-server:5555 --username admin --password new-password
```

**Ошибка: "Connection refused"**
```bash
# Решение: проверьте URL сервера и доступность
curl -I http://your-server:5555
```

**Ошибка: "No recommended backend was available" при сохранении пароля в контейнере**
```bash
# Решение: imgctl автоматически использует PlaintextKeyring из keyrings.alt
# Все необходимые зависимости включены в пакет imgctl

# Проверьте что пароль сохранен:
ls -la ~/.config/imgctl/keyring_pass.cfg
# Файл должен существовать с правами 600
```

### Проблемы с кэшем

**Устаревшие данные в выводе команд**
```bash
# Решение: принудительно обновите кэш
imgctl components list --no-cache
imgctl components get my-component --no-cache
```

**Ошибка: "Компонент не найден в кэше"**
```bash
# Решение: обновите кэш и повторите попытку
imgctl components list --no-cache
imgctl logs my-component --no-cache
```

### Проблемы с логами

**Логи не отображаются или показывают ошибку 404**
```bash
# Решение: обновите кэш компонентов
imgctl logs my-component --no-cache
```

**Медленная загрузка логов**
```bash
# Решение: используйте фильтрацию или ограничение строк
imgctl logs my-component --lines 50
imgctl logs my-component --level ERROR
```

### Проблемы с Bash Completion

**Автодополнение не работает**
```bash
# Решение: переустановите completion
./imgctl-completion.bash uninstall
./imgctl-completion.bash install
source ~/.bashrc
```

**Автодополнение показывает устаревшие данные**
```bash
# Решение: очистите кэш completion
rm -rf ~/.cache/imgctl/
./imgctl-completion.bash test
```

### Отладка

**Включите подробный вывод**
```bash
imgctl --verbose components list
```

**Проверьте конфигурацию**
```bash
imgctl servers list
imgctl servers test dev
```

## Bash Completion

imgctl поддерживает полное автодополнение для всех команд, параметров и имен ресурсов.

### Установка completion

```bash
# Установить completion (по умолчанию в ~/.bashrc)
./imgctl-completion.bash install

# Установить в ~/.bashrc
./imgctl-completion.bash install --bashrc

# Установить в ~/.bash_profile
./imgctl-completion.bash install --profile

# Проверить установку
./imgctl-completion.bash test

# Удалить completion
./imgctl-completion.bash uninstall

# Показать справку
./imgctl-completion.bash help
```

### Возможности completion

- **Команды и подкоманды**: автодополнение всех команд
- **Параметры**: все опции командной строки
- **Имена ресурсов**: компоненты, стеки, ноды, серверы, репозитории, реестры
- **Колонки**: для команд `list` с `--columns`
- **Кэширование**: быстрая работа благодаря локальному кэшу
- **Работа в контексте сервера**: через `--server` или переменные окружения
- **Скрытие служебных компонентов**: компоненты, начинающиеся с `monitor-`

### Примеры использования

```bash
# Автодополнение команд
imgctl <TAB>
# → servers nodes stacks components registries repositories logs

# Автодополнение компонентов
imgctl components get <TAB>
# → web-api-staging database-production ...

# Автодополнение параметров
imgctl components list --<TAB>
# → --limit --no-cache --columns --filter --no-headers ...

# Автодополнение с сервером
imgctl --server dev components get <TAB>
# → database-production cache-production ...

# Автодополнение с переменными окружения
IMG_SERVER=dev imgctl components get <TAB>
# → database-production cache-production ...

# Автодополнение колонок
imgctl components list --custom-columns <TAB>
# → NAME NAMESPACE STACK IMAGE TAG STATUS ...
```

### Кэширование

Completion использует кэширование для быстрой работы:
- Кэш создается отдельно для каждого сервера
- Данные кэшируются в `~/.cache/imgctl/<server_name>/`
- Кэш автоматически обновляется при необходимости
- Поддерживает работу с переменными окружения `IMG_SERVER`, `IMG_USERNAME`, `IMG_PASSWORD`

### Управление completion

```bash
./imgctl-completion.bash test      # Тестирование
./imgctl-completion.bash install   # Установка
./imgctl-completion.bash uninstall # Удаление
./imgctl-completion.bash help      # Справка
```


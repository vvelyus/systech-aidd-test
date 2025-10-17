# 📊 Визуальное руководство по проекту

> Понимание проекта через визуализацию с разных точек зрения

---

## 🎯 О гайде

Этот гайд показывает проект через **различные типы диаграмм**, каждая из которых раскрывает определенный аспект системы. Используйте нужную диаграмму в зависимости от того, что хотите понять.

---

## 📐 Содержание

1. [Высокоуровневая архитектура](#1-высокоуровневая-архитектура)
2. [Компоненты и зависимости](#2-компоненты-и-зависимости)
3. [Поток обработки сообщения](#3-поток-обработки-сообщения)
4. [Структура классов](#4-структура-классов)
5. [Жизненный цикл запроса](#5-жизненный-цикл-запроса)
6. [Состояния контекста](#6-состояния-контекста)
7. [Модель данных](#7-модель-данных)
8. [Развертывание](#8-развертывание)
9. [История разработки](#9-история-разработки)
10. [Процесс разработки (TDD)](#10-процесс-разработки-tdd)

---

## 1. Высокоуровневая архитектура

**Что показывает:** Основные компоненты и их взаимодействие

```mermaid
graph TB
    subgraph External[External Services]
        User[User<br/>Telegram User]
        TG[Telegram API]
        OR[OpenRouter API]
    end

    subgraph Application[Application Layer]
        Main[main.py<br/>Entry Point]
        Bot[TelegramBot<br/>Commands & Messages]
        LLM[LLMClient<br/>LLM Integration]
        Storage[ContextStorage<br/>Dialog History]
        Config[Config<br/>Configuration]
        Messages[BotMessages<br/>Text Constants]
    end

    subgraph Infrastructure[Infrastructure]
        Logger[Logger<br/>Logging]
        Prompts[system_prompt.txt<br/>Bot Role]
    end

    User -->|messages| TG
    TG -->|polling| Bot
    Bot -->|responses| TG
    TG -->|responses| User

    Main --> Config
    Main --> Logger
    Main --> Bot
    Main --> LLM
    Main --> Storage

    Bot -->|uses| Messages
    Bot -.->|optional requests| LLM

    LLM -->|read/write| Storage
    LLM -->|API calls| OR

    Config -->|loads| Prompts

    Logger -.->|logs| Bot
    Logger -.->|logs| LLM
    Logger -.->|logs| Storage

    style User fill:#e1f5ff,stroke:#01579b,stroke-width:3px,color:#000
    style Bot fill:#fff3e0,stroke:#e65100,stroke-width:3px,color:#000
    style LLM fill:#f3e5f5,stroke:#4a148c,stroke-width:3px,color:#000
    style Storage fill:#e8f5e9,stroke:#1b5e20,stroke-width:3px,color:#000
    style Config fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#000
    style Messages fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#000
    style Logger fill:#f1f8e9,stroke:#558b2f,stroke-width:2px,color:#000
    style Prompts fill:#ede7f6,stroke:#4527a0,stroke-width:2px,color:#000
    style OR fill:#ffebee,stroke:#c62828,stroke-width:3px,color:#000
    style TG fill:#e0f2f1,stroke:#00695c,stroke-width:3px,color:#000
    style Main fill:#ffccbc,stroke:#d84315,stroke-width:3px,color:#000
```

**Ключевые наблюдения:**
- 🚀 **main.py** - оркестратор, создает все компоненты
- 🤖 **Bot** - единственная точка входа от Telegram
- 🧠 **LLM** - изолирован от Telegram (можно использовать отдельно)
- 💾 **Storage** - pluggable (Protocol-based)

---

## 2. Компоненты и зависимости

**Что показывает:** Иерархия модулей и направление зависимостей

```mermaid
graph LR
    subgraph Core[Core]
        Main[main.py]
    end

    subgraph Domain[Business Logic]
        Bot[bot.py]
        LLM[llm_client.py]
    end

    subgraph Storage[Storage]
        CS[context_storage.py]
        CSP[ContextStorage Protocol]
        IMS[InMemoryContextStorage]
    end

    subgraph Config[Configuration]
        Conf[config.py]
        Env[.env]
        Prompt[system_prompt.txt]
    end

    subgraph Utils[Utils]
        Msg[messages.py]
        Log[logger.py]
    end

    subgraph External[External]
        Aiogram[aiogram 3.x]
        OpenAI[openai]
        Dotenv[python-dotenv]
    end

    Main --> Bot
    Main --> LLM
    Main --> Conf
    Main --> Log
    Main --> IMS

    Bot --> Msg
    Bot -.->|optional| LLM
    Bot --> Aiogram

    LLM --> CSP
    LLM --> OpenAI

    IMS -.->|implements| CSP

    Conf --> Dotenv
    Conf --> Env
    Conf --> Prompt

    style Main fill:#ffccbc,stroke:#d84315,stroke-width:4px,color:#000
    style Bot fill:#fff3e0,stroke:#e65100,stroke-width:3px,color:#000
    style LLM fill:#f3e5f5,stroke:#4a148c,stroke-width:3px,color:#000
    style CSP fill:#c8e6c9,stroke:#2e7d32,stroke-width:3px,color:#000
    style IMS fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#000
    style Conf fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#000
    style Msg fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#000
    style Log fill:#f1f8e9,stroke:#558b2f,stroke-width:2px,color:#000
```

**Принцип зависимостей:**
- ⬇️ Зависимости направлены **вниз** (от абстракций к деталям)
- 🔄 Нет циклических зависимостей
- 📦 Storage использует Protocol (Dependency Inversion)

---

## 3. Поток обработки сообщения

**Что показывает:** Последовательность действий при получении сообщения

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant T as Telegram
    participant B as Bot
    participant M as Messages
    participant L as LLM
    participant S as Storage
    participant O as OpenRouter

    rect rgb(225, 245, 255)
        Note over U,T: User sends message
        U->>T: Text message
        T->>B: polling: new message
    end

    rect rgb(255, 243, 224)
        Note over B: Bot validates and processes
        B->>B: handle_message()
        B->>B: Check length
        alt Empty message
            B->>M: empty_message()
            M-->>B: Error text
            B->>T: Error response
            T->>U: Error
        else Too long (>4000)
            B->>M: message_too_long()
            M-->>B: Error text
            B->>T: Error response
            T->>U: Error
        end
        B->>T: send_chat_action(TYPING)
    end

    rect rgb(243, 229, 245)
        Note over L,S: LLM processes with context
        B->>L: get_response_with_context(user_id, text)
        L->>S: add_message(user_id, "user", text)
        S->>S: Add to history
        S->>S: Trim to 20 messages
        L->>S: get_context(user_id)
        S-->>L: [last 20 messages]
    end

    rect rgb(255, 235, 238)
        Note over L,O: Request to OpenRouter API
        L->>L: Build messages array
        L->>O: chat.completions.create()
        O-->>L: LLM response
    end

    rect rgb(243, 229, 245)
        Note over L,S: Save response
        L->>S: add_message(user_id, "assistant", response)
        S->>S: Add to history
        L-->>B: LLM response
    end

    rect rgb(225, 245, 255)
        Note over B,U: Send response to user
        B->>T: Response
        T->>U: Bot response
    end
```

**Временная сложность:** ~1-3 секунды на сообщение (зависит от OpenRouter)

---

## 4. Структура классов

**Что показывает:** Классы, их атрибуты и методы

```mermaid
classDiagram
    class Config {
        +str telegram_token
        +str openrouter_api_key
        +str bot_name
        +str openrouter_model
        +str system_prompt_file
        +int max_context_messages
        +from_env() Config
        +load_system_prompt() str
    }

    class TelegramBot {
        -Bot bot
        -Dispatcher dp
        -Logger logger
        -str system_prompt
        -LLMClient llm_client
        +cmd_start(Message)
        +cmd_help(Message)
        +cmd_role(Message)
        +cmd_reset(Message)
        +cmd_status(Message)
        +handle_message(Message)
        +start()
    }

    class LLMClient {
        -AsyncOpenAI client
        -str model
        -str system_prompt
        -Logger logger
        -ContextStorage context_storage
        +get_response(str) str
        +get_response_with_context(int, str) str
        +reset_context(int)
    }

    class ContextStorage {
        <<Protocol>>
        +add_message(int, str, str)
        +get_context(int) List
        +reset_context(int)
    }

    class InMemoryContextStorage {
        -Dict _storage
        -int _max_messages
        -int _max_users
        -Logger _logger
        +add_message(int, str, str)
        +get_context(int) List
        +reset_context(int)
        +get_user_count() int
        +clear_all()
    }

    class BotMessages {
        <<Static>>
        +welcome(str, str) str$
        +help_text() str$
        +role(str) str$
        +status() str$
        +context_reset_success() str$
        +empty_message() str$
        +message_too_long() str$
        +processing_error() str$
    }

    TelegramBot --> LLMClient : uses
    TelegramBot --> BotMessages : uses
    LLMClient --> ContextStorage : depends on
    InMemoryContextStorage ..|> ContextStorage : implements
    Config ..> BotMessages : creates prompt

    style Config fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#000
    style TelegramBot fill:#fff3e0,stroke:#e65100,stroke-width:3px,color:#000
    style LLMClient fill:#f3e5f5,stroke:#4a148c,stroke-width:3px,color:#000
    style ContextStorage fill:#c8e6c9,stroke:#2e7d32,stroke-width:3px,color:#000
    style InMemoryContextStorage fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#000
    style BotMessages fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#000
```

**Паттерны:**
- 🔷 **Protocol** - ContextStorage (Dependency Inversion)
- 🔶 **Static Methods** - BotMessages (stateless)
- 🔹 **Decorator** - @log_command (AOP pattern)
- 🔸 **Factory Method** - Config.from_env()

---

## 5. Жизненный цикл запроса

**Что показывает:** Состояния запроса от начала до конца

```mermaid
stateDiagram-v2
    [*] --> MessageReceived : Telegram polling

    MessageReceived --> Validating : handle_message()

    Validating --> ErrorEmpty : if len < 1
    Validating --> ErrorTooLong : if len > 4000
    Validating --> Processing : if valid

    ErrorEmpty --> SendError
    ErrorTooLong --> SendError
    SendError --> [*]

    Processing --> ShowTyping : valid message
    ShowTyping --> AddToContext : TYPING action

    AddToContext --> GetContext : add user message
    GetContext --> TrimContext : fetch history
    TrimContext --> BuildRequest : trim to 20 msgs

    BuildRequest --> CallAPI : system + context
    CallAPI --> APISuccess : response OK
    CallAPI --> APIError : API fail

    APIError --> LogError
    LogError --> SendError

    APISuccess --> SaveResponse : extract content
    SaveResponse --> SendResponse : add to context
    SendResponse --> [*] : answer to user

    note right of Validating
        Edge cases
        Empty or too long
    end note

    note right of TrimContext
        Max 20 messages
        per user
    end note

    note right of CallAPI
        OpenRouter API
    end note
```

**Точки отказа:**
- ❌ Валидация (пустое/длинное сообщение)
- ❌ API ошибка (сеть, лимиты, ключ)
- ✅ Все ошибки логируются и обрабатываются gracefully

---

## 6. Состояния контекста

**Что показывает:** Как изменяется контекст диалога

```mermaid
stateDiagram-v2
    [*] --> NoContext : New user

    NoContext --> HasContext : add_message()

    state HasContext {
        [*] --> Growing
        Growing --> Growing : add_message()<br/>(< 20 msgs)
        Growing --> Full : add_message()<br/>(= 20 msgs)
        Full --> Full : add_message()<br/>(trim oldest)
    }

    HasContext --> NoContext : reset_context()
    HasContext --> NoContext : Evicted (LRU) when > 1000 users

    note right of NoContext
        User not in storage
        or context cleared
    end note

    note left of Growing
        Less than 20 messages
        Add to the end
    end note

    note left of Full
        Exactly 20 messages
        Remove oldest, add new
    end note
```

**Стратегии:**
- 🔄 **FIFO** для одного пользователя (при > 20 сообщений)
- 🔄 **LRU** для всех пользователей (при > 1000 пользователей)

---

## 7. Модель данных

**Что показывает:** Структуры данных и их связи

```mermaid
erDiagram
    CONFIG ||--|| TELEGRAM_TOKEN : contains
    CONFIG ||--|| OPENROUTER_KEY : contains
    CONFIG ||--o{ DEFAULTS : has
    CONFIG ||--|| PROMPT_FILE : references

    TELEGRAM_BOT ||--|| CONFIG : uses
    TELEGRAM_BOT ||--o| LLM_CLIENT : uses
    TELEGRAM_BOT }o--|| LOGGER : uses

    LLM_CLIENT ||--|| CONTEXT_STORAGE : uses
    LLM_CLIENT ||--|| OPENROUTER : calls
    LLM_CLIENT }o--|| LOGGER : uses

    CONTEXT_STORAGE ||--|{ USER_CONTEXT : stores
    USER_CONTEXT ||--|{ MESSAGE : contains

    MESSAGE {
        string role
        string content
    }

    USER_CONTEXT {
        int user_id PK
        list messages
    }

    CONTEXT_STORAGE {
        dict storage
        int max_messages
        int max_users
    }

    CONFIG {
        string telegram_token
        string openrouter_api_key
        string bot_name
        string openrouter_model
        string system_prompt_file
        int max_context_messages
    }
```

**Ограничения:**
- 📊 **20 сообщений** на пользователя
- 👥 **1000 пользователей** максимум
- 📝 **4000 символов** максимум в сообщении

---

## 8. Развертывание

**Что показывает:** Текущая архитектура развертывания

```mermaid
graph TB
    subgraph Machine[Local Machine]
        subgraph Python[Python 3.11+ Environment]
            subgraph Process[Python Process]
                App[systech-aidd-test<br/>Single Instance]

                subgraph Memory[RAM]
                    Context[Context Storage<br/>max 1000 users<br/>max 20 msgs/user]
                end
            end

            Files[File System]
        end
    end

    subgraph External[External Services]
        Telegram[Telegram API<br/>api.telegram.org]
        OpenRouter[OpenRouter API<br/>openrouter.ai]
    end

    App -->|Polling<br/>getUpdates| Telegram
    Telegram -->|Messages| App

    App -->|HTTP POST<br/>chat.completions| OpenRouter
    OpenRouter -->|JSON Response| App

    App -->|Read| Files
    Files -.->|.env config| App
    Files -.->|system_prompt.txt| App
    App -->|Write| Files
    Files -.->|logs/bot.log| App

    Context -.->|stored in| Memory

    style App fill:#ffccbc,stroke:#d84315,stroke-width:3px,color:#000
    style Context fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#000
    style Files fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#000
    style Telegram fill:#e1f5ff,stroke:#01579b,stroke-width:3px,color:#000
    style OpenRouter fill:#ffebee,stroke:#c62828,stroke-width:3px,color:#000
    style Memory fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
```

**Характеристики:**
- 🖥️ Single instance (не распределенная)
- 💾 In-memory storage (не персистентная)
- 🔄 Polling mode (не webhook)
- 📦 Нет контейнеризации (запуск через make run)

**Готовность к масштабированию:**
- ✅ Protocol-based storage → легко заменить на Redis
- ✅ Stateless design → можно запустить N инстансов
- ⚠️ Polling → нужно изменить на webhook

---

## 9. История разработки

**Что показывает:** Эволюция проекта по итерациям

```mermaid
gantt
    title Development History
    dateFormat YYYY-MM-DD
    section MVP Iterations
    Iteration 1 Setup and Bot      :done, i1, 2025-10-10, 1d
    Iteration 2 LLM Integration       :done, i2, 2025-10-10, 1d
    Iteration 3 Dialog Context      :done, i3, 2025-10-10, 1d
    Iteration 4 Tests and Finalize  :done, i4, 2025-10-10, 1d
    Iteration 5 AI Product with Role   :done, i5, 2025-10-11, 1d

    section Tech Debt
    TD-1 Quality Infrastructure     :done, td1, 2025-10-11, 1d
    TD-2 Config Refactoring          :done, td2, 2025-10-11, 1d
    TD-3 Coverage Extension         :done, td3, 2025-10-11, 1d
    TD-4 Bot SRP Refactoring         :done, td4, 2025-10-11, 1d
    TD-5 Storage Abstraction          :done, td5, 2025-10-11, 1d

    section Documentation
    Guides Must Have Guides           :active, doc1, 2025-10-16, 1d
```

**Ключевые вехи:**
- 📅 **День 1 (10.10):** MVP функционал (итерации 1-4)
- 📅 **День 2 (11.10):** AI-продукт + устранение тех.долга (TD-1 → TD-5)
- 📅 **День 7 (16.10):** Документация и гайды

**Метрики прогресса:**
- Итерация 1 → 4: **0% → 72%** test coverage
- TD-3: **72% → 100%** test coverage
- TD-1 → TD-5: **0 → 49** тестов

---

## 10. Процесс разработки (TDD)

**Что показывает:** Workflow TDD цикла

```mermaid
graph TD
    Start([Start Task]) --> ReadTask[Read<br/>Task]
    ReadTask --> ThinkSolution[Think<br/>Solution]

    ThinkSolution --> RED[RED Phase]

    subgraph TDD_Cycle[TDD Cycle]
        RED[Write<br/>failing test] --> RunTestRed[make test]
        RunTestRed --> CheckRed{Test<br/>fails?}
        CheckRed -->|No| RED
        CheckRed -->|Yes| GREEN[GREEN Phase]

        GREEN[Minimal<br/>implementation] --> RunTestGreen[make test]
        RunTestGreen --> CheckGreen{Test<br/>passes?}
        CheckGreen -->|No| GREEN
        CheckGreen -->|Yes| REFACTOR[REFACTOR Phase]

        REFACTOR{Need<br/>refactoring?} -->|Yes| ImproveCode[Improve<br/>code]
        ImproveCode --> RunCI[make ci]
        RunCI --> CheckCI{CI<br/>passes?}
        CheckCI -->|No| ImproveCode
        CheckCI -->|Yes| NextTest{More<br/>tests?}

        REFACTOR -->|No| NextTest
        NextTest -->|Yes| RED
    end

    NextTest -->|No| FinalCI[Final check<br/>make ci]
    FinalCI --> Commit[Git commit<br/>with message]
    Commit --> Done([Done])

    style Start fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px,color:#000
    style RED fill:#ffebee,stroke:#c62828,stroke-width:3px,color:#000
    style GREEN fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px,color:#000
    style REFACTOR fill:#fff3e0,stroke:#e65100,stroke-width:3px,color:#000
    style FinalCI fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    style Commit fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style Done fill:#c8e6c9,stroke:#1b5e20,stroke-width:3px,color:#000
    style TDD_Cycle fill:#f9fbe7,stroke:#827717,stroke-width:2px
```

**Правила TDD:**
1. 🔴 **RED:** Тест ДОЛЖЕН упасть (проверяем правильность теста)
2. 🟢 **GREEN:** Минимальный код для прохождения (не больше!)
3. ♻️ **REFACTOR:** Улучшаем только если нужно (KISS!)

---

## 🎨 Легенда цветов

### Компоненты
- 🟠 **Оранжевый** - Точка входа (main.py, Bot)
- 🟣 **Фиолетовый** - Бизнес-логика (LLM)
- 🟢 **Зеленый** - Хранилище (Storage)
- 🟡 **Желтый** - Конфигурация
- 🔴 **Красный** - Внешние API
- 🔵 **Синий** - Telegram

### Состояния
- 🟢 **Зеленый** - Успех, валидный
- 🔴 **Красный** - Ошибка, провал
- 🟡 **Желтый** - В процессе
- 🟣 **Фиолетовый** - Проверка

---

## 📚 Навигация по диаграммам

### Хочу понять общую архитектуру
→ [1. Высокоуровневая архитектура](#1-высокоуровневая-архитектура)

### Хочу понять зависимости модулей
→ [2. Компоненты и зависимости](#2-компоненты-и-зависимости)

### Хочу понять как обрабатывается сообщение
→ [3. Поток обработки сообщения](#3-поток-обработки-сообщения)

### Хочу понять структуру классов
→ [4. Структура классов](#4-структура-классов)

### Хочу понять состояния запроса
→ [5. Жизненный цикл запроса](#5-жизненный-цикл-запроса)

### Хочу понять работу контекста
→ [6. Состояния контекста](#6-состояния-контекста)

### Хочу понять модель данных
→ [7. Модель данных](#7-модель-данных)

### Хочу понять развертывание
→ [8. Развертывание](#8-развертывание)

### Хочу понять историю проекта
→ [9. История разработки](#9-история-разработки)

### Хочу понять процесс разработки
→ [10. Процесс разработки (TDD)](#10-процесс-разработки-tdd)

---

## 🔗 Связанные гайды

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Текстовое описание архитектуры
- **[CODEBASE_TOUR.md](CODEBASE_TOUR.md)** - Тур по коду с примерами
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Процессы разработки
- **[TESTING.md](TESTING.md)** - Стратегия тестирования

---

**Используйте визуализацию для быстрого понимания системы! 📊**

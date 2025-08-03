# 🚀 Быстрый старт - Meeting Summary Bot

Пошаговая инструкция для запуска бота за 10 минут.

## 📝 Шаг 1: Подготовка

### 1.1 Создание Telegram бота
1. Откройте Telegram и найдите [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/newbot`
3. Введите название бота (например: "Meeting Summary Bot")
4. Введите username бота (например: "my_meeting_summary_bot")
5. **Сохраните токен** - он понадобится в .env файле

### 1.2 Получение OpenAI API ключа
1. Перейдите на [platform.openai.com](https://platform.openai.com/)
2. Войдите в аккаунт или зарегистрируйтесь
3. Перейдите в API Keys → Create new secret key
4. **Сохраните ключ** - он понадобится в .env файле

## ⚙️ Шаг 2: Настройка проекта

### 2.1 Установка зависимостей
```bash
# Установка Python зависимостей
pip install -r requirements.txt
```

### 2.2 Настройка окружения
```bash
# Копируем пример конфигурации
cp .env.example .env

# Редактируем .env файл (используйте любой текстовый редактор)
nano .env
```

### 2.3 Заполнение .env файла
Замените следующие значения в `.env`:
```env
# ОБЯЗАТЕЛЬНЫЕ параметры
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE

# Остальные параметры можно оставить по умолчанию
OPENAI_MODEL=gpt-4o-mini
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=100
FILE_RETENTION_HOURS=24
```

## 🏃‍♂️ Шаг 3: Запуск

### 3.1 Локальный запуск
```bash
python main.py
```

Вы должны увидеть сообщение:
```
Meeting Bot is running!
```

### 3.2 Тестирование бота
1. Найдите своего бота в Telegram по username
2. Отправьте команду `/start`
3. Загрузите .m4a файл записи встречи
4. Подождите саммари (1-3 минуты)

## 🐳 Альтернатива: Docker

Если предпочитаете Docker:

```bash
# Сборка образа
docker build -t meeting-bot .

# Запуск контейнера
docker run --env-file .env meeting-bot
```

## 🌐 Деплой на Railway (продакшн)

### 3.1 Подготовка Railway
1. Зарегистрируйтесь на [railway.app](https://railway.app)
2. Подключите GitHub аккаунт
3. Создайте новый проект из GitHub репозитория

### 3.2 Настройка переменных
В Railway панели добавьте переменные окружения:
- `TELEGRAM_BOT_TOKEN`
- `OPENAI_API_KEY` 
- `OPENAI_MODEL=gpt-4o-mini`
- `LOG_LEVEL=INFO`

### 3.3 Автоматический деплой
- Railway автоматически деплоит при пуше в main ветку
- GitHub Actions настроены для автоматического тестирования и деплоя

## 🔧 Тестовые команды

### Проверка функциональности
```bash
# Запуск тестов
pytest tests/

# Проверка стиля кода
flake8 .
black --check .
```

## ❗ Решение проблем

### Проблема: "Module not found"
```bash
# Переустановите зависимости
pip install --upgrade -r requirements.txt
```

### Проблема: "Invalid token"
- Проверьте правильность TELEGRAM_BOT_TOKEN в .env
- Убедитесь, что токен скопирован полностью

### Проблема: "OpenAI API error"
- Проверьте правильность OPENAI_API_KEY
- Убедитесь, что у вас есть кредиты на OpenAI аккаунте

### Проблема: "Permission denied"
```bash
# Создайте необходимые директории
mkdir -p logs temp_files
chmod 755 logs temp_files
```

## 📊 Мониторинг

После запуска проверьте:
- Логи в файле `logs/meeting_bot.log`
- Временные файлы в папке `temp_files/`
- Статус бота в Telegram

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи в `logs/meeting_bot.log`
2. Убедитесь, что все переменные в `.env` заполнены
3. Проверьте интернет соединение
4. Создайте Issue в GitHub репозитории

---

🎉 **Готово!** Ваш бот для саммари встреч готов к использованию!
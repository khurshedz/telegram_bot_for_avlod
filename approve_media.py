import os
import sys
import asyncio
import signal
from datetime import datetime
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from secret import *


# Конфигурация
CONFIG = {
    'BOT_TOKEN': TELEGRAM_TOKEN,
    'TARGET_CHAT_ID': CHAT_IDS,  # ID группы куда отправлять
    'MEDIA_FOLDER': '/home/spac/Pictures',  # Папка с медиафайлами
    'SUPPORTED_FORMATS': {'.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.avi', '.mkv'},
    'WHITELIST': WHITELIST,  # Список ID пользователей, которым разрешен доступ,
    'STATE_FILE': './bot_state.txt',  # Файл для хранения состояния
    'SENT_FILES_LOG': './sent_files.txt',  # Лог отправленных файлов
    'DELETE_ON_SKIP': False,  # Удалять файл при нажатии "Другой"
}


class MediaBot:
    def __init__(self):
        self.current_file_index = {}
        self.media_files = []
        self.application = None
        self.should_stop = False
        self.sent_files = set()  # Множество отправленных файлов
        self.processing_lock = {}  # Блокировка для предотвращения двойной обработки
        self.load_state()
        self.load_sent_files()

    def load_state(self):
        """Загружает состояние из файла"""
        state_file = Path(CONFIG['STATE_FILE'])
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if ':' in line:
                            user_id, idx = line.strip().split(':')
                            self.current_file_index[int(user_id)] = int(idx)
                            self.processing_lock[int(user_id)] = False
                print(f"📂 Загружено состояние: {self.current_file_index}")
            except Exception as e:
                print(f"⚠️ Ошибка загрузки состояния: {e}")
        else:
            print("📝 Файл состояния не найден, начинаем с чистого листа")

    def save_state(self):
        """Сохраняет состояние в файл"""
        try:
            with open(CONFIG['STATE_FILE'], 'w', encoding='utf-8') as f:
                for user_id, idx in self.current_file_index.items():
                    f.write(f"{user_id}:{idx}\n")
            print(f"💾 Состояние сохранено: {self.current_file_index}")
        except Exception as e:
            print(f"⚠️ Ошибка сохранения состояния: {e}")

    def load_sent_files(self):
        """Загружает список отправленных файлов"""
        sent_log = Path(CONFIG['SENT_FILES_LOG'])
        if sent_log.exists():
            try:
                with open(sent_log, 'r', encoding='utf-8') as f:
                    self.sent_files = set(line.strip() for line in f if line.strip())
                print(f"📋 Загружено {len(self.sent_files)} отправленных файлов")
            except Exception as e:
                print(f"⚠️ Ошибка загрузки лога отправок: {e}")

    def add_sent_file(self, file_path):
        """Добавляет файл в список отправленных"""
        file_name = str(file_path)
        if file_name not in self.sent_files:
            self.sent_files.add(file_name)
            try:
                with open(CONFIG['SENT_FILES_LOG'], 'a', encoding='utf-8') as f:
                    f.write(f"{file_name}\n")
                print(f"✅ Файл добавлен в лог отправок: {file_name}")
            except Exception as e:
                print(f"⚠️ Ошибка записи в лог: {e}")

    def is_file_sent(self, file_path):
        """Проверяет, был ли файл уже отправлен"""
        return str(file_path) in self.sent_files

    def scan_media_files(self):
        """Сканирует папку и собирает все медиафайлы, сортируя по дате создания"""
        media_folder = Path(CONFIG['MEDIA_FOLDER'])

        if not media_folder.exists():
            media_folder.mkdir(parents=True, exist_ok=True)
            print(f"📁 Создана папка: {media_folder}")
            return []

        files = []
        for file_path in media_folder.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in CONFIG['SUPPORTED_FORMATS']:
                # Проверяем, что файл существует (может быть удалён другим процессом)
                if file_path.exists():
                    try:
                        files.append({
                            'path': file_path,
                            'created': datetime.fromtimestamp(file_path.stat().st_ctime),
                            'size': file_path.stat().st_size,
                            'sent': self.is_file_sent(file_path)
                        })
                    except Exception as e:
                        print(f"⚠️ Ошибка обработки файла {file_path}: {e}")

        # Сортируем по дате создания
        files.sort(key=lambda x: x['created'])
        self.media_files = files
        print(f"📊 Найдено файлов: {len(files)}, из них отправлено: {sum(1 for f in files if f['sent'])}")
        return files

    def get_keyboard(self, is_sent=False):
        """Создает клавиатуру с кнопками"""
        if is_sent:
            # Если файл уже отправлен, показываем только кнопки перехода
            keyboard = [
                [InlineKeyboardButton("🔄 Другой", callback_data='next')],
                [InlineKeyboardButton("❌ Завершить", callback_data='cancel')]
            ]
        else:
            keyboard = [
                [
                    InlineKeyboardButton("✅ Отправить", callback_data='send'),
                    InlineKeyboardButton("🗑️ Пропустить", callback_data='next'),
                ],
                [InlineKeyboardButton("❌ Завершить", callback_data='cancel')]
            ]
        return InlineKeyboardMarkup(keyboard)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user_id = update.effective_user.id

        # Проверка белого списка
        if user_id not in CONFIG['WHITELIST']:
            await update.message.reply_text(
                "⛔ У вас нет доступа к этому боту.\n"
                f"Ваш ID: {user_id}\n"
                "Обратитесь к администратору для получения доступа."
            )
            return

        # Инициализация блокировки для пользователя
        if user_id not in self.processing_lock:
            self.processing_lock[user_id] = False

        # Сканируем файлы
        files = self.scan_media_files()

        if not files:
            await update.message.reply_text(
                f"❌ Не найдено медиафайлов в папке {CONFIG['MEDIA_FOLDER']}\n"
                f"Поддерживаемые форматы: {', '.join(CONFIG['SUPPORTED_FORMATS'])}"
            )
            return

        # Проверяем, есть ли уже сохраненное состояние
        if user_id in self.current_file_index:
            idx = self.current_file_index[user_id]
            if idx < len(self.media_files):
                await update.message.reply_text(
                    f"♻️ Продолжаем работу.\n"
                    f"Текущий файл: #{idx + 1} из {len(self.media_files)}\n"
                    f"Отправлено файлов: {sum(1 for f in self.media_files if f['sent'])}"
                )
                await self.send_current_file(update, context, user_id)
                return

        # Начинаем с первого файла
        self.current_file_index[user_id] = 0
        self.save_state()
        await update.message.reply_text(
            f"🚀 Начинаем обработку файлов.\n"
            f"Всего файлов: {len(files)}\n"
            f"Уже отправлено: {sum(1 for f in files if f['sent'])}"
        )
        await self.send_current_file(update, context, user_id)

    async def send_current_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """Отправляет текущий файл пользователю"""
        idx = self.current_file_index.get(user_id, 0)

        if idx >= len(self.media_files):
            message = (
                "✅ Все файлы просмотрены!\n\n"
                f"📊 Статистика:\n"
                f"• Всего обработано: {len(self.media_files)}\n"
                f"• Отправлено: {sum(1 for f in self.media_files if f['sent'])}\n"
                f"• Пропущено: {len(self.media_files) - sum(1 for f in self.media_files if f['sent'])}"
            )
            if update.callback_query:
                await update.callback_query.message.reply_text(message)
            else:
                await update.message.reply_text(message)
            return

        file_info = self.media_files[idx]
        file_path = file_info['path']

        # Проверяем, существует ли файл
        if not file_path.exists():
            await (update.callback_query.message if update.callback_query else update.message).reply_text(
                f"⚠️ Файл не найден (возможно удалён): {file_path.name}\n"
                "Переход к следующему..."
            )
            self.current_file_index[user_id] = idx + 1
            self.save_state()
            await self.send_current_file(update, context, user_id)
            return

        created = file_info['created'].strftime('%d.%m.%Y %H:%M:%S')
        size_mb = file_info['size'] / (1024 * 1024)
        is_sent = file_info['sent']

        status_emoji = "✅" if is_sent else "📝"
        status_text = "УЖЕ ОТПРАВЛЕН" if is_sent else "Новый"

        caption = (
            f"{status_emoji} Статус: {status_text}\n"
            f"📁 Файл: {file_path.name}\n"
            f"📅 Дата создания: {created}\n"
            f"📊 Размер: {size_mb:.2f} MB\n"
            f"🔢 Файл {idx + 1} из {len(self.media_files)}\n"
            f"📤 Отправлено всего: {sum(1 for f in self.media_files if f['sent'])}"
        )

        if is_sent:
            caption += "\n\n⚠️ Этот файл уже был отправлен ранее"

        try:
            # Определяем тип файла и отправляем
            ext = file_path.suffix.lower()
            with open(file_path, 'rb') as f:
                if ext in {'.jpg', '.jpeg', '.png', '.gif'}:
                    if update.callback_query:
                        await update.callback_query.message.reply_photo(
                            photo=f,
                            caption=caption,
                            reply_markup=self.get_keyboard(is_sent)
                        )
                    else:
                        await update.message.reply_photo(
                            photo=f,
                            caption=caption,
                            reply_markup=self.get_keyboard(is_sent)
                        )
                elif ext in {'.mp4', '.mov', '.avi', '.mkv'}:
                    if update.callback_query:
                        await update.callback_query.message.reply_video(
                            video=f,
                            caption=caption,
                            reply_markup=self.get_keyboard(is_sent)
                        )
                    else:
                        await update.message.reply_video(
                            video=f,
                            caption=caption,
                            reply_markup=self.get_keyboard(is_sent)
                        )
        except Exception as e:
            error_msg = f"❌ Ошибка при отправке файла: {str(e)}"
            if update.callback_query:
                await update.callback_query.message.reply_text(error_msg)
            else:
                await update.message.reply_text(error_msg)

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()

        user_id = update.effective_user.id

        # Проверка белого списка
        if user_id not in CONFIG['WHITELIST']:
            await query.message.reply_text("⛔ У вас нет доступа к этому боту.")
            return

        # Проверка блокировки (защита от двойного нажатия)
        if self.processing_lock.get(user_id, False):
            await query.answer("⏳ Предыдущая операция ещё выполняется...", show_alert=True)
            return

        action = query.data

        if action == 'send':
            # Блокируем повторные нажатия
            self.processing_lock[user_id] = True

            idx = self.current_file_index.get(user_id, 0)

            # Проверяем, не отправлен ли файл уже
            if idx < len(self.media_files):
                file_info = self.media_files[idx]

                if file_info['sent']:
                    await query.message.reply_text(
                        "⚠️ Этот файл уже был отправлен ранее!\n"
                        "Используйте кнопку 'Другой' для перехода к следующему файлу."
                    )
                    self.processing_lock[user_id] = False
                    return

                # Отправляем файл в целевую группу
                await self.send_to_target_group(update, context, user_id)

            self.processing_lock[user_id] = False

        elif action == 'next':
            # Блокируем повторные нажатия
            self.processing_lock[user_id] = True

            idx = self.current_file_index.get(user_id, 0)

            if idx < len(self.media_files):
                file_to_delete = self.media_files[idx]['path']

                # Проверяем, существует ли файл
                if file_to_delete.exists():
                    if CONFIG['DELETE_ON_SKIP']:
                        try:
                            file_to_delete.unlink()  # Удаляем файл
                            await query.message.reply_text(f"🗑️ Файл удалён: {file_to_delete.name}")
                        except Exception as e:
                            await query.message.reply_text(f"⚠️ Ошибка при удалении: {str(e)}")
                    else:
                        await query.message.reply_text(f"⏭️ Файл пропущен: {file_to_delete.name}")
                else:
                    await query.message.reply_text(f"ℹ️ Файл уже удалён: {file_to_delete.name}")

                # Пересканируем файлы после удаления
                self.scan_media_files()

            # Индекс остаётся тем же (файл удалён, список сдвинулся)
            self.save_state()
            await query.message.reply_text("🔄 Загружаю следующий файл...")
            await self.send_current_file(update, context, user_id)

            self.processing_lock[user_id] = False

        elif action == 'cancel':
            # Завершаем работу БЕЗ очистки состояния
            await query.message.reply_text(
                "👋 Работа приостановлена. Прогресс сохранён.\n"
                "При следующем запуске продолжим с текущего места.\n\n"
                "Бот завершает работу..."
            )
            self.save_state()  # Сохраняем состояние перед выходом
            self.should_stop = True
            # Останавливаем приложение
            if self.application:
                await self.application.stop()

    async def send_to_target_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """Отправляет текущий файл в целевую группу"""
        idx = self.current_file_index.get(user_id, 0)

        if idx >= len(self.media_files):
            await update.callback_query.message.reply_text("❌ Файл не найден")
            return

        file_info = self.media_files[idx]
        file_path = file_info['path']

        # Ещё раз проверяем, не отправлен ли файл
        if self.is_file_sent(file_path):
            await update.callback_query.message.reply_text(
                "⚠️ Этот файл уже был отправлен ранее!"
            )
            return

        # Проверяем существование файла
        if not file_path.exists():
            await update.callback_query.message.reply_text(
                f"❌ Файл не найден: {file_path.name}"
            )
            return

        try:
            ext = file_path.suffix.lower()
            with open(file_path, 'rb') as f:
                if ext in {'.jpg', '.jpeg', '.png', '.gif'}:
                    await context.bot.send_photo(
                        chat_id=CONFIG['TARGET_CHAT_ID'],
                        photo=f,
                        caption=f"📤 {file_path.name}"
                    )
                elif ext in {'.mp4', '.mov', '.avi', '.mkv'}:
                    await context.bot.send_video(
                        chat_id=CONFIG['TARGET_CHAT_ID'],
                        video=f,
                        caption=f"📤 {file_path.name}"
                    )

            # Добавляем файл в лог отправленных
            self.add_sent_file(file_path)

            # Обновляем статус в текущем списке
            self.media_files[idx]['sent'] = True

            await update.callback_query.message.reply_text(
                "✅ Файл успешно отправлен в целевую группу!\n"
                "Используйте кнопку 'Другой' для следующего файла."
            )

        except Exception as e:
            await update.callback_query.message.reply_text(
                f"❌ Ошибка при отправке в группу: {str(e)}\n"
                f"Проверьте правильность TARGET_CHAT_ID"
            )

    async def text_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений для автоматической отправки"""
        user_id = update.effective_user.id
        text = update.message.text.lower().strip()

        # Проверка белого списка
        if user_id not in CONFIG['WHITELIST']:
            await update.message.reply_text(
                "⛔ У вас нет доступа к этому боту.\n"
                f"Ваш ID: {user_id}"
            )
            return

        # Инициализация блокировки
        if user_id not in self.processing_lock:
            self.processing_lock[user_id] = False

        # Проверка блокировки
        if self.processing_lock.get(user_id, False):
            await update.message.reply_text("⏳ Предыдущая операция ещё выполняется...")
            return

        # Команды для отправки
        if text in ['отправить', 'send', 'отправь']:
            self.processing_lock[user_id] = True

            idx = self.current_file_index.get(user_id)

            if idx is None:
                # Если нет состояния, автоматически запускаем
                files = self.scan_media_files()
                if not files:
                    await update.message.reply_text("❌ Нет файлов для отправки")
                    self.processing_lock[user_id] = False
                    return
                self.current_file_index[user_id] = 0
                self.save_state()
                idx = 0

            # Проверяем, не отправлен ли файл
            if idx < len(self.media_files) and self.media_files[idx]['sent']:
                await update.message.reply_text(
                    "⚠️ Этот файл уже был отправлен ранее!\n"
                    "Используйте команду 'другой' для следующего файла."
                )
                self.processing_lock[user_id] = False
                return

            await update.message.reply_text("📤 Отправляю файл...")
            await self.send_to_target_group_direct(update, context, user_id)

            self.processing_lock[user_id] = False

        # Команды для следующего файла
        elif text in ['другой', 'next', 'далее', 'следующий', 'пропустить']:
            self.processing_lock[user_id] = True

            idx = self.current_file_index.get(user_id)

            if idx is None:
                # Автоматически начинаем
                files = self.scan_media_files()
                if not files:
                    await update.message.reply_text("❌ Нет файлов")
                    self.processing_lock[user_id] = False
                    return
                self.current_file_index[user_id] = 0
                self.save_state()
            else:
                # Удаляем текущий файл перед переходом к следующему
                if idx < len(self.media_files):
                    file_to_delete = self.media_files[idx]['path']

                    if file_to_delete.exists():
                        if CONFIG['DELETE_ON_SKIP']:
                            try:
                                file_to_delete.unlink()
                                await update.message.reply_text(f"🗑️ Файл удалён: {file_to_delete.name}")
                            except Exception as e:
                                await update.message.reply_text(f"⚠️ Ошибка при удалении: {str(e)}")
                        else:
                            await update.message.reply_text(f"⏭️ Файл пропущен: {file_to_delete.name}")
                    else:
                        await update.message.reply_text(f"ℹ️ Файл уже удалён: {file_to_delete.name}")

                    # Пересканируем файлы
                    self.scan_media_files()

                # Индекс остаётся тем же
                self.save_state()

            await update.message.reply_text("🔄 Загружаю следующий файл...")
            await self.send_current_file(update, context, user_id)

            self.processing_lock[user_id] = False

        # Команды для завершения
        elif text in ['отмена', 'cancel', 'стоп', 'stop', 'завершить']:
            await update.message.reply_text(
                "👋 Работа приостановлена. Прогресс сохранён.\n"
                "При следующем запуске продолжим с текущего места.\n\n"
                "Бот завершает работу..."
            )
            self.save_state()
            self.should_stop = True
            # Останавливаем приложение
            if self.application:
                await self.application.stop()
        else:
            await update.message.reply_text(
                "ℹ️ Доступные команды:\n"
                "• 'отправить' - отправить файл в группу\n"
                "• 'другой' / 'пропустить' - удалить и перейти к следующему\n"
                "• 'завершить' - сохранить прогресс и выйти\n\n"
                "Или используйте /start для начала работы"
            )

    async def send_to_target_group_direct(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """Отправляет текущий файл в целевую группу (для прямых команд)"""
        idx = self.current_file_index.get(user_id, 0)

        if idx >= len(self.media_files):
            await update.message.reply_text("❌ Файл не найден")
            return

        file_info = self.media_files[idx]
        file_path = file_info['path']

        # Проверяем, не отправлен ли файл
        if self.is_file_sent(file_path):
            await update.message.reply_text(
                "⚠️ Этот файл уже был отправлен ранее!"
            )
            return

        # Проверяем существование
        if not file_path.exists():
            await update.message.reply_text(
                f"❌ Файл не найден: {file_path.name}"
            )
            return

        try:
            ext = file_path.suffix.lower()
            with open(file_path, 'rb') as f:
                if ext in {'.jpg', '.jpeg', '.png', '.gif'}:
                    await context.bot.send_photo(
                        chat_id=CONFIG['TARGET_CHAT_ID'],
                        photo=f,
                        caption=f"📤 {file_path.name}"
                    )
                elif ext in {'.mp4', '.mov', '.avi', '.mkv'}:
                    await context.bot.send_video(
                        chat_id=CONFIG['TARGET_CHAT_ID'],
                        video=f,
                        caption=f"📤 {file_path.name}"
                    )

            # Добавляем в лог отправленных
            self.add_sent_file(file_path)

            # Обновляем статус
            self.media_files[idx]['sent'] = True

            await update.message.reply_text(
                "✅ Файл успешно отправлен в целевую группу!\n"
                "Напишите 'другой' для следующего файла."
            )

        except Exception as e:
            await update.message.reply_text(
                f"❌ Ошибка при отправке в группу: {str(e)}\n"
                f"Проверьте правильность TARGET_CHAT_ID"
            )


def signal_handler(signum, frame):
    """Обработчик сигналов для корректного завершения"""
    print("\n⚠️ Получен сигнал завершения. Сохранение состояния...")
    sys.exit(0)


def main():
    """Главная функция запуска бота"""
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    bot = MediaBot()

    # Создаем приложение
    application = Application.builder().token(CONFIG['BOT_TOKEN']).build()
    bot.application = application

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CallbackQueryHandler(bot.button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.text_handler))

    print("=" * 50)
    print("🤖 Бот запущен")
    print("=" * 50)
    print(f"📁 Папка с медиа: {CONFIG['MEDIA_FOLDER']}")
    print(f"🎯 Целевая группа: {CONFIG['TARGET_CHAT_ID']}")
    print(f"👥 Белый список: {CONFIG['WHITELIST']}")
    print(f"🗑️ Удаление при пропуске: {CONFIG['DELETE_ON_SKIP']}")
    print(f"💾 Файл состояния: {CONFIG['STATE_FILE']}")
    print(f"📋 Лог отправок: {CONFIG['SENT_FILES_LOG']}")
    print("=" * 50)

    try:
        # Запускаем бота
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        print("\n⚠️ Получен сигнал остановки (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    finally:
        # Сохраняем состояние перед выходом
        if not bot.should_stop:
            bot.save_state()
        print("💾 Состояние сохранено")
        print("👋 Бот остановлен")
        sys.exit(0)


if __name__ == '__main__':
    main()
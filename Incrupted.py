import os
import re
import telebot

# Ваш токен
API_TOKEN = '8060632074:AAGiUoZn6vkKl-_qON8rBofw8F2CjQEsQOI'
bot = telebot.TeleBot(API_TOKEN)

# Путь к папке с базами данных
DATABASE_FOLDER = '/storage/emulated/0/А_MyFullSourceGlaz/MyTestBD'

# Состояния для управления режимами поиска
SEARCH_MODE = 'search_mode'

# Хранение состояний пользователей
user_states = {}

# Хранение номеров из всех баз данных
all_numbers = set()

# Список кодировок для попытки чтения файла
ENCODINGS = ['utf-8', 'windows-1251', 'ISO-8859-1', 'utf-16']

def read_file_with_encodings(file_path):
    """Пробует прочитать файл с использованием нескольких кодировок и возвращает номера в виде множества."""
    numbers = set()
    for encoding in ENCODINGS:
        try:
            with open(file_path, 'r', encoding=encoding, errors='ignore') as file:
                for line in file:
                    cleaned_line = clean_phone_number(line.strip())
                    numbers.add(cleaned_line)  # Добавляем очищенный номер в множество
            break  # Выходим из цикла, если файл успешно прочитан
        except Exception:
            continue  # Переходим к следующей кодировке, если чтение не удалось
    return numbers

def clean_phone_number(phone_number):
    """Удаляет все символы, кроме цифр и знака '+' из номера телефона."""
    return re.sub(r'[^0-9+]', '', phone_number)  # Оставляем только цифры и знак '+'

def load_numbers_from_folder(folder_path):
    """Загружает номера из всех файлов в указанной папке."""
    global all_numbers  # Используем глобальную переменную all_numbers
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):  # Обрабатываем только файлы
            numbers = read_file_with_encodings(file_path)
            if numbers is not None:
                all_numbers.update(numbers)  # Добавляем номера из файла в общее множество

# Загружаем номера из всех баз данных в память
load_numbers_from_folder(DATABASE_FOLDER)
print(f"Загружено номеров: {len(all_numbers)}")  # Выводим количество загруженных номеров

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, '👋 Привет! Я бот для поиска номеров телефонов. Используйте команду /search для поиска по номеру телефона.')

@bot.message_handler(commands=['search'])
def search(message):
    user_states[message.chat.id] = SEARCH_MODE
    bot.reply_to(message, '🔍 Введите номер телефона для поиска.')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_state = user_states.get(message.chat.id)

    # Проверка состояния пользователя
    if user_state == SEARCH_MODE:
        find_phone(message)
    else:
        bot.reply_to(message, '⚠️ Пожалуйста, используйте /search для начала поиска.')

def find_phone(message):
    phone_number = message.text.strip()
    cleaned_number = clean_phone_number(phone_number)  # Очищаем введенный номер

    bot.reply_to(message, '⏳ Идет поиск... Пожалуйста, подождите.')  # Сообщение о начале поиска

    if cleaned_number in all_numbers:
        bot.reply_to(message, '✅ Номер найден в базе данных.')
    else:
        bot.reply_to(message, '❌ Ничего не найдено.')

    # Сбрасываем состояние после завершения поиска
    user_states[message.chat.id] = None

if __name__ == '__main__':
    bot.polling(none_stop=True)

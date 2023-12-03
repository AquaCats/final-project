import random
import json
from aiogram import Bot, Dispatcher, types
from aiogram import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = '6975984623:AAGPuUMlMBg2S7eWafvgyqGcJen2aZTr_ZM'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Dictionary to store game state for each user
user_states = {}

def choose_word():
    with open('word.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    words_list = data['words']
    random_word = random.choice(words_list)
    return random_word

def display_word(word, guessed_letters):
    display = ""
    for letter in word:
        if letter in guessed_letters:
            display += letter
        else:
            display += "_"
    return display

def create_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button = [KeyboardButton('/play')]
    keyboard.add(*button)
    return keyboard

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.reply("Вітаємо у грі 'Вішалка'! Введіть /play, щоб розпочати гру.", reply_markup=create_keyboard())

@dp.message_handler(commands=['play'])
async def cmd_play(message: types.Message):
    user_id = message.from_user.id
    secret_word = choose_word().lower()
    guessed_letters = []
    attempts = 6

    user_states[user_id] = {'secret_word': secret_word, 'guessed_letters': guessed_letters, 'attempts': attempts}

    await message.reply(f"Спробуйте вгадати слово: {display_word(secret_word, guessed_letters)}", reply_markup=create_keyboard())

@dp.message_handler()
async def handle_letter_input(message: types.Message):
    user_id = message.from_user.id
    letter_input = message.text.lower()

    user_state = user_states.get(user_id, {})
    secret_word = user_state.get('secret_word')
    guessed_letters = user_state.get('guessed_letters', [])
    attempts = user_state.get('attempts', 6)

    if len(message.text) == 1:

        if letter_input in guessed_letters:
            await message.reply("Ви вже вводили цю літеру. Спробуйте іншу.", reply_markup=create_keyboard())
        else:
            guessed_letters.append(letter_input)

            if letter_input not in secret_word:
                attempts -= 1
                await message.reply(f"Неправильно! Цієї літери немає у слові. Залишилося спроб: {attempts}", reply_markup=create_keyboard())

                if attempts == 0:
                    await message.reply(f"Гра закінчена. Ви не вгадали слово. Загадане слово було: {secret_word}", reply_markup=create_keyboard())
                    del user_states[user_id]
                else:
                    user_states[user_id]['attempts'] = attempts
            else:
                display = display_word(secret_word, guessed_letters)
                await message.reply(f"Вірно! {display}", reply_markup=create_keyboard())

                if "_" not in display:
                    await message.reply(f"Ви виграли! Загадане слово: {secret_word}", reply_markup=create_keyboard())
                    del user_states[user_id]
    else:
        if letter_input == secret_word:
            await message.reply(f"Вірно! Загадане слово: {secret_word}", reply_markup=create_keyboard())
            del user_states[user_id]
        if letter_input != secret_word:
            attempts -= 1
            await message.reply(f"Неправильно! Це не те слово. Залишилося спроб: {attempts}", reply_markup=create_keyboard())
        if attempts == 0:
            await message.reply(f"Гра закінчена. Ви не вгадали слово. Загадане слово було: {secret_word}", reply_markup=create_keyboard())
            del user_states[user_id]
        else:
            user_states[user_id]['attempts'] = attempts


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
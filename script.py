from aiogram import Bot, Dispatcher, executor
from config import botToken
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()
bot = Bot(botToken, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)

if __name__ == '__main__':
    from handlers import dp, send_to_admin, send_picture, echo_message

    # register handlers
    dp.register_message_handler(send_picture, lambda msg: msg, text='q')
    dp.register_message_handler(echo_message, lambda msg: msg)

    executor.start_polling(dp, on_startup=send_to_admin)

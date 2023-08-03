import textwrap
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
from aiogram import types
from aiogram.types import InputFile
from aiogram.utils.markdown import text, bold
from pilmoji import Pilmoji

from config import admin_id, botToken
from filter import IsGroup
from script import bot, dp


async def send_to_admin(*args):
    await bot.send_message(chat_id=admin_id, text="здарова")


@dp.message_handler(IsGroup(), content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_member(message: types.Message):
    members = ", ".join([m.get_mention(as_html=True) for m in message.new_chat_members])
    await message.reply(f"Hello, {members}.")


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    msg = text(bold("Інтуїтивно не зрозуміло?))"))
    await message.reply(msg)


async def send_picture(message: types.Message):
    if message.reply_to_message:
        profile_pictures = await bot.get_user_profile_photos(message.reply_to_message.from_user.id)
        if len(profile_pictures.photos[0]) > 0:
            file = await bot.get_file(profile_pictures.photos[0][0].file_id)
            byte_file = get_profile_picture(file.file_path)
            create_quote_photo(byte_file, "©" + message.reply_to_message.from_user.username,
                               message.reply_to_message.text,
                               str(message.reply_to_message.date).split()[0])
            photo = InputFile("assets/image.jpg")
            await bot.send_photo(chat_id=message.chat.id, photo=photo)
    else:
        await message.reply('Я сам маю придумати цитату?')


def create_quote_photo(file, username, quote, date):
    response = requests.get('https://random.imagecdn.app/500/300')

    # open images
    profile_picture = Image.open(file)
    base_image = Image.open(BytesIO(response.content)).filter(ImageFilter.GaussianBlur(5))

    # reduce brightness
    enhancer = ImageEnhance.Brightness(base_image)
    base_image = enhancer.enhance(0.6)

    # draw profile picture mask
    mask_size = profile_picture.size
    circle_shape = [(40, 40), (150 - 10, 150 - 10)]

    mask_image = Image.new('L', mask_size, 0)
    mask_draw = ImageDraw.Draw(mask_image)
    mask_draw.ellipse(circle_shape, fill=255)

    base_image.paste(profile_picture, (0, 0), mask_image)

    # draw text elements
    base_image_text_emoji = Pilmoji(base_image)

    font_request = requests.get("https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Black.ttf?raw=true",
                                allow_redirects=True)
    font = ImageFont.truetype(BytesIO(font_request.content), size=20)

    base_image_text_emoji.text((30, 150), username, fill="white", font=font)  # username
    base_image_text_emoji.text((40, 180), str(date), fill="white", font=font)  # date

    # draw quote
    quote_lines = textwrap.wrap(quote, width=30)
    offset = 50

    for line in quote_lines:
        base_image_text_emoji.text((180, offset), line, font=font, fill="white")
        offset += 25

    base_image.save('assets/image.jpg', quality=100)
    return base_image


def get_profile_picture(file_path):
    response = requests.get('https://api.telegram.org/file/bot' + botToken + '/' + file_path)
    byte_file = BytesIO(response.content)

    return byte_file

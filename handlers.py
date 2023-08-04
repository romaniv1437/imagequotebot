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
    print(message)
    if message.reply_to_message:

        username = "©" + message.reply_to_message.from_user.username
        quote = message.reply_to_message.text
        date = str(message.reply_to_message.date).split()[0]

        profile_pictures = await bot.get_user_profile_photos(message.reply_to_message.from_user.id)

        if profile_pictures.photos and len(profile_pictures.photos[0]) > 0:
            profile_picture_file = await bot.get_file(profile_pictures.photos[0][0].file_id)
            profile_picture_byte = get_telegram_image_file(profile_picture_file.file_path)
            if message.reply_to_message.photo:
                reply_image_file = await bot.get_file(message.reply_to_message.photo[1].file_id)
                reply_image_byte = get_telegram_image_file(reply_image_file.file_path)
                create_quote_image_photo(profile_picture_byte, username, reply_image_byte, date)
            else:
                create_quote_photo(profile_picture_byte, username, quote, date)

        photo = InputFile("assets/image.jpg")
        await bot.send_photo(chat_id=message.chat.id, photo=photo)
    else:
        await message.reply('Я сам маю придумати цитату?')


def create_quote_photo(profile_pic, username, quote, date):
    response = requests.get('https://random.imagecdn.app/500/300')

    # open images
    profile_picture = Image.open(profile_pic)
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


def create_quote_image_photo(profile_pic, username, image, date):
    response = requests.get('https://random.imagecdn.app/500/300')

    # open images
    profile_picture = Image.open(profile_pic)
    base_image = Image.open(BytesIO(response.content)).filter(ImageFilter.GaussianBlur(5))
    quote_image = Image.open(image)
    quote_image_with_padding = crop_image(quote_image, (280, 200), (5, 5, 5, 5))

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

    # paste replied image

    base_image.paste(quote_image_with_padding, (180, 50))

    # draw text elements
    base_image_text_emoji = ImageDraw.Draw(base_image)

    font_request = requests.get("https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Black.ttf?raw=true",
                                allow_redirects=True)
    font = ImageFont.truetype(BytesIO(font_request.content), size=20)

    base_image_text_emoji.text((30, 150), username, fill="white", font=font)  # username
    base_image_text_emoji.text((40, 180), str(date), fill="white", font=font)  # date

    base_image.save('assets/image.jpg', quality=100)
    return base_image


def get_telegram_image_file(file_path):
    response = requests.get('https://api.telegram.org/file/bot' + botToken + '/' + file_path)
    byte_file = BytesIO(response.content)

    return byte_file


def crop_image(image, new_size, border_widths):

    pl_img = image
    sXr, sYr = new_size
    lWx, rWx, tWy, bWy = border_widths

    sX, sY = pl_img.size
    sXi, sYi = sXr - (lWx + rWx), sYr - (tWy + bWy)

    pl_lft_top = pl_img.crop((0, 0, lWx, tWy))
    pl_rgt_top = pl_img.crop((sX - rWx, 0, sX, tWy))
    pl_lft_btm = pl_img.crop((0, sY - bWy, lWx, sY))
    pl_rgt_btm = pl_img.crop((sX - rWx, sY - bWy, sX, sY))

    pl_lft_lft = pl_img.crop((0, tWy, lWx, sY - bWy)).resize((lWx, sYi))
    pl_rgt_rgt = pl_img.crop((sX - rWx, tWy, sX, sY - bWy)).resize((rWx, sYi))
    pl_top_top = pl_img.crop((lWx, 0, sX - rWx, tWy)).resize((sXi, tWy))
    pl_btm_btm = pl_img.crop((lWx, sY - bWy, sX - rWx, sY)).resize((sXi, bWy))

    pl_mid_mid = pl_img.crop((lWx, tWy, sX - rWx, sY - bWy)).resize((sXi, sYi))

    pl_new = Image.new(pl_img.mode, (sXr, sYr))

    pl_new.paste(pl_mid_mid, (lWx, tWy))

    pl_new.paste(pl_top_top, (lWx, 0))
    pl_new.paste(pl_btm_btm, (lWx, sYr - bWy))
    pl_new.paste(pl_lft_lft, (0, tWy))
    pl_new.paste(pl_rgt_rgt, (sXr - rWx, tWy))

    pl_new.paste(pl_lft_top, (0, 0))
    pl_new.paste(pl_rgt_top, (sXr - rWx, 0))
    pl_new.paste(pl_lft_btm, (0, sYr - bWy))
    pl_new.paste(pl_rgt_btm, (sXr - rWx, sYr - bWy))
    return pl_new

from telegram.ext.updater import Updater
from telegram.update import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext import CallbackQueryHandler
import logging
import re
import json
import ast

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

updater = Updater("5927932816:AAHX9Rkz7RfGisGBEH8v419ZrwflbitxK-8", use_context=True)


def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    update.message.reply_text(f"""👋 Hey there, {user.first_name}!
This bot will automatically extract link(s) from any message.
The bot will treat website's header as title and web preview image as a generated snapshot of website.
You can also add a custom title and web preview image.
/rules - Check to avoid being rejected
/help - Know the mechanism of the bot
/about - Know about the developer
/donate - Support the developer
""")


def has_link_shortener(url):
    link_shorteners = ['bit.ly', 'tinyurl.com', 'ow.ly', 'tiny.cc', 'is.gd', 'shorte.st', 'adf.ly', 'adcrun.ch',
                       'shrinkme.io', 'cutt.ly', ]
    # Check if any of the link shorteners are in the URL
    for shortener in link_shorteners:
        if shortener in url:
            return True
    return False


# Button for send the link to channel prompt
send_button = InlineKeyboardButton(text="Send ✅", callback_data="yes")
keyboard1 = [[send_button]]
reply_markup_send = InlineKeyboardMarkup(keyboard1)

# Buttons to select the link to confirm
keyboard = [[InlineKeyboardButton("Option 1", callback_data="1"), InlineKeyboardButton("Option 2", callback_data="2")],
            [InlineKeyboardButton("Option 3", callback_data="3")]]
reply_markup_select = InlineKeyboardMarkup(keyboard)

links = []


def button_handler(update, context):
    query = update.callback_query
    query.answer()

    if query.data == 'yes':
        context.bot.send_message(chat_id='@duhlinkdump', text=links)
        query.edit_message_text(text='Message sent to channel')


def help(update: Update, context: CallbackContext):
    update.message.reply_text("Your Message")


def extract_url(a, update: Update, context: CallbackContext):
    # s = ast.literal_eval(json.dumps(str(a), indent=2))
    # for i in s.split(","):
    #     update.message.reply_text(i)
    if a.caption:
        raw = a.caption_html_urled
    else:
        raw = a.text_html_urled
    if "href" in raw:
        if raw.count("href") >= 2:
            m1 = context.bot.send_message(chat_id=a.chat_id, text="🔄 Processing...", reply_to_message_id=a.message_id)
            context.bot.edit_message_text(chat_id=m1.chat_id, message_id=m1.message_id, text="🔎 Found multiple links")
            link_pattern = r'href="([^"]*)"'
            found_link = re.findall(link_pattern, raw)
            found_link = list(set(found_link))
            link_pattern2 = r"(?:[?&](?:utm_(?:source|medium|campaign|term|content)|referral|cid|start|cn|z|igshid)|=.*|#.*)"
            clean_links = []
            for i in found_link:
                clean_links.append(re.sub(link_pattern2, "/=/ 3 ", i).split('/=/ 3 ')[0].lower())
            numbered_links = '\n'.join(['<b>' + str(i + 1) + '.</b> ' + item for i, item in enumerate(clean_links)])
            context.bot.edit_message_text(chat_id=m1.chat_id, message_id=m1.message_id,
                                          text=f"🔗 <b>Links Found:</b>\n\n{numbered_links}",
                                          disable_web_page_preview=True,
                                          parse_mode="HTML", reply_markup=reply_markup_select)
            return clean_links
        else:
            m1 = update.message.reply_text("🔄 Processing...", reply_to_message_id=a.message_id)
            link_pattern = r'href="([^"]*)"'
            found_link = re.findall(link_pattern, raw)
            link_pattern2 = r"(?:[?&](?:utm_(?:source|medium|campaign|term|content)|referral|cid|start|cn|z|igshid|m)|=.*|#.*)"
            clean_link = re.sub(link_pattern2, "", found_link[0]).lower()
            context.bot.edit_message_text(chat_id=m1.chat_id, message_id=m1.message_id,
                                          text=f"🔗 <b>Link Found:</b>\n\n{clean_link}",
                                          disable_web_page_preview=True,
                                          parse_mode="HTML", reply_markup=reply_markup_send)
            return clean_link
    else:
        update.message.reply_text("❎<b> No Link(s) Found</b>", parse_mode="HTML", reply_to_message_id=a.message_id)


def extract(update: Update, context: CallbackContext):
    global links
    links = extract_url(update.message, update, context)


def unknown_text(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry I can't recognize you , you said '%s'" % update.message.text)


updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(MessageHandler(None, extract))
updater.dispatcher.add_handler(CallbackQueryHandler(button_handler))

updater.start_polling()

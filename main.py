from telegram.ext.updater import Updater
from telegram.update import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext import CallbackQueryHandler
from telegram.ext.filters import Filters
import logging
import re
import os

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

updater = Updater(os.environ['api'], use_context=True)


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

# Button for send the link to channel prompt
send_button = InlineKeyboardButton(text="Send ✅", callback_data="yes")
keyboard1 = [[send_button]]
reply_markup_send = InlineKeyboardMarkup(keyboard1)

# Buttons to select the link to confirm
keyboard = [[InlineKeyboardButton("Option 1", callback_data="1"), InlineKeyboardButton("Option 2", callback_data="2")],[InlineKeyboardButton("Option 3", callback_data="3")]]
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


def extract_url(a:str, update: Update, context: CallbackContext):
    if a.caption:
        raw = a.caption_html_urled
    else:
        raw = a.text_html_urled
    if "href" in raw:
        if raw.count("href") >= 2:
            m1 = update.message.reply_text("🔄 Processing...")
            m2 = update.message.reply_text("⛓ Multiple Links Found")
            link_pattern = r'href="([^"]*)"'
            found_link = re.findall(link_pattern, raw)
            found_link = list(set(found_link))
            link_pattern2 = r"(?:[?&](?:utm_(?:source|medium|campaign|term|content)|referral|cid|start|cn|z|igshid)|=.*|#.*)"
            clean_links = []
            for i in found_link:
                clean_links.append(re.sub(link_pattern2, "/=/ 3 ", i).split('/=/ 3 ')[0])
            numbered_links = '\n'.join(['<b>' + str(i+1) + '.</b> ' + item for i, item in enumerate(clean_links)])
            context.bot.delete_message(chat_id=m1.chat_id, message_id=m1.message_id)
            context.bot.delete_message(chat_id=m2.chat_id, message_id=m2.message_id)
            update.message.reply_text(f"🔗 <b>Links Found:</b>\n\n{numbered_links}", disable_web_page_preview = True, parse_mode="HTML", reply_markup=reply_markup_select)
            return clean_links
        else:
            m1 = update.message.reply_text("🔄 Processing...")
            link_pattern = r'href="([^"]*)"'
            found_link = re.findall(link_pattern, raw)
            link_pattern2 = r"(?:[?&](?:utm_(?:source|medium|campaign|term|content)|referral|cid|start|cn|z|igshid|m)|=.*|#.*)"
            clean_link = re.sub(link_pattern2, "", found_link[0])
            context.bot.delete_message(chat_id=m1.chat_id, message_id=m1.message_id)
            update.message.reply_text(f"🔗 <b>Link Found:</b>\n\n{clean_link}", disable_web_page_preview = True, parse_mode="HTML", reply_markup=reply_markup_send)
            return clean_link
    else:
        update.message.reply_text("❎<b> No Link(s) Found</b>", parse_mode="HTML")


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

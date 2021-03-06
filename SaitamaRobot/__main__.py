import importlib
import time
import re
from sys import argv
from typing import Optional
from SaitamaRobot import (ALLOW_EXCL, CERT_PATH, DONATION_LINK, LOGGER, ARROW_IMG,
                          OWNER_ID, PORT, SUPPORT_CHAT, TOKEN, URL, WEBHOOK, pbot,
                          SUPPORT_CHAT, dispatcher, StartTime, telethn, updater)
# needed to dynamically load modules
# NOTE: Module order is not guaranteed, specify that in the config file!
from SaitamaRobot.modules import ALL_MODULES
from SaitamaRobot.modules.helper_funcs.chat_status import is_user_admin
from SaitamaRobot.modules.helper_funcs.misc import paginate_modules
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ParseMode,
                      Update)
from telegram.error import (BadRequest, ChatMigrated, NetworkError,
                            TelegramError, TimedOut, Unauthorized)
from telegram.ext import (CallbackContext, CallbackQueryHandler, CommandHandler,
                          Filters, MessageHandler)
from telegram.ext.dispatcher import DispatcherHandlerStop, run_async
from telegram.utils.helpers import escape_markdown


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


PM_START_TEXT = """
අඩේ! {}, මගේ නම ඇවිල්ලා {}↗️!  

මම group manage කරන්න පුළුවන් poweful🦾 බොට් කෙනෙක්🙂. 

මගේ owner කාරයා ඇවිල්ලා \n[Đ€Ş卄ΔĐ€€Ť卄 Ť卄ĪŞΔŘคŇΔ](t.me/DeshadeethThisarana) \nකියල චරිතයක්😝.

මගේ ownerට මාව නිර්මාණය \nකරන්න full support \nඑක දීලා තියෙන්නෙ \n[★彡ᵖⓡ𝓪Ｂ卄𝒶𝐒𝒽ค彡★](t.me/Prabha_sha) කියල පොරක්😇

ඔබට මගේ උපකාරයෙන් ලබා ගත හැකි විධාන ලැයිස්තුව සොයාගන්න /help කියල message එකක් එවන්න🤪

ඔබට මගේ ඉංග්‍රීසි පරිවර්තන බොට් ද භාවිතා කළ හැකිය \n[👉Arrow👈](t.me/MrArrow2bot)

©2021 [🛡Ģ₳ŇĞ🛡 ØF FŔĮĘŃĐŞ📝](t.me/gangoffriends) \n©2021 [Đ€Ş卄ΔĐ€€Ť卄 Ť卄ĪŞΔŘคŇΔ](t.me/DeshadeethThisarana) \n⚠️All Rights Reserved⚠️
"""

HELP_STRINGS = """
හායි, මගේ නම ඇවිල්ලා *{}*[🤖](ARROW_IMG).

මම ගොඩක් powerful සහ මම adminsලට ඔවුන්ගේ group manage කිරීමට උදව් කරමි😁
මට ඔබට උදව් කළ හැකි දේවල් පිළිබඳ අදහසක් ලබා ගන්න පහත සඳහන් දෑ බලන්න👇 

*ප්‍රධාන* විධාන:
 
 • /help: මෙම මැසේජ් එක private message \nඑකකින් යොමු කරයි.
 
 • /help <module name>: අදාල module එක පිළිබඳ තොරතුරු \nprivate message එකකින් ලබා දෙයි
 
 • /donate: අයිතිකරු වෙත පරිත්‍යාග කරන්නේ කෙසේද යන්න \nපිළිබඳ තොරතුරු!                     
 
 • /settings:
   • in PM: මොඩියුල පිළිබඳ තොරතුරු ඔබට යොමු කරයි.
   • in a group: Group එකේ සැකසුම් ඔබට Private Message \nඑකකින් යොමු කරයි.

{}
සහ පහත සඳහන් දෑ:
""".format(
    dispatcher.bot.first_name, ""
    if not ALLOW_EXCL else "\nසියලුම Commands '/' හෝ '!' සමඟ ක්‍රියා කරයි.\n")

SAITAMA_IMG = ARROW_IMG

DONATE_STRING = """
අඩේ! ඔබට පරිත්‍යාග කිරීමට අවශ්‍ය බව දැනගැනීමට ලැබීම සතුටක්! 

[{}](ARROW_IMG) Heroku's Servers සත්කාරකත්වය දරන අතර මේ වන විට කිසිදු පරිත්‍යාගයක් අවශ්‍ය නොවේ😁.

නමුත් ඔබට base code එකේ original writer වන \nĐ€Ş卄ΔĐ€€Ť卄ට පරිත්‍යාග කළ හැකිය. 
ඔහුට සහාය දැක්වීමට ක්‍රම දෙකක් තිබේ. [Telegram](t.me/DeshadeethThisarana) හෝ [Paypal](https://paypal.me/deshadeeththisarana) මගින් ඔහුට පරිත්‍යාග කළ හැකිය
"""

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("SaitamaRobot.modules." +
                                              module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if not imported_module.__mod_name__.lower() in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception(
            "Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=keyboard)


@run_async
def test(update: Update, context: CallbackContext):
    # pprint(eval(str(update)))
    # update.effective_message.reply_text("Hello! _මට_ `markdown` තිබේ", parse_mode=ParseMode.MARKDOWN)
    update.effective_message.reply_text("මේ හාදයා message එක edit කරා🤨")
    print(update.effective_message)


@run_async
def start(update: Update, context: CallbackContext):
    args = context.args
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split('_', 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                send_help(
                    update.effective_chat.id, HELPABLE[mod].__help__,
                    InlineKeyboardMarkup([[
                        InlineKeyboardButton(
                            text="Back", callback_data="help_back")
                    ]]))
            elif args[0].lower() == "markdownhelp":
                IMPORTED["extras"].markdown_help_sender(update)
            elif args[0].lower() == "disasters":
                IMPORTED["disasters"].send_disasters(update)
            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(
                        match.group(1), update.effective_user.id, False)
                else:
                    send_settings(
                        match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                IMPORTED["rules"].send_rules(update, args[0], from_pm=True)

        else:
            first_name = update.effective_user.first_name
            update.effective_message.reply_photo(
                SAITAMA_IMG,
                PM_START_TEXT.format(
                    escape_markdown(first_name),
                    escape_markdown(context.bot.first_name)),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton(
                             text=" 🧰 Support Group 🧰 ",
                             url="https://t.me/Gangoffriends"),
                         InlineKeyboardButton(
                             text=" 📺 Update Channel 📺 ",
                             url="https://t.me/gangoffriendschannel")
                     ],
                     [
                        InlineKeyboardButton(
                            text=" ⛑ Help ⛑ ",
                            url="https://t.me/{}?start=help".format(
                                context.bot.username)),
                         InlineKeyboardButton(
                            text=" ⚡️ Developer ⚡️ ",
                             url="https://t.me/DeshadeethThisarana")        
                       
                     ], 
                     [
                        InlineKeyboardButton(
                            text=" ➕ Add me to Your Group ↗️ ",
                            url="t.me/MrArrowbot?startgroup=true"),
                    
                    ]]))
    else:
        update.effective_message.reply_text(
            "මට ඔබට උදව් කල හැක්කේ කෙසේද? 😊"
            .format(uptime),
            parse_mode=ParseMode.HTML)

# for test purposes
def error_callback(update: Update, context: CallbackContext):
    error = context.error
    try:
        raise error
    except Unauthorized:
        print("no nono1")
        print(error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print("no nono2")
        print("BadRequest අහුවුණා")
        print(error)

        # handle malformed requests - read more below!
    except TimedOut:
        print("no nono3")
        # handle slow connection problems
    except NetworkError:
        print("no nono4")
        # handle other connection problems
    except ChatMigrated as err:
        print("no nono5")
        print(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors


@run_async
def help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)

    print(query.message.chat.id)

    try:
        if mod_match:
            module = mod_match.group(1)
            text = ("මෙන්න *{}* module එක සඳහා උපකාර:\n".format(
                HELPABLE[module].__mod_name__) + HELPABLE[module].__help__)
            query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        text="Back", callback_data="help_back")
                ]]))

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")))

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")))

        elif back_match:
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")))

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
        # query.message.delete()

    except BadRequest:
        pass


@run_async
def get_help(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            update.effective_message.reply_text(
                f"{module.capitalize()} module එකේ උදව් ලබා ගැනීමට PMහි මා අමතන්න.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        text="Help",
                        url="t.me/{}?start=ghelp_{}".format(
                            context.bot.username, module))
                ]]))
            return
        update.effective_message.reply_text(
            "විධාන ලැයිස්තුව ලබා ගැනීමට PMහි මා අමතන්න. නැත්නම් පහළින් ඇති 'Help' button එක click කරන්න😄",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    text="Help",
                    url="t.me/{}?start=help".format(context.bot.username))
            ]]))
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = "*{}* මොඩියුලය සඳහා ඇති උපකාර මෙන්න:\n  ".format(HELPABLE[module].__mod_name__) \
               + HELPABLE[module].__help__
        send_help(
            chat.id, text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Back",
                                       callback_data="help_back")]]))

    else:
        send_help(chat.id, HELP_STRINGS)


def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join("*{}*:\n{}".format(
                mod.__mod_name__, mod.__user_settings__(user_id))
                                   for mod in USER_SETTINGS.values())
            dispatcher.bot.send_message(
                user_id,
                "මේවා ඔබගේ වර්තමාන සැකසුම් වේ:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN)

        else:
            dispatcher.bot.send_message(
                user_id,
                "විශේෂිත සැකසුම් පරිශීලක නොමැති බව පෙනේ🧐 :'(",
                parse_mode=ParseMode.MARKDOWN)

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                text="{} group එකේ settings සඳහා ඔබ පරීක්ෂා කිරීමට කැමති කුමන module එකද?"
                .format(chat_name),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)))
        else:
            dispatcher.bot.send_message(
                user_id,
                "Group settings කිසිවක් නොමැති බව පෙනේ 😕:'(\nඔබ admin "
                "සිටින group එකක එහි වර්තමාන settings සොයා ගැනීමට මෙය යවන්න.",
                parse_mode=ParseMode.MARKDOWN)


@run_async
def settings_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* group එකේ *{}* මොඩියුලය සඳහා පහත සැකසුම් ඇත:\n\n".format(escape_markdown(chat.title),
                                                                                     CHAT_SETTINGS[module].__mod_name__) + \
                   CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        text="Back",
                        callback_data="stngs_back({})".format(chat_id))
                ]]))

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "ආයුබෝවන්! {} group එක සඳහා settings කිහිපයක් තිබේ - ඉදිරියට ගොස් ඔබ "
                "කැමති දේ තෝරා ගන්න.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id)))

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "ආයුබෝවන්! {} group එක සඳහා settings කිහිපයක් තිබේ - ඉදිරියට ගොස් ඔබ "
                "කැමති දේ තෝරා ගන්න.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id)))

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                text="ආයුබෝවන්! {} group එක සඳහා settings කිහිපයක් තිබේ - ඉදිරියට ගොස් ඔබ "
                "කැමති දේ තෝරා ගන්න.".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)))

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message == "පණිවිඩය වෙනස් කර නොමැත":
            pass
        elif excp.message == "විමසූ id එක අවලංගුයි":
            pass
        elif excp.message == "Message එක delete කිරීමට නොහැක😔":
            pass
        else:
            LOGGER.exception("සැකසුම් බොත්තම් වල විශිෂ්ටත්වය. %s",
                             str(query.data))


@run_async
def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "මෙම group එකේ settings මෙන්ම ඔබගේ settingsද ලබා ගැනීමට මෙතන click කරන්න👇"
            msg.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        text="Settings",
                        url="t.me/{}?start=stngs_{}".format(
                            context.bot.username, chat.id))
                ]]))
        else:
            text = "ඔබගේ settings පරීක්ෂා කිරීමට මෙතන click කරන්න."

    else:
        send_settings(chat.id, user.id, True)


@run_async
def donate(update: Update, context: CallbackContext):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]
    bot = context.bot
    if chat.type == "private":
        update.effective_message.reply_text(
            DONATE_STRING,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True)

        if OWNER_ID != 254318997 and DONATION_LINK:
            update.effective_message.reply_text(
                "දැනට මා control කරන පුද්ගලයාට ද ඔබට පරිත්‍යාග කළ හැකිය" 
                 " 👉[Click here](t.me/DeshadeethThisarana)👈",
                parse_mode=ParseMode.MARKDOWN)

    else:
        try:
            bot.send_message(
                user.id,
                DONATE_STRING,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True)

            update.effective_message.reply_text(
                "මගේ නිර්මාණකරුට පරිත්‍යාග කිරීම ගැන මම ඔබට PM message එකක් send කර ඇත්තෙමි!")
        except Unauthorized:
            update.effective_message.reply_text(
                "පරිත්‍යාග තොරතුරු ලබා ගැනීම සඳහා ප්‍රථමයෙන් PMහි මා අමතන්න.")


def migrate_chats(update: Update, context: CallbackContext):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("%s සිට %s දක්වා සංක්‍රමණය වීම", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("සාර්ථකව සංක්‍රමණය විය🙂")
    raise DispatcherHandlerStop


def main():

    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            dispatcher.bot.sendMessage(f"@GangOfFiends", "මම දැන් online සිටිමි😁")
        except Unauthorized:
            LOGGER.warning(
                "Support_chat එකට බොට්ට පණිවිඩ යැවිය නොහැක, ගොස් පරීක්ෂා කරන්න!")
        except BadRequest as e:
            LOGGER.warning(e.message)

    test_handler = CommandHandler("test", test)
    start_handler = CommandHandler("start", start)

    help_handler = CommandHandler("help", get_help)
    help_callback_handler = CallbackQueryHandler(
        help_button, pattern=r"help_.*")

    settings_handler = CommandHandler("settings", get_settings)
    settings_callback_handler = CallbackQueryHandler(
        settings_button, pattern=r"stngs_")

    donate_handler = CommandHandler("donate", donate)
    migrate_handler = MessageHandler(Filters.status_update.migrate,
                                     migrate_chats)

    # dispatcher.add_handler(test_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(settings_callback_handler)
    dispatcher.add_handler(migrate_handler)
    dispatcher.add_handler(donate_handler)

    dispatcher.add_error_handler(error_callback)

    if WEBHOOK:
        LOGGER.info("Webhooks භාවිතා කිරීම.")
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)

        if CERT_PATH:
            updater.bot.set_webhook(
                url=URL + TOKEN, certificate=open(CERT_PATH, 'rb'))
        else:
            updater.bot.set_webhook(url=URL + TOKEN)

    else:
        LOGGER.info("Long polling භාවිතා කිරීම.")
        updater.start_polling(timeout=15, read_latency=4, clean=True)

    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()

    updater.idle()


if __name__ == '__main__':
    LOGGER.info("Modules සාර්ථකව load කර ඇත: " + str(ALL_MODULES))
    telethn.start(bot_token=TOKEN)
    pbot.start()
    main()

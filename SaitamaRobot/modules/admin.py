import html

from telegram import ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters, run_async
from telegram.utils.helpers import mention_html

from SaitamaRobot import DRAGONS, dispatcher
from SaitamaRobot.modules.disable import DisableAbleCommandHandler
from SaitamaRobot.modules.helper_funcs.chat_status import (bot_admin, can_pin,
                                                           can_promote,
                                                           connection_status,
                                                           user_admin,
                                                           ADMIN_CACHE)

from SaitamaRobot.modules.helper_funcs.extraction import (extract_user,
                                                          extract_user_and_text)
from SaitamaRobot.modules.log_channel import loggable
from SaitamaRobot.modules.helper_funcs.alternate import send_message


@run_async
@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def promote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = chat.get_member(user.id)

    if not (promoter.can_promote_members or
            promoter.status == "creator") and not user.id in DRAGONS:
        message.reply_text("මේ admin නැති හාදයා මට මොකද්ද කරන්න කියන්නෙ🤨")
        return

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text(
            "ඔය ID එක වැරදි🤦‍♂️ හරියට බලන්න.."
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status == 'administrator' or user_member.status == 'creator':
        message.reply_text(
            "දැනට admin ඉන්න එකෙකුට කොහොමද මම ආපහු admin දෙන්නෙ?😤")
        return

    if user_id == bot.id:
        message.reply_text(
            "මට මාවම promote කරන්න බෑ😐. වෙන admin කෙනෙකුට කියල මාව promote කරන්න")
        return

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chat.get_member(bot.id)

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            # can_promote_members=bot_member.can_promote_members,
            can_restrict_members=bot_member.can_restrict_members,
            can_pin_messages=bot_member.can_pin_messages)
    except BadRequest as err:
        if err.message == "User_not_mutual_contact":
            message.reply_text(
                "මට මේ group එකේ නැති එකෙක්ව promote කරන්න බැහැ😬.")
        else:
            message.reply_text(".")
        return

    bot.sendMessage(
        chat.id,
        f"සාර්ථකව promote කරා😁<b>{user_member.user.first_name or user_id}</b>!",
        parse_mode=ParseMode.HTML)

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#PROMOTED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message


@run_async
@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def demote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "ඔය ID එක හෝ username එක වැරදි🤦‍♂️ හරියට බලන්න.."
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status == 'creator':
        message.reply_text(
            "මේ group එක හදපු කෙනාව මම කොහොමද demote කරන්නෙ යකෝ😠")
        return

    if not user_member.status == 'administrator':
        message.reply_text("මම admin දීපු නැති අයව මට demote කරන්න බෑ😐")
        return

    if user_id == bot.id:
        message.reply_text(
            "මට මාවම demote කරගන්න බෑ මනුස්සයෝ😬. වෙන admin කෙනෙකුට කියල ඒක කරගන්න😏.")
        return

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False)

        bot.sendMessage(
            chat.id,
            f"සාර්ථකව කෙලියා😝 <b>{user_member.user.first_name or user_id}</b>!",
            parse_mode=ParseMode.HTML)

        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#DEMOTED\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
        )

        return log_message
    except BadRequest:
        message.reply_text(
            "මට promote/demote කරන්න බෑ"
            " මට admin දුන්නොත් මම ඒ වැඩේ කරල දෙන්නම්")
        return


@run_async
@user_admin
def refresh_admin(update, _):
    try:
        ADMIN_CACHE.pop(update.effective_chat.id)
    except KeyError:
        pass

    update.effective_message.reply_text("Admins cache අලුත් කරා😃")


@run_async
@connection_status
@bot_admin
@can_promote
@user_admin
def set_title(update: Update, context: CallbackContext):
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message

    user_id, title = extract_user_and_text(message, args)
    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if not user_id:
        message.reply_text(
            "ඔය ID එක හෝ username එක වැරදි🤦‍♂️ හරියට බලන්න.."
        )
        return

    if user_member.status == 'creator':
        message.reply_text(
            "මේ group එක හදපු කෙනාට මම කොහොමද custom title එකක් දාන්නෙ?😠")
        return

    if not user_member.status == 'administrator':
        message.reply_text(
            "Admin නැති කෙනෙකුට කොහොමද title එකක් දාන්නෙ😬\nමුලින්ම admin දීලා ඊට පස්සෙ custom title එකක් දාන්න"
        )
        return

    if user_id == bot.id:
        message.reply_text(
            "මට මගේ custom title දාන්න බෑ😔. මට admin දුන්න කෙනාට කියල මගේ title එක දාවන්න."
        )
        return

    if not title:
        message.reply_text("Title එක හිස් තියල වැඩක් නෑ.")
        return

    if len(title) > 16:
        message.reply_text(
            "Title length එක characters 16ට වඩා වැඩියි.\nඒක characters 16ට වඩා අඩු කරන්න."
        )

    try:
        bot.setChatAdministratorCustomTitle(chat.id, user_id, title)
    except BadRequest:
        message.reply_text(
            "මම admin දුන්නෙ නැති අයට මට title එක දාන්න බෑ.")
        return

    bot.sendMessage(
        chat.id,
        f"සාර්ථකව <code>{user_member.user.first_name or user_id}</code>ට title එක දැම්මා😁"
        f"to <code>{html.escape(title[:16])}</code>!",
        parse_mode=ParseMode.HTML)


@run_async
@bot_admin
@can_pin
@user_admin
@loggable
def pin(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    user = update.effective_user
    chat = update.effective_chat

    is_group = chat.type != "private" and chat.type != "channel"
    prev_message = update.effective_message.reply_to_message

    is_silent = True
    if len(args) >= 1:
        is_silent = not (args[0].lower() == 'notify' or args[0].lower()
                         == 'loud' or args[0].lower() == 'violent')

    if prev_message and is_group:
        try:
            bot.pinChatMessage(
                chat.id,
                prev_message.message_id,
                disable_notification=is_silent)
        except BadRequest as excp:
            if excp.message == "Chat_not_modified":
                pass
            else:
                raise
        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#PINNED\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}"
        )

        return log_message


@run_async
@bot_admin
@can_pin
@user_admin
@loggable
def unpin(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    chat = update.effective_chat
    user = update.effective_user

    try:
        bot.unpinChatMessage(chat.id)
    except BadRequest as excp:
        if excp.message == "Chat_not_modified":
            pass
        else:
            raise

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNPINNED\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}")

    return log_message


@run_async
@bot_admin
@user_admin
@connection_status
def invite(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat

    if chat.username:
        update.effective_message.reply_text(f"https://t.me/{chat.username}")
    elif chat.type == chat.SUPERGROUP or chat.type == chat.CHANNEL:
        bot_member = chat.get_member(bot.id)
        if bot_member.can_invite_users:
            invitelink = bot.exportChatInviteLink(chat.id)
            update.effective_message.reply_text(invitelink)
        else:
            update.effective_message.reply_text(
                "I don't have access to the invite link, try changing my permissions!"
            )
    else:
        update.effective_message.reply_text(
            "I can only give you invite links for supergroups and channels, sorry!"
        )


@run_async
@connection_status
def adminlist(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    args = context.args
    bot = context.bot

    if update.effective_message.chat.type == "private":
        send_message(update.effective_message,
                     "This command only works in Groups.")
        return

    chat = update.effective_chat
    chat_id = update.effective_chat.id
    chat_name = update.effective_message.chat.title

    try:
        msg = update.effective_message.reply_text(
            'Fetching group admins...', parse_mode=ParseMode.HTML)
    except BadRequest:
        msg = update.effective_message.reply_text(
            'Fetching group admins...', quote=False, parse_mode=ParseMode.HTML)

    administrators = bot.getChatAdministrators(chat_id)
    text = "Admins in <b>{}</b>:".format(
        html.escape(update.effective_chat.title))

    bot_admin_list = []

    for admin in administrators:
        user = admin.user
        status = admin.status
        custom_title = admin.custom_title

        if user.first_name == '':
            name = "☠ Deleted Account"
        else:
            name = "{}".format(
                mention_html(
                    user.id,
                    html.escape(user.first_name + " " +
                                (user.last_name or ""))))

        if user.is_bot:
            bot_admin_list.append(name)
            administrators.remove(admin)
            continue

        #if user.username:
        #    name = escape_markdown("@" + user.username)
        if status == "creator":
            text += "\n 👑 Creator:"
            text += "\n<code> • </code>{}\n".format(name)

            if custom_title:
                text += f"<code> ┗━ {html.escape(custom_title)}</code>\n"

    text += "\n🔱 Admins:"

    custom_admin_list = {}
    normal_admin_list = []

    for admin in administrators:
        user = admin.user
        status = admin.status
        custom_title = admin.custom_title

        if user.first_name == '':
            name = "☠ Deleted Account"
        else:
            name = "{}".format(
                mention_html(
                    user.id,
                    html.escape(user.first_name + " " +
                                (user.last_name or ""))))
        #if user.username:
        #    name = escape_markdown("@" + user.username)
        if status == "administrator":
            if custom_title:
                try:
                    custom_admin_list[custom_title].append(name)
                except KeyError:
                    custom_admin_list.update({custom_title: [name]})
            else:
                normal_admin_list.append(name)

    for admin in normal_admin_list:
        text += "\n<code> • </code>{}".format(admin)

    for admin_group in custom_admin_list.copy():
        if len(custom_admin_list[admin_group]) == 1:
            text += "\n<code> • </code>{} | <code>{}</code>".format(
                custom_admin_list[admin_group][0], html.escape(admin_group))
            custom_admin_list.pop(admin_group)

    text += "\n"
    for admin_group in custom_admin_list:
        text += "\n🚨 <code>{}</code>".format(admin_group)
        for admin in custom_admin_list[admin_group]:
            text += "\n<code> • </code>{}".format(admin)
        text += "\n"

    text += "\n🤖 Bots:"
    for each_bot in bot_admin_list:
        text += "\n<code> • </code>{}".format(each_bot)

    try:
        msg.edit_text(text, parse_mode=ParseMode.HTML)
    except BadRequest:  # if original message is deleted
        return


__help__ = """
 • `/admins`*:* list of admins in the chat

*Admins only:*
 • `/pin`*:* silently pins the message replied to - add `'loud'` or `'notify'` to give notifs to users
 • `/unpin`*:* unpins the currently pinned message
 • `/invitelink`*:* gets invitelink
 • `/promote`*:* promotes the user replied to
 • `/demote`*:* demotes the user replied to
 • `/title <title here>`*:* sets a custom title for an admin that the bot promoted
 • `/admincache`*:* force refresh the admins list
 • `/zombies` *:* Scan deleted accounts
 • `/zombies clean` *:* Cleans deleted accounts
"""

ADMINLIST_HANDLER = DisableAbleCommandHandler("admins", adminlist)

PIN_HANDLER = CommandHandler("pin", pin, filters=Filters.group)
UNPIN_HANDLER = CommandHandler("unpin", unpin, filters=Filters.group)

INVITE_HANDLER = DisableAbleCommandHandler("invitelink", invite)

PROMOTE_HANDLER = DisableAbleCommandHandler("promote", promote)
DEMOTE_HANDLER = DisableAbleCommandHandler("demote", demote)

SET_TITLE_HANDLER = CommandHandler("title", set_title)
ADMIN_REFRESH_HANDLER = CommandHandler(
    "admincache", refresh_admin, filters=Filters.group)

dispatcher.add_handler(ADMINLIST_HANDLER)
dispatcher.add_handler(PIN_HANDLER)
dispatcher.add_handler(UNPIN_HANDLER)
dispatcher.add_handler(INVITE_HANDLER)
dispatcher.add_handler(PROMOTE_HANDLER)
dispatcher.add_handler(DEMOTE_HANDLER)
dispatcher.add_handler(SET_TITLE_HANDLER)
dispatcher.add_handler(ADMIN_REFRESH_HANDLER)

__mod_name__ = "Admin"
__command_list__ = [
    "adminlist", "admins", "invitelink", "promote", "demote", "admincache"
]
__handlers__ = [
    ADMINLIST_HANDLER, PIN_HANDLER, UNPIN_HANDLER, INVITE_HANDLER,
    PROMOTE_HANDLER, DEMOTE_HANDLER, SET_TITLE_HANDLER, ADMIN_REFRESH_HANDLER
]

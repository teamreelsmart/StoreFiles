from datetime import datetime, timedelta
import re
from urllib.parse import quote
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNER_ID


async def _debug_log(client: Client, where: str, error: Exception, user_id: int | None = None):
    log_channel = int(getattr(client, 'verify_log_channel', 0) or 0)
    if not log_channel:
        return
    msg = f"⚠️ Refer Debug Error\nWhere: `{where}`\nError: `{str(error)[:1500]}`"
    if user_id is not None:
        msg += f"\nUser: `{user_id}`"
    try:
        await client.send_message(log_channel, msg)
    except Exception:
        pass


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


async def grant_referral_day(client: Client, user_id: int):
    now = datetime.now()
    if await client.mongodb.is_pro(user_id):
        current_expiry = await client.mongodb.get_expiry_date(user_id)
        if current_expiry is None:
            return
    else:
        current_expiry = None

    base = current_expiry if current_expiry and current_expiry > now else now
    await client.mongodb.add_pro(user_id, base + timedelta(days=1))


async def build_refer_panel(client: Client, user):
    invite_link = f"https://t.me/{client.username}?start=refer_{user.id}"
    photo = client.messages.get("REFER_PHOTO", client.messages.get("START_PHOTO", ""))
    caption = client.messages.get(
        "REFER_MSG",
        "<b>🎁 Refer & Earn!\nInvite your friends and both of you get 1 day premium after successful join.</b>\n\n🔗 {invite_link}"
    ).format(invite_link=invite_link)

    share_text = "Check this awesome file"
    share_url = (
        "https://t.me/share/url"
        f"?url={quote(invite_link, safe='')}"
        f"&text={quote(share_text, safe='')}"
    )
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("📨 Share Invite", url=share_url)],
        [InlineKeyboardButton("🔗 Invite Link", url=invite_link)]
    ])

    return photo, caption, markup


async def send_refer_panel(client: Client, chat_id: int, user):
    photo, caption, markup = await build_refer_panel(client, user)

    # Try full rich message first
    if photo:
        try:
            return await client.send_photo(chat_id, photo=photo, caption=caption, reply_markup=markup)
        except Exception as e:
            await _debug_log(client, "send_refer_panel.send_photo", e, user.id)

    # Fallback plain text (no HTML parse problems)
    plain = _strip_html(caption)
    try:
        return await client.send_message(chat_id, text=plain, reply_markup=markup)
    except Exception as e:
        await _debug_log(client, "send_refer_panel.send_message", e, user.id)
        raise


async def handle_referral_payload(client: Client, message, payload: str) -> bool:
    if not payload.startswith("refer_"):
        return False

    user_id = message.from_user.id
    try:
        referrer_id = int(payload.split("refer_", 1)[1])

        if referrer_id == user_id:
            await message.reply("⚠️ You cannot refer yourself.")
            return True

        if not await client.mongodb.present_user(referrer_id):
            await message.reply("⚠️ Referrer not found.")
            return True

        existing_referrer = await client.mongodb.get_referrer(user_id)
        if existing_referrer:
            await message.reply("⚠️ Referral already claimed for your account.")
            return True

        await client.mongodb.set_referrer(user_id, referrer_id)

        if not await client.mongodb.is_referral_rewarded(user_id):
            await grant_referral_day(client, user_id)
            await grant_referral_day(client, referrer_id)
            await client.mongodb.mark_referral_rewarded(user_id)
            await client.mongodb.add_referral_success(referrer_id)

            try:
                await client.send_message(referrer_id, f"🎉 You referred a new user: {message.from_user.mention}. Both got 1 day premium!")
            except Exception as e:
                await _debug_log(client, "handle_referral_payload.notify_referrer", e, referrer_id)

            try:
                await client.send_message(user_id, f"🎉 You were referred by [user](tg://user?id={referrer_id}). You got 1 day premium!")
            except Exception as e:
                await _debug_log(client, "handle_referral_payload.notify_referred", e, user_id)

            owner_msg = f"✅ Referral Success\nReferrer: [user](tg://user?id={referrer_id})\nReferred: {message.from_user.mention}\nReward: 1 day premium both"
            try:
                await client.send_message(OWNER_ID, owner_msg)
            except Exception as e:
                await _debug_log(client, "handle_referral_payload.notify_owner", e, OWNER_ID)

            log_channel = int(getattr(client, 'verify_log_channel', 0) or 0)
            if log_channel:
                try:
                    await client.send_message(log_channel, owner_msg)
                except Exception as e:
                    await _debug_log(client, "handle_referral_payload.notify_log", e, log_channel)

        return True

    except Exception as e:
        await _debug_log(client, "handle_referral_payload.main", e, user_id)
        await message.reply("⚠️ Referral processing error. Please try again.")
        return True


@Client.on_message(filters.command('refer') & filters.private)
async def refer_command(client: Client, message):
    try:
        await send_refer_panel(client, message.chat.id, message.from_user)
    except Exception as e:
        await _debug_log(client, "refer_command", e, message.from_user.id)
        await message.reply("⚠️ Refer panel error. Admin has been notified.")


@Client.on_callback_query(filters.regex('^refer_earn$'))
async def refer_callback(client: Client, query):
    if not query.from_user:
        return
    await query.answer()
    try:
        await send_refer_panel(client, query.message.chat.id, query.from_user)
    except Exception as e:
        await _debug_log(client, "refer_callback", e, query.from_user.id)
        await query.message.reply("⚠️ Refer panel error. Admin has been notified.")

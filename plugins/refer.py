from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNER_ID


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


async def send_refer_panel(client: Client, user):
    invite_link = f"https://t.me/{client.username}?start=refer_{user.id}"
    photo = client.messages.get("REFER_PHOTO", client.messages.get("START_PHOTO", ""))
    caption = client.messages.get(
        "REFER_MSG",
        "<b>🎁 Refer & Earn!\nInvite your friends and both of you get 1 day premium after successful join.</b>\n\n🔗 {invite_link}"
    ).format(invite_link=invite_link)

    share_text = "Hey brother i just found a Amezing network for viral videos and other stuff here link join fast you get  day premium as joining bonu"
    share_url = f"https://t.me/share/url?url={invite_link}&text={share_text}"
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("📨 Share Invite", url=share_url)],
        [InlineKeyboardButton("🔗 Invite Link", url=invite_link)]
    ])

    if photo:
        try:
            return photo, caption, markup
        except Exception:
            pass
    return None, caption, markup


async def handle_referral_payload(client: Client, message, payload: str) -> bool:
    if not payload.startswith("refer_"):
        return False

    user_id = message.from_user.id
    try:
        referrer_id = int(payload.split("refer_", 1)[1])
    except Exception:
        await message.reply("⚠️ Invalid referral link.")
        return True

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
        except Exception:
            pass

        try:
            await client.send_message(user_id, f"🎉 You were referred by [user](tg://user?id={referrer_id}). You got 1 day premium!")
        except Exception:
            pass

        owner_msg = f"✅ Referral Success\nReferrer: [user](tg://user?id={referrer_id})\nReferred: {message.from_user.mention}\nReward: 1 day premium both"
        try:
            await client.send_message(OWNER_ID, owner_msg)
        except Exception:
            pass

        log_channel = int(getattr(client, 'verify_log_channel', 0) or 0)
        if log_channel:
            try:
                await client.send_message(log_channel, owner_msg)
            except Exception:
                pass

    return True


@Client.on_message(filters.command('refer') & filters.private)
async def refer_command(client: Client, message):
    photo, caption, markup = await send_refer_panel(client, message.from_user)
    if photo:
        try:
            return await client.send_photo(message.chat.id, photo=photo, caption=caption, reply_markup=markup)
        except Exception:
            pass
    return await message.reply(caption, reply_markup=markup)


@Client.on_callback_query(filters.regex('^refer_earn$'))
async def refer_callback(client: Client, query):
    if not query.from_user:
        return
    await query.answer()
    photo, caption, markup = await send_refer_panel(client, query.from_user)
    if photo:
        try:
            return await client.send_photo(query.message.chat.id, photo=photo, caption=caption, reply_markup=markup)
        except Exception:
            pass
    return await query.message.reply(caption, reply_markup=markup)

from helper.helper_func import *
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import humanize
from config import MSG_EFFECT, OWNER_ID
from plugins.shortner import get_short
from helper.helper_func import get_messages, force_sub, decode, batch_auto_del_notification
import asyncio
import secrets
from datetime import datetime, timedelta

#===============================================================#

def build_verify_path(client: Client, token: str) -> str:
    base = getattr(client, 'service_url', '').rstrip('/')
    return f"{base}/verify/{token}" if base else f"https://t.me/{client.username}?start=verify_{token}"


async def issue_verify_link(client: Client, message: Message, payload: str):
    token = secrets.token_urlsafe(8).replace('-', '').replace('_', '')[:10]
    deep_link = f"https://t.me/{client.username}?start=verify_{token}"
    provider = await client.mongodb.get_next_shortner_provider(message.from_user.id)
    try:
        short_link = get_short(deep_link, client, provider=provider)
    except Exception as e:
        client.LOGGER(__name__, client.name).warning(f"Shortener failed: {e}")
        return await message.reply("Couldn't generate short link.")

    expires_at = datetime.now() + timedelta(seconds=max(int(getattr(client, 'verify_cooldown', 30)), 1))
    await client.mongodb.create_verify_link(token, message.from_user.id, payload, short_link, expires_at, provider)

    short_photo = client.messages.get("SHORT_PIC", "")
    short_caption = client.messages.get("SHORT_MSG", "")
    tutorial_link = getattr(client, 'tutorial_link', "https://t.me/HowToDownloadSnap/2")
    service_link = build_verify_path(client, token)

    access_hours = int(getattr(client, 'verify_access_hours', 4) or 4)

    await client.send_photo(
        chat_id=message.chat.id,
        photo=short_photo,
        caption=(
            f"{short_caption}\n\n"
            f"⏱ Verify timer: {getattr(client, 'verify_cooldown', 30)}s\n"
            f"✅ One-time verification unlocks {access_hours} hour(s) access"
        ),
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("• ᴏᴘᴇɴ ʟɪɴᴋ", url=service_link),
                InlineKeyboardButton("ᴛᴜᴛᴏʀɪᴀʟ •", url=tutorial_link)
            ],
            [
                InlineKeyboardButton(" • ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ •", url="https://t.me/SnapLoverXBot?start=premium")
            ]
        ])
    )


async def send_verify_bypass_warning(client: Client, message: Message, attempt_count: int, seconds_left: int):
    warning_photo = client.messages.get("VERIFY_WARN_PHOTO", client.messages.get("SHORT_PIC", ""))
    warning_text = client.messages.get(
        "VERIFY_WARN_MSG",
        "⚠️ You are trying to bypass verification.\nWait {seconds}s and use the new link.\nAttempt: {attempt}/2"
    )
    caption = warning_text.format(attempt=attempt_count, seconds=max(seconds_left, 0))

    if warning_photo:
        try:
            return await client.send_photo(
                chat_id=message.chat.id,
                photo=warning_photo,
                caption=caption
            )
        except Exception as e:
            client.LOGGER(__name__, client.name).warning(f"Failed to send verify warning photo: {e}")

    return await message.reply(caption)



async def send_start_home(client: Client, message: Message):
    user_id = message.from_user.id
    buttons = [
        [InlineKeyboardButton("🎁 Refer & Earn", callback_data="refer_earn")],
    ]

    service_url = getattr(client, 'service_url', '').rstrip('/')
    if service_url:
        mini_url = f"{service_url}/mini/{user_id}"
        buttons.append([InlineKeyboardButton("📱 Mini App", url=mini_url)])

    buttons.append([InlineKeyboardButton("Help", callback_data="about"), InlineKeyboardButton("Close", callback_data='close')])
    if user_id in client.admins:
        buttons.insert(0, [InlineKeyboardButton("⛩️ ꜱᴇᴛᴛɪɴɢꜱ ⛩️", callback_data="settings")])

    photo = client.messages.get("START_PHOTO", "")
    start_caption = client.messages.get('START', 'Welcome, {mention}').format(
        first=message.from_user.first_name,
        last=message.from_user.last_name,
        username=None if not message.from_user.username else '@' + message.from_user.username,
        mention=message.from_user.mention,
        id=message.from_user.id
    )

    if photo:
        await client.send_photo(
            chat_id=message.chat.id,
            photo=photo,
            caption=start_caption,
            message_effect_id=MSG_EFFECT,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        await client.send_message(
            chat_id=message.chat.id,
            text=start_caption,
            message_effect_id=MSG_EFFECT,
            reply_markup=InlineKeyboardMarkup(buttons)
        )


async def grant_referral_day(client: Client, user_id: int):
    now = datetime.now()
    # Permanent premium users should remain permanent
    if await client.mongodb.is_pro(user_id):
        current_expiry = await client.mongodb.get_expiry_date(user_id)
        if current_expiry is None:
            return
    else:
        current_expiry = None

    base = current_expiry if current_expiry and current_expiry > now else now
    await client.mongodb.add_pro(user_id, base + timedelta(days=1))


async def send_refer_panel(client: Client, message: Message):
    invite_link = f"https://t.me/{client.username}?start=refer_{message.from_user.id}"
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
            return await client.send_photo(message.chat.id, photo=photo, caption=caption, reply_markup=markup)
        except Exception:
            pass
    return await message.reply(caption, reply_markup=markup)

@Client.on_message(filters.command('start') & filters.private)
@force_sub
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id

    present = await client.mongodb.present_user(user_id)
    if not present:
        try:
            await client.mongodb.add_user(user_id)
        except Exception as e:
            client.LOGGER(__name__, client.name).warning(f"Error adding a user:\n{e}")

    is_banned = await client.mongodb.is_banned(user_id)
    if is_banned:
        return await message.reply("**You have been banned from using this bot!**")

    text = message.text
    if len(text) > 7:
        try:
            original_payload = text.split(" ", 1)[1]
            base64_string = original_payload
        except IndexError:
            return await message.reply("Invalid command format.")

        verify_token = None
        is_short_link = False

        if base64_string.startswith("refer_"):
            try:
                referrer_id = int(base64_string.split("refer_", 1)[1])
            except Exception:
                return await message.reply("⚠️ Invalid referral link.")

            if referrer_id == user_id:
                return await message.reply("⚠️ You cannot refer yourself.")

            if not await client.mongodb.present_user(referrer_id):
                return await message.reply("⚠️ Referrer not found.")

            existing_referrer = await client.mongodb.get_referrer(user_id)
            if existing_referrer:
                return await message.reply("⚠️ Referral already claimed for your account.")

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

            await send_start_home(client, message)
            return

        if base64_string.startswith("channel_"):
            try:
                _, channel_id_raw, _ = base64_string.split("_", 2)
                channel_id = int(channel_id_raw)
                chat = await client.get_chat(channel_id)
                invite = await client.create_chat_invite_link(
                    channel_id,
                    expire_date=datetime.now() + timedelta(minutes=15),
                    creates_join_request=True
                )
            except Exception as e:
                client.LOGGER(__name__, client.name).warning(f"Channel invite generation failed: {e}")
                return await message.reply("⚠️ Unable to generate channel invite. Make sure bot is admin in channel.")

            photo = client.messages.get("CHANNEL_LINK_PHOTO", client.messages.get("FSUB_PHOTO", ""))
            text = client.messages.get(
                "CHANNEL_LINK_MSG",
                "<b>Join request link is ready for <i>{channel_name}</i>.\nThis link expires in {expire_minutes} minutes.</b>"
            ).format(channel_name=chat.title or "Channel", expire_minutes=15, channel_id=channel_id)
            buttons = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Join Channel", url=invite.invite_link)]])

            if photo:
                try:
                    await client.send_photo(chat_id=message.chat.id, photo=photo, caption=text, reply_markup=buttons)
                except Exception:
                    await message.reply(text, reply_markup=buttons)
            else:
                await message.reply(text, reply_markup=buttons)
            return

        if base64_string.startswith("verify_"):
            verify_token = base64_string.split("verify_", 1)[1]
            verify_data = await client.mongodb.get_verify_link(verify_token)
            if not verify_data:
                return await message.reply("⚠️ Invalid or expired verify link.")
            if verify_data.get("used"):
                return await message.reply("⚠️ This link is already used. Generate a new one.")
            if verify_data.get("user_id") != user_id:
                return await message.reply("⚠️ This verify link is only for the original user.")

            expires_at = verify_data.get("expires_at")
            if expires_at and datetime.now() < expires_at:
                count = await client.mongodb.increment_early_verify_violation(user_id)
                left = int((expires_at - datetime.now()).total_seconds())
                await client.mongodb.remove_verify_link(verify_token)

                mention = f"[{message.from_user.first_name}](tg://user?id={user_id})"
                log_text = (
                    f"⚠️ Early verify detected\n"
                    f"User: {mention}\nUser ID: `{user_id}`\n"
                    f"Attempts: `{count}`\nRemaining: `{max(left, 0)}s`\n"
                    f"Payload: `{verify_data.get('payload', '')[:64]}`"
                )
                log_channel = int(getattr(client, 'verify_log_channel', 0) or 0)
                if log_channel:
                    try:
                        await client.send_message(log_channel, log_text)
                    except Exception as e:
                        client.LOGGER(__name__, client.name).warning(f"Failed to send verify log: {e}")

                if count >= 2:
                    await client.mongodb.ban_user(user_id)
                    return await message.reply("🚫 You are banned for repeated early verification abuse.")

                await send_verify_bypass_warning(client, message, count, left)
                await issue_verify_link(client, message, verify_data.get("payload", ""))
                return

            await client.mongodb.mark_verify_link_used(verify_token)
            await client.mongodb.reset_early_verify_violation(user_id)
            await client.mongodb.set_last_shortner_provider(user_id, verify_data.get("provider", "primary"))
            verify_access_hours = int(getattr(client, 'verify_access_hours', 4) or 4)
            await client.mongodb.set_verify_pass(user_id, verify_access_hours)
            base64_string = verify_data.get("payload", "")
            original_payload = base64_string
            is_short_link = True

        elif base64_string.startswith("yu3elk"):
            base64_string = base64_string[6:-1]
            is_short_link = True

        is_user_pro = await client.mongodb.is_pro(user_id)
        has_verify_pass = await client.mongodb.has_active_verify_pass(user_id)
        shortner_enabled = getattr(client, 'shortner_enabled', True)

        if not is_user_pro and user_id != OWNER_ID and not is_short_link and shortner_enabled and not has_verify_pass:
            await issue_verify_link(client, message, base64_string)
            return

        # 6. Decode and prepare file IDs
        try:
            string = await decode(base64_string)
            argument = string.split("-")
            ids = []
            source_channel_id = None

            if len(argument) == 3:
                # Try to determine source channel from encoded multiplier
                encoded_start = int(argument[1])
                encoded_end = int(argument[2])
                
                # Try primary channel first
                primary_multiplier = abs(client.db)
                start_primary = int(encoded_start / primary_multiplier)
                end_primary = int(encoded_end / primary_multiplier)
                
                # Check if the division results in clean integers (meaning this channel was used for encoding)
                if encoded_start % primary_multiplier == 0 and encoded_end % primary_multiplier == 0:
                    source_channel_id = client.db
                    start = start_primary
                    end = end_primary
                    client.LOGGER(__name__, client.name).info(f"Decoded batch from primary channel {source_channel_id}: {start}-{end}")
                else:
                    # Try secondary channels
                    db_channels = getattr(client, 'db_channels', {})
                    for channel_id_str in db_channels.keys():
                        channel_id = int(channel_id_str)
                        channel_multiplier = abs(channel_id)
                        start_test = int(encoded_start / channel_multiplier)
                        end_test = int(encoded_end / channel_multiplier)
                        
                        if encoded_start % channel_multiplier == 0 and encoded_end % channel_multiplier == 0:
                            source_channel_id = channel_id
                            start = start_test
                            end = end_test
                            client.LOGGER(__name__, client.name).info(f"Decoded batch from secondary channel {source_channel_id}: {start}-{end}")
                            break
                    
                    # Fallback to primary if no match found
                    if source_channel_id is None:
                        source_channel_id = client.db
                        start = start_primary
                        end = end_primary
                
                ids = range(start, end + 1) if start <= end else list(range(start, end - 1, -1))

            elif len(argument) == 2:
                # Single message
                encoded_msg = int(argument[1])
                
                # Try primary channel first
                if hasattr(client, 'db_channel') and client.db_channel:
                    primary_multiplier = abs(client.db_channel.id)
                    msg_id_primary = int(encoded_msg / primary_multiplier)
                    
                    if encoded_msg % primary_multiplier == 0:
                        source_channel_id = client.db_channel.id
                        ids = [msg_id_primary]
                    else:
                        # Try secondary channels
                        db_channels = getattr(client, 'db_channels', {})
                        for channel_id_str in db_channels.keys():
                            channel_id = int(channel_id_str)
                            channel_multiplier = abs(channel_id)
                            msg_id_test = int(encoded_msg / channel_multiplier)
                            
                            if encoded_msg % channel_multiplier == 0:
                                source_channel_id = channel_id
                                ids = [msg_id_test]
                                break
                        
                        # Fallback to primary
                        if source_channel_id is None:
                            source_channel_id = client.db_channel.id if hasattr(client, 'db_channel') else client.db
                            ids = [msg_id_primary]
                else:
                    # Fallback for legacy compatibility
                    source_channel_id = client.db
                    ids = [int(encoded_msg / abs(client.db))]

        except Exception as e:
            client.LOGGER(__name__, client.name).warning(f"Error decoding base64: {e}")
            return await message.reply("⚠️ Invalid or expired link.")

        # 7. Get messages from the specific source channel first
        temp_msg = await message.reply("Wait A Sec..")
        messages = []

        try:
            # Try to get messages from the identified source channel first
            if source_channel_id:
                client.LOGGER(__name__, client.name).info(f"Trying to get messages from source channel: {source_channel_id}")
                try:
                    msgs = await client.get_messages(
                        chat_id=source_channel_id,
                        message_ids=list(ids)
                    )
                    # Filter out None messages (deleted/not found)
                    valid_msgs = [msg for msg in msgs if msg is not None]
                    messages.extend(valid_msgs)
                    client.LOGGER(__name__, client.name).info(f"Found {len(valid_msgs)} messages from source channel {source_channel_id}")
                    
                    # If we didn't get all messages, try the fallback system
                    if len(valid_msgs) < len(list(ids)):
                        missing_ids = [mid for mid in ids if mid not in {msg.id for msg in valid_msgs}]
                        if missing_ids:
                            client.LOGGER(__name__, client.name).info(f"Missing {len(missing_ids)} messages, trying fallback system")
                            # Use the fallback system for missing messages
                            additional_messages = await get_messages(client, missing_ids)
                            messages.extend(additional_messages)
                            client.LOGGER(__name__, client.name).info(f"Found {len(additional_messages)} additional messages from fallback")
                except Exception as e:
                    client.LOGGER(__name__, client.name).warning(f"Error getting messages from source channel {source_channel_id}: {e}")
                    # Fallback to the multi-channel system
                    messages = await get_messages(client, ids)
            else:
                client.LOGGER(__name__, client.name).info("No specific source channel identified, using multi-channel fallback")
                # Use the multi-channel fallback system
                messages = await get_messages(client, ids)
        except Exception as e:
            await temp_msg.edit_text("Something went wrong!")
            client.LOGGER(__name__, client.name).warning(f"Error getting messages: {e}")
            return

        if not messages:
            return await temp_msg.edit("Couldn't find the files in the database.")
        await temp_msg.delete()

        yugen_msgs = []
        for msg in messages:
            caption = (
                client.messages.get('CAPTION', '').format(
                    previouscaption=msg.caption.html if msg.caption else msg.document.file_name
                ) if bool(client.messages.get('CAPTION', '')) and bool(msg.document)
                else ("" if not msg.caption else msg.caption.html)
            )
            reply_markup = msg.reply_markup if not client.disable_btn else None

            try:
                copied_msg = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    reply_markup=reply_markup,
                    protect_content=client.protect
                )
                yugen_msgs.append(copied_msg)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                copied_msg = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    reply_markup=reply_markup,
                    protect_content=client.protect
                )
                yugen_msgs.append(copied_msg)
            except Exception as e:
                client.LOGGER(__name__, client.name).warning(f"Failed to send message: {e}")
                pass

        # 8. Auto delete timer
        if messages and client.auto_del > 0:
            # Create transfer link for getting files again (original base64_string)
            transfer_link = original_payload
            
            # Start batch auto delete notification - single notification for all files
            asyncio.create_task(batch_auto_del_notification(
                bot_username=client.username,
                messages=yugen_msgs,
                delay_time=client.auto_del,
                transfer_link=transfer_link,
                chat_id=message.from_user.id,
                client=client
            ))
        return

    # 9. Normal start message
    else:
        buttons = [[InlineKeyboardButton("Help", callback_data="about"), InlineKeyboardButton("Close", callback_data='close')]]
        if user_id in client.admins:
            buttons.insert(0, [InlineKeyboardButton("⛩️ ꜱᴇᴛᴛɪɴɢꜱ ⛩️", callback_data="settings")])

        photo = client.messages.get("START_PHOTO", "")
        start_caption = client.messages.get('START', 'Welcome, {mention}').format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        )

        if photo:
            await client.send_photo(
                chat_id=message.chat.id,
                photo=photo,
                caption=start_caption,
                message_effect_id=MSG_EFFECT,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            await client.send_message(
                chat_id=message.chat.id,
                text=start_caption,
                message_effect_id=MSG_EFFECT,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        return


#===============================================================#

@Client.on_message(filters.command('refer') & filters.private)
@force_sub
async def refer_command(client: Client, message: Message):
    await send_refer_panel(client, message)


@Client.on_callback_query(filters.regex('^refer_earn$'))
async def refer_callback(client: Client, query):
    if not query.from_user:
        return

    dummy = query.message
    # Reuse sender with callback message context
    class _Msg:
        from_user = query.from_user
        chat = query.message.chat
        reply = query.message.reply
    await query.answer()
    await send_refer_panel(client, _Msg())



@Client.on_message(filters.command('mini') & filters.private)
@force_sub
async def mini_command(client: Client, message: Message):
    service_url = getattr(client, 'service_url', '').rstrip('/')
    if not service_url:
        return await message.reply("⚠️ Mini app is not configured yet.")

    mini_url = f"{service_url}/mini/{message.from_user.id}"
    await message.reply(
        f"📱 Open your mini app profile:\n{mini_url}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Open Mini App", url=mini_url)]])
    )


#===============================================================#

@Client.on_message(filters.command('request') & filters.private)
async def request_command(client: Client, message: Message):
    user_id = message.from_user.id
    is_admin = user_id in client.admins  # ✅ Fix this line
    is_user_premium = await client.mongodb.is_pro(user_id)

    if is_admin or user_id == OWNER_ID:
        await message.reply_text("🔹 **You are my sensei!**\nThis command is only for users.")
        return

    if not is_user_premium: 
        BUTTON_URL = "https://t.me/SnapLoverXBot?start=premium"
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 Upgrade to Premium", url=BUTTON_URL)]
        ])
        await message.reply(
            "❌ **You are not a premium user.**\nUpgrade to premium to access this feature.",
            reply_markup=reply_markup
        )
        return

    if len(message.command) < 2:
        await message.reply("⚠️ **Send me your request in this format:**\n`/request Your_Request_Here`")
        return

    requested = " ".join(message.command[1:])

    owner_message = (
        f"📩 **New Request from {message.from_user.mention}**\n\n"
        f"🆔 User ID: `{user_id}`\n"
        f"📝 Request: `{requested}`"
    )

    await client.send_message(OWNER_ID, owner_message)
    await message.reply("✅ **Thanks for your request!**\nYour request will be reviewed soon. Please wait.")

#===============================================================#

@Client.on_message(filters.command('profile') & filters.private)
async def my_plan(client: Client, message: Message):
    user_id = message.from_user.id
    is_admin = user_id in client.admins  # ✅ Fix here

    if is_admin or user_id == OWNER_ID:
        await message.reply_text("🔹 You're my sensei! This command is only for users.")
        return
    
    is_user_premium = await client.mongodb.is_pro(user_id)

    if is_user_premium:
        await message.reply_text(
            "**👤 Profile Information:**\n\n"
            "🔸 Ads: Disabled\n"
            "🔸 Plan: Premium\n"
            "🔸 Request: Enabled\n\n"
            "🌟 You're a Premium User!"
        )
    else:
        await message.reply_text(
            "**👤 Profile Information:**\n\n"
            "🔸 Ads: Enabled\n"
            "🔸 Plan: Free\n"
            "🔸 Request: Disabled\n\n"
            "🔓 Unlock Premium to get more benefits\n"
            "Contact: @SnapLoverXBot"
        )

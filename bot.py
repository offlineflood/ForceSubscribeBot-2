import logging
import asyncio
import string
import random
from telethon.utils import get_display_name
import re
from telethon import TelegramClient, events, Button
from decouple import config
from telethon.tl.functions.users import GetFullUserRequest
from telethon.errors.rpcerrorlist import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.INFO)

appid = apihash = bottoken = None
# start the bot
print("Starting...")
try:
    apiid = config("API_ID", cast=int)
    apihash = config("API_HASH")
    bottoken = config("BOT_TOKEN")
    xchannel = config("CHANNEL")
    welcome_msg = config("WELCOME_MSG")
    welcome_not_joined = config("WELCOME_NOT_JOINED")
    on_join = config("ON_JOIN", cast=bool)
    on_new_msg = config("ON_NEW_MSG", cast=bool)
except:
    print("Environment vars are missing! Kindly recheck.")
    print("Bot is quiting...")
    exit()

if (apiid != None and apihash!= None and bottoken != None):
    try:
        BotsClub = TelegramClient('BotsClub', apiid, apihash).start(bot_token=bottoken)
    except Exception as e:
        print(f"ERROR!\n{str(e)}")
        print("Bot is quiting...")
        exit()
else:
    print("Environment vars are missing! Kindly recheck.")
    print("Bot is quiting...")
    exit()

channel = xchannel.replace("@", "")

# join check
async def get_user_join(id):
    ok = True
    try:
        await BotsClub(GetParticipantRequest(channel=channel, participant=id))
        ok = True
    except UserNotParticipantError:
        ok = False
    return ok


@BotsClub.on(events.ChatAction())
async def _(event):
    if on_join is False:
        return
    if event.user_joined or event.user_added:
        user = await event.get_user()
        chat = await event.get_chat()
        title = chat.title if chat.title else "this chat"
        pp = await BotsClub.get_participants(chat)
        count = len(pp)
        mention = f"[{get_display_name(user)}](tg://user?id={user.id})"
        name = user.first_name
        last = user.last_name
        if last:
            fullname = f"{name} {last}"
        else:
            fullname = name
        uu = user.username
        if uu:
            username = f"@{uu}"
        else:
            username = mention
        x = await get_user_join(user.id)
        if x is True:
            msg = welcome_msg.format(mention=mention, title=title, fullname=fullname, username=username, name=name, last=last, channel=f"@{channel}")
            butt = [Button.url("Channel", url=f"https://t.me/{channel}")]
        else:
            msg = welcome_not_joined.format(mention=mention, title=title, fullname=fullname, username=username, name=name, last=last, channel=f"@{channel}")
            butt = [Button.url("Channel", url=f"https://t.me/{channel}"), Button.inline("UnMute Me", data=f"unmute_{user.id}")]
            await BotsClub.edit_permissions(event.chat.id, user.id, until_date=None, send_messages=False)
        
        await event.reply(msg, buttons=butt)


@BotsClub.on(events.NewMessage(incoming=True))
async def mute_on_msg(event):
    if event.is_private:
        return
    if on_new_msg is False:
        return
    x = await get_user_join(event.sender_id)
    temp = await BotsClub(GetFullUserRequest(event.sender_id))
    if x is False:
        if temp.user.bot:
            return
        nm = temp.user.first_name
        try:
            await BotsClub.edit_permissions(event.chat.id, event.sender_id, until_date=None, send_messages=False)
        except Exception as e:
            print(str(e))
            return
        await event.reply(f"Hey {nm}, seems like you haven't joined our channel. Please join @{channel} and then press the button below to unmute yourself!", buttons=[[Button.url("Channel", url=f"https://t.me/{channel}")], [Button.inline("UnMute Me", data=f"unmute_{event.sender_id}")]])


@BotsClub.on(events.callbackquery.CallbackQuery(data=re.compile(b"unmute_(.*)")))
async def _(event):
    uid = int(event.data_match.group(1).decode("UTF-8"))
    if uid == event.sender_id:
        x = await get_user_join(uid)
        nm = (await BotsClub(GetFullUserRequest(uid))).user.first_name
        if x is False:
            await event.answer(f"You haven't joined @{channel} yet!", cache_time=0, alert=True)
        elif x is True:
            try:
                await BotsClub.edit_permissions(event.chat.id, uid, until_date=None, send_messages=True)
            except Exception as e:
                print(str(e))
                return
            msg = f"Welcome to {(await event.get_chat()).title}, {nm}!\nGood to see you here!"
            butt = [Button.url("Channel", url=f"https://t.me/{channel}")]
            await event.edit(msg, buttons=butt)
    else:
        await event.answer("You are an old member and can speak freely! This isn't for you!", cache_time=0, alert=True)

@BotsClub.on(events.NewMessage(pattern="/start"))
async def strt(event):
    await event.reply(f"Hi. I'm a force subscribe bot made specially for @{channel}!\n\nCheckout @BotsClubOfficial , @BotsClubDiscussion :)", buttons=[Button.url("Channel", url=f"https://t.me/{channel}"), Button.url("Creator", url="https://t.me/mkspali"), Button.url("Source Code", url="https://github.com/BotsClub/ForceSubscribeBot")])

    
print("ForceSub Bot has started.\nDo visit Channel --> @BotsClubOfficial Support Group --> @BotsClubDiscussion!")
BotsClub.run_until_disconnected()

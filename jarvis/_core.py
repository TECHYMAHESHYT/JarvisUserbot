import asyncio
import os
from datetime import datetime
from pathlib import Path

import jarvis.utils
from jarvis import bot
from jarvis.utils import *

jarvis = bot
DELETE_TIMEOUT = 5


@jarvis.on(admin_cmd(pattern="install", outgoing=True))
@jarvis.on(admin_cmd(pattern="install", allow_sudo=True))
async def install(event):
    if event.fwd_from:
        return
    if event.reply_to_msg_id:
        try:
            downloaded_file_name = (
                await event.client.download_media(  # pylint:disable=E0602
                    await event.get_reply_message(),
                    "jarvis/plugins/",  # pylint:disable=E0602
                )
            )
            if "(" not in downloaded_file_name:
                path1 = Path(downloaded_file_name)
                shortname = path1.stem
                load_module(shortname.replace(".py", ""))
                await event.reply(
                    "Installed Plugin `{}`".format(
                        os.path.basename(downloaded_file_name)
                    )
                )
            else:
                os.remove(downloaded_file_name)
                await event.reply(
                    "Errors! This plugin is already installed/pre-installed."
                )
        except Exception as e:  # pylint:disable=C0103,W0703
            await event.reply(str(e))
            os.remove(downloaded_file_name)
    await asyncio.sleep(DELETE_TIMEOUT)
    await event.delete()


@jarvis.on(admin_cmd(pattern="send (?P<shortname>\w+)$", outgoing=True))
@jarvis.on(admin_cmd(pattern="send (?P<shortname>\w+)$", allow_sudo=True))
async def send(event):
    if event.fwd_from:
        return
    message_id = event.message.id
    input_str = event.pattern_match["shortname"]
    the_plugin_file = "./jarvis/plugins/{}.py".format(input_str)
    start = datetime.now()
    await event.client.send_file(  # pylint:disable=E0602
        event.chat_id,
        the_plugin_file,
        force_document=True,
        allow_cache=False,
        reply_to=message_id,
    )
    end = datetime.now()
    time_taken_in_ms = (end - start).seconds
    await event.reply("Uploaded {} in {} seconds".format(input_str, time_taken_in_ms))
    await asyncio.sleep(DELETE_TIMEOUT)
    await event.delete()


@jarvis.on(admin_cmd(pattern="unload (?P<shortname>\w+)$", outgoing=True))
@jarvis.on(admin_cmd(pattern="unload (?P<shortname>\w+)$", allow_sudo=True))
async def unload(event):
    if event.fwd_from:
        return
    shortname = event.pattern_match["shortname"]
    try:
        remove_plugin(shortname)
        await event.reply(f"Unloaded {shortname} successfully")
    except Exception as e:
        await event.reply(
            "Successfully unload {shortname}\n{}".format(shortname, str(e))
        )


@jarvis.on(admin_cmd(pattern="load (?P<shortname>\w+)$", outgoing=True))
@jarvis.on(admin_cmd(pattern="load (?P<shortname>\w+)$", allow_sudo=True))
async def load(event):
    if event.fwd_from:
        return
    shortname = event.pattern_match["shortname"]
    try:
        try:
            remove_plugin(shortname)
        except:
            pass
        load_module(shortname)
        await event.reply(f"Successfully loaded {shortname}")
    except Exception as e:
        await event.reply(
            f"Could not load {shortname} because of the following error.\n{str(e)}"
        )

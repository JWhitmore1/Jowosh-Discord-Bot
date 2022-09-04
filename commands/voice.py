import os
import math

import lightbulb
import hikari
import lavaplayer
import asyncio

import logging
import subprocess

plugin = lightbulb.Plugin("Music")

auto_start_lavalink_server = os.environ.get("auto_start_lavalink_server", False)
if auto_start_lavalink_server:
    logging.info("Starting lavalink...")
    lavalink_process = subprocess.Popen(["java", "-Djava.io.tempdir=/home/pi/.tempjava", "-jar", "Lavalink.jar"], cwd="./server")


lavalink = lavaplayer.LavalinkClient(
    host=os.environ.get("lavalink_host", "localhost"),
    port=os.environ.get("lavalink_port", 2333),
    password=os.environ.get("lavalink_password"),
)


def shutdown_lavalink():
    logging.info("Stopping lavalink...")
    lavalink_process.send_signal(subprocess.signal.SIGINT)
    lavalink_process.communicate()


async def connect():
    logging.info("Connecting to lavalink instance")
    lavalink.set_user_id(plugin.bot.get_me().id)
    lavalink.set_event_loop(asyncio.get_event_loop())
    lavalink.connect()


@plugin.listener(hikari.StartedEvent)
async def on_start(event: hikari.StartedEvent):
    await connect()


@plugin.listener(hikari.VoiceStateUpdateEvent)
async def voice_state_update(event: hikari.VoiceStateUpdateEvent):
    await lavalink.raw_voice_state_update(event.guild_id, event.state.user_id, event.state.session_id, event.state.channel_id)


@plugin.listener(hikari.VoiceServerUpdateEvent)
async def voice_server_update(event: hikari.VoiceServerUpdateEvent):
    await lavalink.raw_voice_server_update(event.guild_id, event.endpoint, event.token)


@plugin.command()
@lightbulb.command('join', 'Get Jowosh to join your voice channel')
@lightbulb.implements(lightbulb.SlashCommand)
async def join(ctx):
    states = ctx.bot.cache.get_voice_states_view_for_guild(ctx.guild_id)
    voice_state = [state async for state in states.iterator().filter(lambda i: i.user_id == ctx.author.id)]
    if not voice_state:
        await ctx.respond("Join a voice channel to use this command")
        return
    
    channel_id = voice_state[0].channel_id
    await ctx.bot.update_voice_state(ctx.guild_id, channel_id, self_deaf=True)
    # await connect()
    await lavalink.wait_for_connection(ctx.guild_id)

    await lavalink.volume(ctx.guild_id, 50)

    await ctx.respond(f"Joined <#{channel_id}>")


@plugin.command()
@lightbulb.option('query', 'The query to search for', required=True)
@lightbulb.command('play', 'Get Jowosh to play a song/video')
@lightbulb.implements(lightbulb.SlashCommand)
async def play(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node:
        await ctx.respond('I must be in your voice channel before you can use that command')
        return

    query = ctx.options.query
    message = await ctx.respond(f"Searching for '{query}'")
    try:
        result = await lavalink.auto_search_tracks(query)
    except:
        await message.edit("Query failed")
        return
    if not result:
        await message.edit("No results found")
        return
    elif isinstance(result, lavaplayer.TrackLoadFailed):
        await message.edit("Failed to load media, try again later.\n```{}```".format(result.message))
        return
    elif isinstance(result, lavaplayer.PlayList):
        await lavalink.add_to_queue(ctx.guild_id, result.tracks, ctx.author.id)
        await message.edit(f"Added {len(result.tracks)} tracks to queue")
        return

    await lavalink.play(ctx.guild_id, result[0], ctx.author.id)
    await message.edit(f"[{result[0].title}]({result[0].uri})")


@plugin.command()
@lightbulb.command('leave', 'Get Jowosh to stop the music and leave', aliases=['stop'])
@lightbulb.implements(lightbulb.SlashCommand)
async def stop(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node:
        await ctx.respond('I must be in your voice channel before you can use that command')
        return

    # Stop music is any is playing
    try:
        await lavalink.stop(ctx.guild_id)
    except:
        pass

    await plugin.bot.update_voice_state(ctx.guild_id, None)
    await ctx.respond("Stopped the music")


@plugin.command()
@lightbulb.command(name='pause', description='Get Jowosh to pause the music')
@lightbulb.implements(lightbulb.SlashCommand)
async def pause_command(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node:
        await ctx.respond('I must be in your voice channel before you can use that command')
        return

    await lavalink.pause(ctx.guild_id, True)
    await ctx.respond("Paused the music")


@plugin.command()
@lightbulb.command(name='resume', description='Get Jowosh to resume the music')
@lightbulb.implements(lightbulb.SlashCommand)
async def resume_command(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node:
        await ctx.respond('I must be in your voice channel before you can use that command')
        return

    await lavalink.pause(ctx.guild_id, False)
    await ctx.respond("Resumed the music")


@plugin.command()
@lightbulb.app_command_permissions(perms=8)
@lightbulb.option(name='level', description='New level', type=int, min_value=0, max_value=1000, required=True)
@lightbulb.command(name="volume", description='Change the volume')
@lightbulb.implements(lightbulb.SlashCommand)
async def volume_command(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node:
        await ctx.respond('I must be in your voice channel before you can use that command')
        return

    volume = ctx.options.level
    await lavalink.volume(ctx.guild_id, volume)
    await ctx.respond(f"Set volume to {volume}%")


@plugin.command()
@lightbulb.command(name='queue', description='View the music queue')
@lightbulb.implements(lightbulb.SlashCommand)
async def queue_command(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        await ctx.respond('The queue is empty')
        return

    queue_str = ""
    for index, track in enumerate(node.queue):
        queue_str += f"{index + 1}. "
        queue_str += f"[{track.title}]({track.uri}) "
        total_seconds = round(track.length / 1000)
        minutes = math.floor(total_seconds / 60)
        seconds = str(total_seconds % 60).rjust(2, " ")
        queue_str += f"({minutes}:{seconds})"
        queue_str += "\n"

    embed = hikari.Embed(description=queue_str)
    await ctx.respond(embed=embed)


@plugin.command()
@lightbulb.command(name='now-playing', description='Get the currently playing track')
@lightbulb.implements(lightbulb.SlashCommand)
async def np_command(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        await ctx.respond('Nothing playing')
        return

    await ctx.respond(f"[{node.queue[0].title}]({node.queue[0].uri})")


@plugin.command()
@lightbulb.command(name='shuffle', description='Shuffle command')
@lightbulb.implements(lightbulb.SlashCommand)
async def shuffle_command(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        await ctx.respond('The queue is empty, nothing to shuffle')
        return

    await lavalink.shuffle(ctx.guild_id)
    await ctx.respond('Shuffled the queue')


@plugin.command()
@lightbulb.command(name='skip', description='Skip the current track')
@lightbulb.implements(lightbulb.SlashCommand)
async def skip_command(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node:
        await ctx.respond('I must be in your voice channel before you can use that command')
        return

    res = await lavalink.skip(ctx.guild_id)
    if not res:
        await ctx.respond('There is nothing to skip')
    await ctx.respond('Skipped the current track')


# Handle lavalink events
@lavalink.listen(lavaplayer.WebSocketClosedEvent)
async def web_socket_closed_event(event: lavaplayer.WebSocketClosedEvent):
    logging.error(f"Websocket error: {event.reason}")


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)

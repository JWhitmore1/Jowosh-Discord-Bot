import os
import math
import uuid

import lightbulb
import hikari
import lavaplayer
import pyttsx3
import soundfile
import asyncio

import logging
import subprocess
import atexit
import shutil
import http.server
import threading
import importlib
import time

plugin = lightbulb.Plugin("Music")

auto_start_lavalink_server = os.environ.get("auto_start_lavalink_server", False)
if auto_start_lavalink_server:
    logging.info("Starting lavalink...")
    lavalink_process = subprocess.Popen(["java", "-jar", "Lavalink.jar"], cwd="./server")

lavalink = lavaplayer.LavalinkClient(
    host=os.environ.get("lavalink_host", "localhost"),
    port=os.environ.get("lavalink_port", 2333),
    password=os.environ.get("lavalink_password"),
)

should_read_no_mic = False
tts_lock = threading.Lock()
os.mkdir("tts-audio")

tts_server_url = "http://localhost:8082"
tts_audio_server = http.server.HTTPServer(("localhost", 8082), http.server.SimpleHTTPRequestHandler)

def start_tts_audio_server():
    tts_audio_server.serve_forever()

# Serve files in tts-audio
tts_audio_server_thread = threading.Thread(target=start_tts_audio_server)
tts_audio_server_thread.start()

def shutdown_tts_audio_server():
    logging.info("Shutting down tts audio server...")
    tts_audio_server.shutdown()

def delete_tts_audio():
    logging.info("Clearing tts audio...")
    shutil.rmtree("tts-audio")

def shutdown_lavalink():
    logging.info("Stopping lavalink...")
    lavalink_process.send_signal(subprocess.signal.SIGINT)
    lavalink_process.communicate()

atexit.register(delete_tts_audio)
if auto_start_lavalink_server:
    # Shutdown lavalink when the bot is exited
    atexit.register(shutdown_lavalink)

@plugin.listener(hikari.StoppedEvent)
async def on_stop(event: hikari.StoppedEvent):
    shutdown_tts_audio_server()

@plugin.listener(hikari.StartedEvent)
async def on_start(event: hikari.StartedEvent):
    logging.info("Connecting to lavalink instance")
    lavalink.set_user_id(plugin.bot.get_me().id)
    lavalink.set_event_loop(asyncio.get_event_loop())
    lavalink.connect()

queue_to_restore: list = None
position_to_restore = None

@lavalink.listen(lavaplayer.TrackEndEvent)
async def on_track_end(event: lavaplayer.TrackEndEvent):
    global queue_to_restore
    global position_to_restore

    if not event.track.uri.startswith("http://localhost:8082/tts-audio"):
        return

    if queue_to_restore:
        for track in queue_to_restore:
            await lavalink.play(event.guild_id, track)
        queue_to_restore = None
    if position_to_restore:
        await lavalink.seek(event.guild_id, position_to_restore)
        position_to_restore = None
    if tts_lock.locked():
        tts_lock.release()

async def play_tts_audio(event: hikari.MessageCreateEvent, filename: str):
    global queue_to_restore
    global position_to_restore

    try:
        result = await lavalink.auto_search_tracks(f"{tts_server_url}/{filename}")
    except:
        await event.message.respond("Failed to load tts audio as track from tts file server")
        return
    if not result:
        await event.message.respond("Failed to play tts audio from tts file server")
        return
    elif isinstance(result, lavaplayer.TrackLoadFailed):
        await event.message.respond("Failed to load tts audio from tts file server")
        return

    # Join the sender's voice channel
    states = plugin.bot.cache.get_voice_states_view_for_guild(event.guild_id)
    voice_state = [state async for state in states.iterator().filter(lambda i: i.user_id == event.author.id)]
    if not voice_state:
        await event.message.respond("Join a voice channel to have your messages read out")
        return

    channel_id = voice_state[0].channel_id
    await plugin.bot.update_voice_state(event.guild_id, channel_id, self_deaf=True)
    await lavalink.wait_for_connection(event.guild_id)

    queue = await lavalink.queue(event.guild_id)

    saved_position = None
    if len(queue) >= 1:
        saved_position = int(queue[0].position * 1000)

    # Clear queue
    if queue:
        queue = queue.copy()
        for _ in range(len(queue)):
            await lavalink.skip(event.guild_id)
    else:
        queue = []

    # Play tts audio
    await lavalink.play(event.guild_id, result[0])
    queue_to_restore = queue
    position_to_restore = saved_position

# Read out no-mic using tts if enabled
'''
@plugin.listener(hikari.MessageCreateEvent)
async def handle_message_created(event: hikari.MessageCreateEvent):
    if not should_read_no_mic:
        return

    if plugin.bot.cache.get_guild_channel(event.channel_id).name != "testing": # TODO: change to no-mic
        return

    if event.author.id == plugin.bot.cache.get_me().id:
        return

    logging.info("TTS-ing message")

    # Generate tts audio
    filename = f"tts-audio/{uuid.uuid4().hex}"
    importlib.reload(pyttsx3) # Fix for pyttsx3 hanging after using it to generate a second file
    tts_engine = pyttsx3.init()
    tts_engine.save_to_file(event.content, f"{filename}.aiff")
    tts_engine.runAndWait()
    tts_engine.stop()

    # Convert tts audio to format supported by lavaplayer
    data, samplerate = soundfile.read(f"{filename}.aiff")
    soundfile.write(f"{filename}.wav", data, samplerate)
    logging.info("Generated audio")

    tts_lock.acquire(timeout=-1)
    logging.info("Acquired lock")
    await play_tts_audio(event, f"{filename}.wav")
'''
    # Lock is released when the audio track ends

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
    await lavalink.wait_for_connection(ctx.guild_id)

    await ctx.respond(f"Joined <#{channel_id}>")

@plugin.command()
@lightbulb.command('toggle-read-no-mic', 'Toggle whether Jowosh reads out messages in #no-mic')
@lightbulb.implements(lightbulb.SlashCommand)
async def read_no_mic(ctx):
    global should_read_no_mic

    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node and not should_read_no_mic:
        await ctx.respond('I must be in your voice channel before you can use that command')
        return

    should_read_no_mic = not should_read_no_mic
    if should_read_no_mic:
        await ctx.respond("Reading out new messages from #no-mic")
    else:
        await ctx.respond("Stopped reading messages from #no-mic")

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
    try:
        result = await lavalink.auto_search_tracks(query)
    except:
        await ctx.respond("Query failed")
        return
    if not result:
        await ctx.respond("No results found")
        return
    elif isinstance(result, lavaplayer.TrackLoadFailed):
        await ctx.respond("Failed to load media, try again later.\n```{}```".format(result.message))
        return
    elif isinstance(result, lavaplayer.PlayList):
        await lavalink.add_to_queue(ctx.guild_id, result.tracks, ctx.author.id)
        await ctx.respond(f"Added {len(result.tracks)} tracks to queue")
        return

    await lavalink.play(ctx.guild_id, result[0], ctx.author.id)
    await ctx.respond(f"[{result[0].title}]({result[0].uri})")

@plugin.command()
@lightbulb.command('leave', 'Get Jowosh to stop the music and leave')
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

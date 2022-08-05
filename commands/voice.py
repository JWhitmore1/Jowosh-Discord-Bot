import os

import lightbulb
import hikari
import lavasnek_rs

import logging


class EventHandler:
    """Events from the Lavalink server"""

    async def track_start(self, _: lavasnek_rs.Lavalink, event: lavasnek_rs.TrackStart) -> None:
        logging.info("Track started on guild: %s", event.guild_id)

    async def track_finish(self, _: lavasnek_rs.Lavalink, event: lavasnek_rs.TrackFinish) -> None:
        logging.info("Track finished on guild: %s", event.guild_id)

    async def track_exception(self, lavalink: lavasnek_rs.Lavalink, event: lavasnek_rs.TrackException) -> None:
        logging.warning("Track exception event happened on guild: %d", event.guild_id)

        # If a track was unable to be played, skip it
        skip = await lavalink.skip(event.guild_id)
        node = await lavalink.get_guild_node(event.guild_id)

        if not node:
            return

        if skip and not node.queue and not node.now_playing:
            await lavalink.stop(event.guild_id)


plugin = lightbulb.Plugin("Music")


# function for bot to join author's voice channel
async def _join(ctx):
    channel = ctx.bot.cache.get_voice_state(ctx.guild_id, ctx.member).channel_id
    guild = ctx.guild_id

    # connects the bot to voice channel
    await ctx.bot.update_voice_state(guild, channel)

    # EVERYTHING STABLE EXCEPT THiS DEMON SPAWN OF CODE FUCK YOU HIKARI AND LAVALINK AND UR MOM
    connection_info = await plugin.bot.d.lavalink.wait_for_full_connection_info_insert(guild)
    await plugin.bot.d.lavalink.create_session(connection_info)

    return channel


@plugin.listener(hikari.ShardReadyEvent)
async def start_lavalink(event):
    builder = (
        lavasnek_rs.LavalinkBuilder(event.my_user.id, os.environ.get('bot_token'))
        .set_host('127.0.0.1')
        .set_password(os.environ.get("lavalink_password"))
    )

    logging.info("Created Lavalink instance")

    builder.set_start_gateway(False)

    lava_client = await builder.build(EventHandler())

    plugin.bot.d.lavalink = lava_client


@plugin.command()
@lightbulb.command('join', 'Get Jowosh to join your voice channel')
@lightbulb.implements(lightbulb.SlashCommand)
async def join(ctx):
    channel = await _join(ctx)

    await ctx.respond(f"Joined <#{channel}>")


@plugin.command()
@lightbulb.option('query', 'The query to search for', modifier=lightbulb.OptionModifier.CONSUME_REST)
@lightbulb.command('play', 'Get Jowosh to play a song/video')
@lightbulb.implements(lightbulb.SlashCommand)
async def play(ctx):
    query = ctx.options.query
    if not query:
        await ctx.respond('Please enter a search query.')
        return

    con = plugin.bot.d.lavalink.get_guild_gateway_connection_info(ctx.guild_id)
    if not con:
        await _join(ctx)

    query_info = await plugin.bot.d.lavalink.auto_search_tracks(query)

    if not query_info.tracks:
        await ctx.respond('Could not find a video based on the query.')
        return

    await plugin.bot.d.lavalink.play(ctx.guild_id, query_info.tracks[0]).requester(ctx.author.id).queue()

    await ctx.respond('temp')


@plugin.command()
@lightbulb.command('stop', 'Get Jowosh to leave your channel')
@lightbulb.implements(lightbulb.SlashCommand)
async def stop(ctx):
    guild = ctx.guild_id

    await plugin.bot.d.lavalink.destroy(guild)

    # disconnects the bot from voice channel
    await ctx.bot.update_voice_state(guild, None)

    await plugin.bot.d.lavalink.wait_for_connection_info_remove(guild)

    await plugin.bot.d.lavalink.remove_guild_node(guild)
    await plugin.bot.d.lavalink.remove_guild_from_loops(guild)

    await ctx.respond('Disconnected.')


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)

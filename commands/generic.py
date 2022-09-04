import lightbulb
import hikari
import datetime


@lightbulb.command('invite', 'Invite Jowosh to another server')
@lightbulb.implements(lightbulb.SlashCommand)
async def invite(ctx):
    embed = hikari.Embed(title='Click here to invite Jowosh to a server', color='#63707a',
                         url='https://discord.com/api/oauth2/authorize?client_id=994903279127511040&permissions=8&scope=bot%20applications.commands')
    await ctx.respond(embed)


@lightbulb.option('amount', 'How many messages would you like deleted?', type=int, min_value=1, max_value=100)
@lightbulb.command('purge', 'Delete a number of messages')
@lightbulb.implements(lightbulb.SlashCommand)
async def purge(ctx):
    if not ctx.guild_id:
        await ctx.respond("This command can only be used in a server.")
        return

    # messages older than 14 days cannot be deleted by bots
    messages = (
        await ctx.app.rest.fetch_messages(ctx.channel_id)
            .take_until(lambda m: datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=14) > m.created_at)
            .limit(ctx.options.amount)
    )

    if messages:
        await ctx.app.rest.delete_messages(ctx.channel_id, messages)
        await ctx.respond(f"Deleted {len(messages)} messages.")
    else:
        await ctx.respond("Could not find any messages younger than 14 days!")


def load(bot: lightbulb.BotApp):
    bot.command(invite)
    bot.command(purge)


def unload(bot: lightbulb.BotApp):
    bot.remove_command(bot.get_slash_command("invite"))
    bot.remove_command(bot.get_slash_command("purge"))

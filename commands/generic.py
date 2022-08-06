import lightbulb
import hikari

generic_plugin = lightbulb.Plugin("Generic")

@lightbulb.command('invite', 'Invite Jowosh to another server')
@lightbulb.implements(lightbulb.SlashCommand)
async def invite(ctx):
    embed = hikari.Embed(title='Click here to invite Jowosh to a server', color='#63707a',
                         url='https://discord.com/api/oauth2/authorize?client_id=994903279127511040&permissions=8&scope=bot%20applications.commands')
    await ctx.respond(embed)


def load(bot: lightbulb.BotApp):
    bot.add_plugin(generic_plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(generic_plugin)

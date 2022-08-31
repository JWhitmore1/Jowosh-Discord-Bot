import lightbulb
import hikari

plugin = lightbulb.Plugin("Generic")


def convert_board_state(state):
    board = []
    for row in state:
        temp_row = []
        row_cells = row.components
        for cell in row_cells:
            temp_row.append(cell.label)
        board.append(temp_row)
    return board


def generate_board(bot, board_info):
    # placeholder board values
    board = [0, 0, 0]
    for i in range(3):
        board[i] = bot.rest.build_action_row()
        for j in range(3):
            # voodoo magic to make number (noughts and crosses)
            button = board[i].add_button(hikari.ButtonStyle.PRIMARY, f"button_nac{i}{j}")
            if board_info is None:
                button.set_label(" ")
            else:
                button.set_label(board_info[i][j])
            button.add_to_container()
    return board


@plugin.listener(hikari.InteractionCreateEvent)
async def on_component_interaction(event: hikari.InteractionCreateEvent) -> None:
    # Filter out all unwanted interactions
    if not isinstance(event.interaction, hikari.ComponentInteraction):
        return

    button_pressed = event.interaction.custom_id

    nac_buttons = []
    for i in range(3):
        for j in range(3):
            nac_buttons.append("button_nac" + str(i) + str(j))

    # checks if button event to do with nac game
    if button_pressed in nac_buttons:
        # gets the two player's discord ids
        users = event.interaction.message.content.split(" ")
        player = users[0].strip("@<>")
        opponent = users[2].strip("@<>")

        board_info = convert_board_state(event.interaction.message.components)

        row_p = int(button_pressed[-2])
        cell_p = int(button_pressed[-1])

        # what to do if the player acted
        if str(event.interaction.member.id) == player:
            # sets the cell the player pressed to be X
            board_info[row_p][cell_p] = "X"

            board = generate_board(event.interaction.app, board_info)

            await event.interaction.message.delete()
            await event.interaction.create_initial_response(
                hikari.ResponseType.MESSAGE_CREATE,
                f"<@{player}> vs. <@{opponent}>",
                components=board
            )

        # what to do if the opponent acted
        if str(event.interaction.member.id) == opponent:
            board_info[row_p][cell_p] = "O"

            board = generate_board(event.interaction.app, board_info)

            await event.interaction.message.delete()
            await event.interaction.create_initial_response(
                hikari.ResponseType.MESSAGE_CREATE,
                f"<@{player}> vs. <@{opponent}>",
                components=board
            )

        # prevents other users from chipping in
        else:
            await event.interaction.create_initial_response(
                hikari.ResponseType.MESSAGE_CREATE,
                "rage_emoji"
            )


@plugin.command()
@lightbulb.command('invite', 'Invite Jowosh to another server')
@lightbulb.implements(lightbulb.SlashCommand)
async def invite(ctx):
    embed = hikari.Embed(title='Click here to invite Jowosh to a server', color='#63707a',
                         url='https://discord.com/api/oauth2/authorize?client_id=994903279127511040&permissions=8&scope=bot%20applications.commands')
    await ctx.respond(embed)


@plugin.command()
@lightbulb.option('opponent', 'Who to battle!?', hikari.User)
@lightbulb.command('ttt', 'gaming')
@lightbulb.implements(lightbulb.SlashCommand)
async def button(ctx):
    if ctx.member.id == ctx.options.opponent.id:
        await ctx.respond("You can't play against yourself!")
    else:
        board = generate_board(ctx.bot, None)
        await ctx.respond(f"<@{ctx.member.id}> vs. <@{ctx.options.opponent.id}>", components=board, user_mentions=False)


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)

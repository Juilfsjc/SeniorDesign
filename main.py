from discord.ext.commands import bot, has_permissions
import discord.ext
from discord.ext import commands
from config import *
import asyncio
import random

# noinspection PyPackageRequirements
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents, description="Test bot for discord.py")


# Event for when the bot is ready and connected to Discord
@bot.event
async def on_ready():
    print('Bot is online and connected to Discord')
    print('------')

    # Send a heartbeat message to a specific channel when the bot comes online
    channel = bot.get_channel(1015712143145959504)
    await channel.send('Bot is online and ready!')


# Member join event notification
@bot.event
async def on_member_join(member, ctx, guild):
    guild = ctx.guild
    welcomeEmbed = discord.Embed(title=f"A new member has joined!",
                                 description=f"{member.name} has joined the {guild.name} server!",
                                 color=discord.Color.blue())

    await bot.get_channel(1015712143145959504).send(embed=welcomeEmbed)


# Define the "hello" command
@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.name}!")


# Define the "Goodbye" command
@bot.command()
async def goodbye(ctx):
    await ctx.send(f"Goodbye, {ctx.author.name}!")


@bot.command()
async def clear(ctx, amount=5):  # Specify the amount of messages to clear, default is 5
    await ctx.channel.purge(limit=amount + 1)  # +1 to include the command message itself
    await ctx.send(f'{amount} messages cleared!',
                   delete_after=5)  # Send a confirmation message and delete it after 5 seconds


# Event: on_member_join
@bot.event
async def on_member_join(member):
    # Send a welcome message
    welcome_channel = discord.utils.get(member.guild.text_channels, name='general')  # Specify the channel
    welcome_message = f"Welcome {member.mention} to the server! Please choose a role from the following options: Cincinnati, Kentucky, Indiana"
    await welcome_channel.send(welcome_message)


# Define a server info command
@bot.event
async def on_message(message, ctx):
    if message.author == bot.user:
        return

    if message.content.startswith('!serverinfo'):
        server = ctx.guild
    server_name = server.name
    server_id = server.id
    server_owner = server.owner
    server_region = server.region
    server_member_count = server.member_count

    # Create an embed to display the server information
    embed = discord.Embed(title='Server Info', color=discord.Color.green())
    embed.add_field(name='Server Name', value=server_name, inline=False)
    embed.add_field(name='Server ID', value=server_id, inline=False)
    embed.add_field(name='Server Owner', value=server_owner, inline=False)
    embed.add_field(name='Server Region', value=server_region, inline=False)
    embed.add_field(name='Member Count', value=server_member_count, inline=False)

    # Send the embed to the server info command invoker
    await ctx.send(embed=embed)


# Slow mode feature
@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Ignore messages from bots

    # Implement slow mode
    slowmode_seconds = 5  # Set the slow mode duration in seconds
    max_messages = 3  # Set the maximum number of messages allowed in the slow mode duration
    cooldown = 10  # Initialize the cooldown counter

    async for prev_message in message.channel.history(limit=max_messages, before=message):
        if prev_message.author == message.author:
            # Check if the user has sent enough messages to trigger slow mode
            cooldown += 1
            if cooldown >= max_messages:
                await message.channel.send(f'{message.author.mention}, you are sending messages too quickly. '
                                           f'Please wait {slowmode_seconds} seconds before sending another message.')
                await asyncio.sleep(slowmode_seconds)
                cooldown = 10
            break

    await bot.process_commands(message)


# Kick command
@bot.command(name="kick", pass_context=True)
@has_permissions(manage_roles=True, ban_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'{member.name} has been kicked.')


# Ban command
@bot.command(name="ban", pass_context=True)
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'{member.name} has been banned.')


# Unban command
@bot.command()
@has_permissions(ban_members=True)
async def unban(ctx, member_id):
    banned_users = await ctx.guild.bans()
    member = discord.utils.get(banned_users, user__id=int(member_id))
    await ctx.guild.unban(member.user)
    await ctx.send(f'{member.user.name} has been unbanned.')


# Define the mute and unmute commands
@bot.command()
async def mute(ctx, member: discord.Member):
    # Check if the bot has the "manage_roles" permission
    if not ctx.author.guild_permissions.manage_roles:
        await ctx.send("You don't have permission to mute members.")
        return
    if not ctx.me.guild_permissions.manage_roles:
        await ctx.send("I don't have permission to mute members.")
        return

    # Find the "Muted" role in the server
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

    # If the "Muted" role doesn't exist, create it
    if not muted_role:
        muted_role = await ctx.guild.create_role(name="Muted", reason="Mute command")
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, send_messages=False)

    # Add the "Muted" role to the member
    await member.add_roles(muted_role)
    await ctx.send(f"{member.display_name} has been muted.")


@bot.command()
async def unmute(ctx, member: discord.Member):
    # Check if the bot has the "manage_roles" permission
    if not ctx.author.guild_permissions.manage_roles:
        await ctx.send("You don't have permission to unmute members.")
        return
    if not ctx.me.guild_permissions.manage_roles:
        await ctx.send("I don't have permission to unmute members.")
        return

    # Find the "Muted" role in the server
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

    # If the "Muted" role doesn't exist, send an error message
    if not muted_role:
        await ctx.send("The 'Muted' role doesn't exist.")
        return

    # Remove the "Muted" role from the member
    await member.remove_roles(muted_role)
    await ctx.send(f"{member.display_name} has been unmuted.")


# Tictactoe
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('!tictactoe'):
        player1 = message.author
        player2 = message.mentions[0] if message.mentions else None

        if not player2:
            await message.channel.send('Please mention another player to play with.')
            return

        if player1 == player2:
            await message.channel.send('You cannot play against yourself!')
            return

        board = [':white_large_square:', ':white_large_square:', ':white_large_square:',
                 ':white_large_square:', ':white_large_square:', ':white_large_square:',
                 ':white_large_square:', ':white_large_square:', ':white_large_square:']
        winner = None
        turn = player1
        game_over = False

        while not game_over:
            if turn == player1:
                sign = ':regional_indicator_x:'
            else:
                sign = ':o:'

            await message.channel.send(f'{turn.mention}\'s turn. Choose a position to place {sign} in.')

            def check(m):
                return m.author == turn and m.content.isdigit() and int(m.content) in range(1, 10) and board[
                    int(m.content) - 1] == ':white_large_square:'

            try:
                msg = await bot.wait_for('message', check=check, timeout=30.0)
            except asyncio.TimeoutError:
                await message.channel.send(f'{turn.mention} took too long to respond. Game ended.')
                game_over = True
                break

            position = int(msg.content) - 1
            board[position] = sign

            await print_board(message.channel, board)

            if check_win(board):
                winner = turn
                game_over = True
            elif check_draw(board):
                game_over = True
            else:
                turn = player2 if turn == player1 else player1

        if winner:
            await message.channel.send(f'Congratulations, {winner.mention}! You won!')
        else:
            await message.channel.send('It\'s a draw!')


async def print_board(channel, board):
    line = ''
    for i, sign in enumerate(board):
        if i % 3 == 2:
            line += sign + '\n'
        else:
            line += sign
    await channel.send(line)


def check_win(board):
    return (board[0] == board[1] == board[2] != ':white_large_square:' or
            board[3] == board[4] == board[5] != ':white_large_square:' or
            board[6] == board[7] == board[8] != ':white_large_square:' or
            board[0] == board[3] == board[6] != ':white_large_square:' or
            board[1] == board[4] == board[7] != ':white_large_square:' or
            board[2] == board[5] == board[8] != ':white_large_square:' or
            board[0] == board[4] == board[8] != ':white_large_square:' or
            board[2] == board[4] == board[6] != ':white_large_square:')


def check_draw(board):
    return all([sign != ':white_large_square:' for sign in board])

 # Define a class for the blackjack game


class Blackjack:
    def __init__(self, ctx):
        self.ctx = ctx
        self.deck = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 4
        self.player_hand = []
        self.dealer_hand = []
        self.player_score = 0
        self.dealer_score = 0

    def deal(self):
        for _ in range(2):
            card = random.choice(self.deck)
            self.player_hand.append(card)
            self.deck.remove(card)
            card = random.choice(self.deck)
            self.dealer_hand.append(card)
            self.deck.remove(card)

    def hit(self, hand):
        card = random.choice(self.deck)
        hand.append(card)
        self.deck.remove(card)

    def calculate_score(self, hand):
        score = 0
        num_aces = 0
        for card in hand:
            if card == 'A':
                num_aces += 1
            elif card in ['J', 'Q', 'K']:
                score += 10
            else:
                score += int(card)
        while num_aces > 0 and score > 21:
            score -= 10
            num_aces -= 1
        return score

    async def play(self):
        self.deal()
        await self.ctx.send(f"**Your hand:** {', '.join(self.player_hand)}")
        await self.ctx.send(f"**Dealer's up card:** {self.dealer_hand[0]}")
        while True:
            await self.ctx.send("Do you want to hit or stand? (Type `hit` or `stand`)")
            try:
                msg = await bot.wait_for('message', check=lambda message: message.author == self.ctx.author,
                                         timeout=30)
                if msg.content.lower() == 'hit':
                    self.hit(self.player_hand)
                    await self.ctx.send(f"**Your hand:** {', '.join(self.player_hand)}")
                    self.player_score = self.calculate_score(self.player_hand)
                    if self.player_score > 21:
                        await self.ctx.send("Bust! You lost!")
                        break
                elif msg.content.lower() == 'stand':
                    while self.calculate_score(self.dealer_hand) < 17:
                        self.hit(self.dealer_hand)
                    self.dealer_score = self.calculate_score(self.dealer_hand)
                    await self.ctx.send(f"**Dealer's hand:** {', '.join(self.dealer_hand)}")
                    if self.dealer_score > 21:
                        await self.ctx.send("Dealer busts! You win!")
                    elif self.dealer_score < self.player_score:
                        await self.ctx.send("You win!")
                    elif self.dealer_score > self.player_score:
                        await self.ctx.send("You lost!")
                    else:
                        await self.ctx.send("It's a tie!")
                    break
                else:
                    await self.ctx.send("Invalid choice! Type `hit` or `stand`.")
            except asyncio.TimeoutError:
                await self.ctx.send("Timeout! You took too long to respond.")
                break


# Define a command for playing blackjack

@bot.command()
async def blackjack(ctx):
    game = Blackjack(ctx)
    await game.play()


# Define the slots emojis
SLOTS_EMOJIS = ['🍇', '🍊', '🍒', '🍓', '🍌', '🍏', '🍆']


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith('!slots'):
        # Spin the slots
        slots_result = spin_slots()

        # Send the slots result
        await message.channel.send(slots_result)


def spin_slots():
    # Generate a list of random slots emojis
    slots = [random.choice(SLOTS_EMOJIS) for _ in range(3)]

    # Check for a winning combination
    if slots[0] == slots[1] and slots[1] == slots[2]:
        # If all three emojis are the same, it's a win
        return f'{slots[0]} {slots[1]} {slots[2]}\nYou win!'
    else:
        # Otherwise, it's a loss
        return f'{slots[0]} {slots[1]} {slots[2]}\nYou lose.'


@bot.command()
async def roulette(ctx, bet: int, guess: str):
    # Convert guess to lowercase for case-insensitive comparison
    guess = guess.lower()
    valid_guesses = ['red', 'black', 'green']

    if guess not in valid_guesses:
        await ctx.send('Invalid guess. Please choose from red, black, or green.')
        return

    if bet <= 0:
        await ctx.send('Invalid bet. Please place a bet greater than 0.')
        return

    # Simulate the roulette spin
    spin = random.choice(valid_guesses)

    if spin == 'green':
        win_amount = bet * 14
        if guess == 'green':
            await ctx.send(f'Congratulations! The spin is **{spin}**. You win {win_amount} credits!')
        else:
            await ctx.send(f'Unlucky! The spin is **{spin}**. You lose {bet} credits.')
    else:
        win_amount = bet * 2
        if guess == spin:
            await ctx.send(f'Congratulations! The spin is **{spin}**. You win {win_amount} credits!')
        else:
            await ctx.send(f'Unlucky! The spin is **{spin}**. You lose {bet} credits.')


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith('!rps'):
        # Split the message into two parts: command and opponent's choice
        parts = message.content.split()
        if len(parts) != 2:
            await message.channel.send('Usage: !rps <rock/paper/scissors>')
            return

        # Store the user's choice and generate a random choice for the opponent
        user_choice = parts[1].lower()
        choices = ['rock', 'paper', 'scissors']
        bot_choice = random.choice(choices)

        # Check if the user's choice is valid
        if user_choice not in choices:
            await message.channel.send('Invalid choice. Choose either rock, paper, or scissors.')
            return

        # Determine the winner and send the result to the channel
        if user_choice == bot_choice:
            await message.channel.send(f'Tie! Both chose {user_choice}.')
        elif (user_choice == 'rock' and bot_choice == 'scissors') or \
                (user_choice == 'paper' and bot_choice == 'rock') or \
                (user_choice == 'scissors' and bot_choice == 'paper'):
            await message.channel.send(f'You won! You chose {user_choice} and the bot chose {bot_choice}.')
        else:
            await message.channel.send(f'You lost! You chose {user_choice} and the bot chose {bot_choice}.')


bot.run(TOKEN, reconnect=True)

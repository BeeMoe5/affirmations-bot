import ast
import asyncio
import traceback
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import uvloop


TOKEN = "this string is reassigned later as this is a placeholder"

def load_secrets():
    global TOKEN
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")

    
intents = discord.Intents.all()
bot = commands.AutoShardedBot(command_prefix=commands.when_mentioned_or('a!'), intents=intents, help_command=commands.MinimalHelpCommand())


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

    for f in os.listdir("src/cogs"):
        if f.endswith(".py"):
            await bot.load_extension(f"cogs.{f[:-3]}")
            print(f"Loaded extension {f[:-3]}")

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="a!help"))



@commands.is_owner()
@bot.command()
async def guilds(ctx: commands.Context):
    e = discord.Embed(title="Guilds", color=discord.Color.green())
    e.insert_field_at(1, name="Loading...", value="This may take a few seconds...")
    msg = await ctx.send(embed=e)
    index = 0
    paginator_loop = True

    def reaction_check(reaction, user):
        emojis = ["⬅️", "➡️", "❌", "#️⃣"]
        return user == ctx.author and str(reaction.emoji) in emojis and reaction.message.id == msg.id
    
    def message_check(message):
        return message.author == ctx.author and message.channel == ctx.channel and message.content.isdigit() and 0 < int(message.content) < len(bot.guilds)
    
    await msg.add_reaction("⬅️")
    await msg.add_reaction("➡️")
    await msg.add_reaction("❌")
    await msg.add_reaction("#️⃣")
    # then set initial field
    e.set_field_at(0, name=f"Page {index + 1}/{len(bot.guilds)}", value=bot.guilds[index].name)

    await msg.edit(embed=e)

    while paginator_loop:  # heres a hashtag emoji unicode: 
        try:
            reaction, user = await bot.wait_for("reaction_add", check=reaction_check, timeout=30.0)
        except asyncio.TimeoutError:
            await msg.clear_reactions()
            paginator_loop = False
            break
        if reaction.emoji == "❌":
            paginator_loop = False
            break
        elif reaction.emoji == "⬅️":
            if index == 0:

                # ignore and remove reaction
                await reaction.remove(user)
            else:
                index -= 1
                await reaction.remove(user)
        elif reaction.emoji == "➡️":
            if index == len(bot.guilds) - 1:
                # ignore and remove reaction
                await reaction.remove(user)
            else:
                index += 1
                await reaction.remove(user)

        elif reaction.emoji == "#️⃣":
            await reaction.remove(user)

            # send new message
            m = await ctx.send("Please enter a number between 1 and " + str(len(bot.guilds)) + ".")
            m2 = await bot.wait_for("message", check=message_check, timeout=15.0)
            index = int(m2.content) - 1
            await m.delete()
            await m2.delete()
        
        e.set_field_at(0, name=f"Page {index + 1}/{len(bot.guilds)}", value=bot.guilds[index].name)
        await msg.edit(embed=e)


def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


@bot.command(name="eval", aliases=["e"])
async def eval_(ctx, *, code):
    """
    Literally runs code
    """
    fn_name = "_eval_expr"

    code = code.strip("` ")

    # add a layer of indentation
    code = "\n".join(f"    {i}" for i in code.splitlines())

    # wrap in async def body
    body = f"async def {fn_name}():\n{code}"

    parsed = ast.parse(body)
    body = parsed.body[0].body

    insert_returns(body)

    env = {
        'bot': ctx.bot,
        'discord': discord,
        'commands': commands,
        'ctx': ctx,
        'message': ctx.message,
        'guild': ctx.guild,
        'channel': ctx.channel,
        'author': ctx.author,
        '__import__': __import__
    }

    try:
        exec(compile(parsed, filename="<ast>", mode="exec"), env)

        result = (await eval(f"{fn_name}()", env))
        if result is not None:
            await ctx.send(result)
        await ctx.message.add_reaction('✅')
    except Exception as e:
        await ctx.send(f"```py\n{traceback.format_exc()}\n```")
        await ctx.message.add_reaction('❌')


if __name__ == '__main__':
    load_secrets()
    uvloop.install()
    bot.run(TOKEN)

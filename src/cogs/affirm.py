import json
import discord
from discord.ext import commands
import asyncio
import datetime
import random
from discord.utils import sleep_until
import os


class Affirm(commands.Cog):
    TEXT_AFFIRMATION: int = 1  # text based affirmations
    VOICE_AFFIRMATION: int = 2  # music based affirmations
    IMAGE_AFFIRMATION: int = 3  # don't completely have an idea for this, but it could be a GIF or image based affirmations

    TEXT_CHANNEL_ID: int = 633365830108708894
    VOICE_CHANNEL_ID: int = 580695981922975744

    TEXT_AFFIRMATIONS: list[str]
    VOICE_AFFIRMATIONS: list[str] = []

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.last_affirmation: datetime.datetime = None
        self.scheduled_datetimes: list[datetime.datetime] = []

        self.load_affirmations()

        self.affirmation_task: asyncio.Task = self.bot.loop.create_task(self._affirmation_task())  # loop is the bot's event loop
        # if the task has any errors, it will be logged to the console
        self.affirmation_task.add_done_callback(self.affirmation_error)

    def load_affirmations(self):
        # load text affirmations
        with open("./src/assets/affirmations.json", "r") as f:
            data = json.load(f)  # its just a list of strings
            self.TEXT_AFFIRMATIONS = data
        
        # load voice affirmations
        for file in os.listdir("./src/assets/sounds"):
            if file.endswith(".mp3"):
                file = f"./src/assets/sounds/{file}"
                self.VOICE_AFFIRMATIONS.append(file)

    def affirmation_error(self, task: asyncio.Task):
        # check if the task has any errors, if so, print them to the console
        if task.exception():
            task.print_stack()

    async def _affirmation_task(self):
        """
        The main loop that runs the affirmations.
        """
        while self.bot.is_ready() and not self.bot.is_closed() and not self.affirmation_task.cancelled():
            await self.before_affirmation()

            print(f"affirmation_task: {self.scheduled_datetimes=}")

            self.last_affirmation = datetime.datetime.now().astimezone()

            random_type = random.randint(1, 2)  # change max to 3 when image affirmations are added

            if random_type == self.TEXT_AFFIRMATION:
                await self.text_affirmation()
            elif random_type == self.VOICE_AFFIRMATION:
                await self.voice_affirmation()
            elif random_type == self.IMAGE_AFFIRMATION:
                await self.image_affirmation()

            await self.after_affirmation()

    async def before_affirmation(self):
        """
        Schedules the next affirmation time before the loop starts.

        This function is called as a before_loop hook on the affirmation task.
        """

        self.schedule_next_affirmation()
        await sleep_until(self.scheduled_datetimes[0])

    async def after_affirmation(self):
        # clean up the schedules
        del self.scheduled_datetimes[0]

    def schedule_next_affirmation(self):
        """
        Appends the next affirmation time to the schedule.
        """
        print("schedule_next_affirmation before", self.scheduled_datetimes)
        dt = self.get_random_datetime()
        self.scheduled_datetimes.append(dt)        

        print(f"Next affirmation scheduled for {dt.strftime('%A %I:%M:%S %p')}")
        print("schedule_next_affirmation after", self.scheduled_datetimes)

    def get_random_datetime(self) -> datetime.datetime:
        """
        Returns a random datetime object between 9am and 10pm the next day.
        If self.last_affirmation is not None, it will return a datetime object
        that is a day after self.last_affirmation.
        """
        current_datetime = datetime.datetime.now().astimezone()

        min_hour, max_hour = 9, 22
        min_minute, min_second = 0, 0

        if self.last_affirmation is not None:
            # there is a previous affirmation, and its safe to assume it was between 9am and 10pm therefore we can assume the current time is between 9am and 10pm, so increment to the next day
            random_date = current_datetime + datetime.timedelta(days=1)
        else:
            random_date = current_datetime

            # if the current hour is between 9am and 10pm, then set the min_hour to the current hour
            if min_hour <= random_date.hour <= max_hour:
                min_hour = random_date.hour

            min_minute = random_date.minute
            min_second = random_date.second
            print(f"{min_hour=}, {min_minute=}, {min_second=} {random_date.hour=}")

        random_hour = random.randint(min_hour, max_hour)
        random_minute = random.randint(min_minute, 59)
        random_second = random.randint(min_second, 59)

        if random_hour == max_hour:
            random_minute = random_second = 0

        return random_date.replace(hour=random_hour, minute=random_minute, second=random_second)
    
    async def text_affirmation(self):
        """
        Sends a random text affirmation to the channel.
        """
        channel = self.bot.get_channel(self.TEXT_CHANNEL_ID)
        role = channel.guild.get_role(550581727903481867)
        random_affirmation = random.choice(self.TEXT_AFFIRMATIONS)
        timestamp = datetime.datetime.now().astimezone()
        embed = discord.Embed(title="Affirmation of the day!", description=random_affirmation, color=discord.Color.green(), timestamp=timestamp)

        await channel.send(content=role.mention, embed=embed)

    async def voice_affirmation(self):
        voice_channel = self.bot.get_channel(self.VOICE_CHANNEL_ID)
        text_channel = self.bot.get_channel(self.TEXT_CHANNEL_ID)
        role = text_channel.guild.get_role(550581727903481867)
        random_song = random.choice(self.VOICE_AFFIRMATIONS)
        player = await voice_channel.connect()
        timestamp = datetime.datetime.now().astimezone()
        after_message = text_channel.send("The song is over, but don't let that stop you from " + random.choice(["having a good day", "being happy", "being content", "being positive", "loving yourself"]))

        embed = discord.Embed(title="Affirmation of the day!", description="Join the VC to hear an affirming song", color=discord.Color.green(), timestamp=timestamp)

        await text_channel.send(content=role.mention, embed=embed)


        async def after_coro():
            await after_message
            await player.disconnect()

        def after_playing(error):
            if error:
                print(error)
            player.stop()
            asyncio.run_coroutine_threadsafe(after_coro(), self.bot.loop)
        player.play(discord.FFmpegPCMAudio(random_song), after=after_playing)


async def setup(bot):
    await bot.add_cog(Affirm(bot))

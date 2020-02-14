import asyncio
import discord
import twitter
import time
import yaml
from datetime import datetime
from discord.ext import commands, tasks
from os.path import abspath

with open(abspath('./config/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)

with open(abspath(config['roles_file']), 'r') as rolesFile:
    roles = yaml.safe_load(configFile)

twitterAPI = twitter.Api(consumer_key=config['twitterAPIKey'],
                         consumer_secret=config['twitterAPISecret'],
                         access_token_key=config['twitterAccessToken'],
                         access_token_secret=config['twitterAccessSecret'])


async def youtube_check(self):
    while self.bot.is_ready():
        await asyncio.sleep(300)


class SocialMedia(commands.Cog, name="Social Media Feed"):
    def __init__(self, bot):
        self.bot= bot
        self._batch = []

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author != self.bot.user:
            if message.webhook_id is not None:
                for feed in roles['webhooks_feed']:
                    if message.channel.id == feed['channel']:
                        guild = self.bot.get_guild(config['server_ID'])
                        pingRole = guild.get_role(feed['id'])
                        await pingRole.edit(reason="Social Media Feed", mentionable=True)
                        await message.channel.send(f"{pingRole.mention}")
                        await pingRole.edit(reason="Social Media Feed", mentionable=False)

            else:
                for feed in roles['other_feed']:
                    if message.channel.id == feed['channel']:
                        guild = self.bot.get_guild(config['server_ID'])
                        pingRole = guild.get_role(feed['id'])
                        await pingRole.edit(reason="Social Media Feed", mentionable=True)
                        await message.channel.send(f"{pingRole.mention}")
                        await pingRole.edit(reason="Social Media Feed", mentionable=False)
        
    @commands.Cog.listener()
    async def on_disconnect(self):
        self.twitter_check.cancel() # pylint: disable=no-member

    @commands.Cog.listener()
    async def on_ready(self):
        self.twitter_check.start() # pylint: disable=no-member
    
    @tasks.loop(seconds=15.0, reconnect=True)
    async def twitter_check(self):
        try:
            tweets = twitterAPI.GetUserTimeline(screen_name=config['twitterFeedUser'], exclude_replies=False, count=10)
            for tweet in tweets:
                if int(tweet.created_at_in_seconds) >= (int(time.time()) - 15):
                    embedTweet = discord.Embed(title=f"New Tweet from {config['twitterFeedUser']}", colour=0x753543)
                    postedBy = tweet.user.profile_image_url
                    embedTweet.set_thumbnail(url=postedBy)
                    embedTweet.add_field(name=f"http://twitter.com/{config['twitterFeedUser']}/status/{tweet.id}", value=tweet.text)
                    datePosted = datetime.utcfromtimestamp(int(tweet.created_at_in_seconds)).strftime("%m/%d/%Y, %H:%M:%S") + " GMT"
                    embedTweet.set_footer(text=datePosted, icon_url="http://x2110311x.me/twitter.png")
                    twitterChan = self.bot.get_channel(config['twitter_channel'])
                    await twitterChan.send(embed=embedTweet)
                    guild = self.bot.get_guild(config['server_ID'])
                    pingRole = guild.get_role(roles['twitter_Role'])
                    await pingRole.edit(reason="Social Media Feed", mentionable=True)
                    await twitterChan.send(f"{pingRole.mention}")
                    await pingRole.edit(reason="Social Media Feed", mentionable=False)
        except:
            chanTest = self.bot.get_channel(config['testing_Channel'])
            await chanTest.send("Error handling Tweets")
        finally:
            guild = self.bot.get_guild(config['server_ID'])
            pingRole = guild.get_role(roles['twitter_Role'])
            await pingRole.edit(reason="Social Media Feed", mentionable=False)
            
    @twitter_check.before_loop
    async def before_twitter_check(self):
        await self.bot.wait_until_ready()
        chanTest = self.bot.get_channel(config['testing_Channel'])
        await chanTest.send("Twitter Feed Started")

def setup(bot):
    bot.add_cog(SocialMedia(bot))

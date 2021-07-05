
import discord
from discord.ext import commands

import asyncio
import itertools
import sys
import traceback
from async_timeout import timeout
from functools import partial
from youtube_dl import YoutubeDL


ytdlopts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # ipv6 addresses cause issues sometimes
    
'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '8',
    }],
    
    'skip_download':True,
    
}
timeestamp=0
ffmpegopts = {
    'before_options': '-vn -ss {timeestamp} -nostdin -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5' ,
    'options': '-vn'
}

ytdl = YoutubeDL(ytdlopts)


class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""


class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')
        self.webpage_url = data.get('webpage_url')

        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md

    def __getitem__(self, item: str):
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=False)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        

        global ffmpegopts
        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

        return cls(discord.FFmpegPCMAudio(source, **ffmpegopts), data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url'], **ffmpegopts), data=data, requester=requester)


class MusicPlayer:

    __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume','que','embed','nowp')

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None  # Now playing message
        self.que=None
        self.embed=None
        self.volume = 1.0
        self.current = None
        self.nowp=None

        ctx.bot.loop.create_task(self.player_loop(ctx))

    async def showw(self,ctx):
        try:
        # Grab up to 5 entries from the queue...
            vc = ctx.voice_client

            if not vc or not vc.is_connected():
                return #await ctx.send('I am not currently connected to voice!',delete_after=10)
            
            upcoming = list(itertools.islice(self.queue._queue, 0, 999999))

            fmt = '\n'.join(f'{_["title"]}' for _ in upcoming)
            #self.embed = discord.Embed(title=f'Upcoming - Next {len(upcoming)}', description=fmt)
            #self.embed=await self._channel.send(f'Upcoming - Next {len(upcoming)}\n{fmt}')
            try:
                await self.que.delete()
                await self.np.delete()
            except Exception as e:
                print("EEE",e)

            self.que=await self._channel.send(f'Upcoming - Next {len(upcoming)}\n{fmt}')
            self.np = await self._channel.send(f'Requested by @{vc.source.requester} {vc.source.webpage_url}')
        except Exception as e:
            await self._channel.send(f'NO songs in queue: {e}',delete_after=10)

        

    async def player_loop(self,ctx):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                async with timeout(999999999):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self._guild)

            if not isinstance(source, YTDLSource):
                # Source was probably a stream (not downloaded)
                # So we should regather to prevent stream expiration
                try:
                    self.nowp=source
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f'There was an error processing your song.\n'
                                             f'```css\n[{e}]\n```',delete_after=10)
                    continue

            source.volume = self.volume
            self.current = source

            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            
            await self.showw(ctx)
            await self.next.wait()

            source.cleanup()
            self.current = None

            try:
                await self.que.delete()
                await self.np.delete()
            except discord.HTTPException:
                pass

    def destroy(self, guild):
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Music(commands.Cog):

    __slots__ = ('bot', 'players')

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __local_check(self, ctx):
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command can not be used in Private Messages.',delete_after=10)
            except discord.HTTPException:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            await ctx.send('Error connecting to Voice Channel. '
                           'Please make sure you are in a valid channel or provide me with one',delete_after=10)

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def get_player(self, ctx):
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    @commands.command(name='connect', aliases=['join'])
    async def connect_(self, ctx, *, channel: discord.VoiceChannel=None):
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise InvalidVoiceChannel('No channel to join. Please either specify a valid channel or join one.')

        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Moving to channel: <{channel}> timed out.',delete_after=10)
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Connecting to channel: <{channel}> timed out.',delete_after=10)

        await ctx.send(f'Connected to: **{channel}**', delete_after=10)
        await ctx.message.delete()

    @commands.command(name='play', aliases=['sing','p'])
    async def play_(self, ctx, *, search: str):
        global timeestamp
        timeestamp=0
        await ctx.trigger_typing()

        vc = ctx.voice_client

        if not vc:
            await ctx.invoke(self.connect_)

        player = self.get_player(ctx)

        source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop, download=False)

        await player.queue.put(source)
        await self.now_playing_(ctx)
        try:
            await ctx.message.delete()
        except Exception as e:
            print(e)

    @commands.command(name='pause')
    async def pause_(self, ctx):
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            return #await ctx.send('I am not currently playing anything!', delete_after=10)
        elif vc.is_paused():
            return

        vc.pause()
        await ctx.send(f'**`{ctx.author}`**: Paused the song!',delete_after=10)
        await ctx.message.delete()

    @commands.command(name='resume')
    async def resume_(self, ctx):
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return #await ctx.send('I am not currently playing anything!', delete_after=10)
        elif not vc.is_paused():
            return

        vc.resume()
        await ctx.send(f'**`{ctx.author}`**: Resumed the song!',delete_after=10)
        await ctx.message.delete()

    @commands.command(name='skip')
    async def skip_(self, ctx):
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return #await ctx.send('I am not currently playing anything!', delete_after=10)

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return
        try:
            player=self.get_player(ctx)
            await player.np.delete()
            await player.que.delete()
            await ctx.message.delete()
        except Exception as e:
            print("skip",e)
        vc.stop()
        await ctx.send(f'**`{ctx.author}`**: Skipped the song!',delete_after=10)

    @commands.command(name='queue', aliases=['q', 'playlist'])
    async def queue_info(self, ctx):
        player = self.get_player(ctx)
        await player.showw(ctx)
        await ctx.message.delete()


    @commands.command(name='now_playing', aliases=['np', 'current', 'currentsong', 'playing'])
    async def now_playing_(self, ctx):

        player = self.get_player(ctx)
        if not player.current:
            return #await ctx.send('I am not currently playing anything!',delete_after=10)
        await player.showw(ctx)
        try:
            await ctx.message.delete()
        except Exception as e:
            print(e)

    @commands.command(name='volume', aliases=['vol'])
    async def change_volume(self, ctx, *, vol: float):
        
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return #await ctx.send('I am not currently connected to voice!', delete_after=10)

        if not 0 < vol < 101:
            return await ctx.send('Please enter a value between 1 and 100.',delete_after=10)

        player = self.get_player(ctx)

        if vc.source:
            vc.source.volume = vol / 100

        player.volume = vol / 100
        await ctx.send(f'**`{ctx.author}`**: Set the volume to **{vol}%**',delete_after=10)
        await ctx.message.delete()

    @commands.command(name='stop')
    async def stop_(self, ctx):
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return #await ctx.send('I am not currently playing anything!', delete_after=10)
        try:
            player=self.get_player(ctx)
            await player.np.delete()
            await player.que.delete()
            await ctx.message.delete()
        except Exception as e:
            print("stop",e)

        await self.cleanup(ctx.guild)
    @commands.command(name='seek')
    async def seek_(self,ctx, *, search: int)
        vc=ctx.voice_client
        if not vc or not vc.is_connected():
            return #await ctx.send('I am not currently playing anything!', delete_after=10)
        try:
            player=self.get_player(ctx)
            await ctx.message.delete()
            vc.stop()
        except Exception as e:
            print("stop",e)
        timeestamp=search
        source=player.nowp
        await ctx.trigger_typing()
        
        await player.now_playing_(ctx)
        try:
            await ctx.message.delete()
        except Exception as e:
            print(e)
            
        await player.bot.wait_until_ready()

        while not player.bot.is_closed():
            player.next.clear()


            if not isinstance(source, YTDLSource):
                # Source was probably a stream (not downloaded)
                # So we should regather to prevent stream expiration
                try:
                    player.nowp=source
                    source = await YTDLSource.regather_stream(source, loop=player.bot.loop)
                except Exception as e:
                    await player._channel.send(f'There was an error processing your song.\n'
                                             f'```css\n[{e}]\n```',delete_after=10)
                    continue

            source.volume = player.volume
            player.current = source

            player._guild.voice_client.play(source, after=lambda _: player.bot.loop.call_soon_threadsafe(player.next.set))
            
            await player.next.wait()

            source.cleanup()
            player.current = None

            try:
                await player.que.delete()
                await player.np.delete()
            except discord.HTTPException:
                pass

            
            

def setup(bot):
    bot.add_cog(Music(bot))

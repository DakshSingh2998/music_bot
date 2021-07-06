import discord
import os
from os import environ
from keep_alive import keep_alive
from discord.ext import commands, tasks
import pickle
import boto3
#Daksh
import time

temp_ctx=None
auto_now=0
client=commands.Bot(command_prefix=';')
status="♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥"
@client.event
async def on_ready():
  print("Ready Daksh. Hey ",client.user)
  await client.change_presence(activity=discord.Game(status))
  await load()
  sav.start()
  
async def load():
    try:
      access_key=os.environ.get('access_key')
      access_secret=os.environ.get('access_secret')
      bucket_name=os.environ.get('bucket_name')
      client_s3=boto3.client(
      's3',
      aws_access_key_id=access_key,
      aws_secret_access_key=access_secret
      )
      
      client_s3.download_file(bucket_name,'ctxs',os.path.join('./storage/','ctxs'))
      #
      dbfile = open('./storage/ctxs', 'rb')     
      ctxs = pickle.load(dbfile)
      print(ctxs)
      dbfile.close()
      for x in ctxs:
          """
          if os.path.exists(f'./storage/channelid{x}'):
              os.remove(f'./storage/channelid{x}')
          if os.path.exists(f'./storage/nowp{x}'):
              os.remove(f'./storage/nowp{x}')
          if os.path.exists(f'./storage/searchqueue{x}'):
              os.remove(f'./storage/searchqueue{x}')
          """
          client_s3.download_file(bucket_name,f'channelid{x}',os.path.join('./storage/',f'channelid{x}'))
          client_s3.download_file(bucket_name,f'nowp{x}',os.path.join('./storage/',f'nowp{x}'))
          client_s3.download_file(bucket_name,f'searchqueue{x}',os.path.join('./storage/',f'searchqueue{x}'))
          
      for x in ctxs:
          dbfile=open(f'./storage/channelid{x}', 'rb')
          channelid=pickle.load(dbfile)
          dbfile.close()

          dbfile=open(f'./storage/nowp{x}', 'rb')
          nowp=pickle.load(dbfile)
          dbfile.close()

          searchqueue=[]
          dbfile=open(f'./storage/searchqueue{x}', 'rb')
          searchqueue=pickle.load(dbfile)
          dbfile.close()
          
          channel = client.get_channel(int(channelid))
          vc_channel = client.get_channel(824253644718997514)
          await vc_channel.connect()
          print(channel)
          await channel.send(f'^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
          await channel.send(f';play {str(nowp)}')
          await asyncio.sleep(5)
          size=len(searchqueue)
          print('sizee',size)
          j=1
          for que in searchqueue:
              j=j+1
              await channel.send(f';play {str(que)}')
              await asyncio.sleep(5)
    except Exception as e:
      print(e)



import discord
from discord.ext import commands

import asyncio
import itertools
import sys
import traceback
from async_timeout import timeout
from functools import partial
from youtube_dl import YoutubeDL
import os
import boto3
import pickle


timeestamp=0
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
    'extract_audio':True,
    'source_address': '0.0.0.0',# ipv6 addresses cause issues sometimes
    
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '4',
    }],
    
    'skip_download':True,
    
    
    
}
sflag=0



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

        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
            global timeestamp
        
        ffmpegopts = {
        'before_options': f'-vn -nostdin -ss {timeestamp} -reconnect 1 -reconnect_at_eof 1 -reconnect_streamed 1 -reconnect_delay_max 4000 -ab 64' ,
        'options': f'-vn'
        }

        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}


        return cls(discord.FFmpegPCMAudio(source,**ffmpegopts), data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)
        global timeestamp
        ffmpegopts = {
        'before_options': f'-vn -nostdin -ss {timeestamp} -reconnect 1 -reconnect_at_eof 1 -reconnect_streamed 1 -reconnect_delay_max 4000 -ab 64' ,
        'options': f'-vn'
        }

        return cls(discord.FFmpegPCMAudio(data['url'],**ffmpegopts), data=data, requester=requester)


class MusicPlayer:

    __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume','que','embed','nowp','searchqueue','cttx')

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog
        self.cttx=ctx

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None  # Now playing message
        self.que=None
        self.embed=None
        self.volume = 1.0
        self.current = None
        self.nowp=None
        self.searchqueue=asyncio.Queue()

        ctx.bot.loop.create_task(self.player_loop(ctx))

    """def __getstate__(self):

        # this method is called when you are
        # going to pickle the class, to know what to pickle
        state = self.__dict__.copy()
        
        # don't pickle the parameter fun. otherwise will raise 
        # AttributeError: Can't pickle local object 'Process.__init__.<locals>.<lambda>'
        del state['next']
        return state
    """
    async def pk(self,ct,ctx):
        try:
        #dbfile = open(f'./storage/ctx{ct}', 'ab')
        #source, destination
        
        #pickle.dump(self.cttx, dbfile)                     
        #dbfile.close()
            dbfile = open(f'./storage/searchqueue{ct}', 'wb')
        # source, destination
        
            temp=[]
            tsize=self.searchqueue.qsize()
            while(tsize>0):
                t=await self.searchqueue.get()
                temp.append(str(t))
                tsize=tsize-1
            pickle.dump(temp, dbfile)                   
            dbfile.close()
        
            dbfile = open(f'./storage/nowp{ct}', 'wb')
            # source, destination
        
            pickle.dump(str(self.nowp), dbfile)                     
            dbfile.close()

            #dbfile = open(f'./storage/guild{ct}', 'ab')
            # source, destination
        
            #pickle.dump(self._guild, dbfile)                     
            #dbfile.close()

            idd=ctx.message.channel.id
            dbfile = open(f'./storage/channelid{ct}', 'wb')
            # source, destination
        
            pickle.dump(idd, dbfile)                     
            dbfile.close()



            
            yy=5
        except Exception as e:
            print(e)
    #def __setstate__(self, state):
    #    self.__dict__.update(state)  

    #def __setstate__(self, d):
    #    self._asdict = d

    async def showw(self,ctx):
        try:

            # Grab up to 5 entries from the queue...
            vc = ctx.voice_client

            if not vc or not vc.is_connected():
                return #await ctx.send('I am not currently connected to voice!',delete_after=10)
            
            upcoming = list(itertools.islice(self.queue._queue, 0, 999999))
            ii=0
            #fmt = '\n'.join(f'{_["title"]}' for _ in upcoming)
            fmt=''
            for temp in upcoming:
                tt=temp["title"]
                ii=ii+1
                fmt=fmt+f'{ii}. {temp["title"]}\n'
                #print(temp)
                #print("##########")
                
            #self.embed = discord.Embed(title=f'Upcoming - Next {len(upcoming)}', description=fmt)
            #self.embed=await self._channel.send(f'Upcoming - Next {len(upcoming)}\n{fmt}')
            try:
                await self.que.delete()
                await self.np.delete()
            except Exception as e:
                print("EEE",e)
                yy=5
            self.que=await self._channel.send(f'Upcoming - Next {len(upcoming)}\n{fmt}')
            self.np = await self._channel.send(f'Requested by @{vc.source.requester} {vc.source.webpage_url}')
            auto_now=0
        except Exception as e:
            await self._channel.send(f'NO songs in queue: {e}',delete_after=10)
            print(e)
            
            
            
            
    async def seek(self,ctx):
        #print(self.nowp)
        try:
            # Grab up to 5 entries from the queue...
            vc = ctx.voice_client

            if not vc or not vc.is_connected():
                return #await ctx.send('I am not currently connected to voice!',delete_after=10)
            

            ssource = await YTDLSource.create_source(ctx, self.nowp, loop=self.bot.loop, download=False)
            #print(ssource)
            tsize=0
            #print(self.queue)
            #print('--')
            temp=asyncio.Queue()
            temp2=asyncio.Queue()
            tsize=self.queue.qsize()
            while(tsize>0):
                t=await self.queue.get()
                t2=await self.searchqueue.get()
                await temp2.put(t2)
                await temp.put(t)
                tsize=tsize-1
            self.queue=None
            self.queue = asyncio.Queue()
            self.searchqueue=None
            self.searchqueue = asyncio.Queue()
            await self.queue.put(ssource)
            await self.searchqueue.put(self.nowp)
            tsize=temp.qsize()
            while(tsize>0):
                t=await temp.get()
                t2=await temp2.get()
                await self.searchqueue.put(t2)
                await self.queue.put(t)
                tsize=tsize-1
                
            yy=5
            #print(self.queue)
            await self.np.delete()
            await self.que.delete()


            

            
        except Exception as e:
            print(e)
        
        
    async def player_loop(self,ctx):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                async with timeout(99999999):  # 5 minutes...
                    source = await self.queue.get()
                    ssearch=await self.searchqueue.get()
                    self.nowp=ssearch
            except asyncio.TimeoutError:
                return self.destroy(self._guild)

            if not isinstance(source, YTDLSource):
                # Source was probably a stream (not downloaded)
                # So we should regather to prevent stream expiration
                try:
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
            global sflag
            if sflag==0:
                global timeestamp
                timeestamp=0
            else:
                sflag=0
            source.cleanup()
            self.current = None

            try:
                await self.que.delete()
                await self.np.delete()
            except discord.HTTPException:
                pass

    def destroy(self, guild):
        return self.bot.loop.create_task(self._cog.cleanup(guild))



players = {}


async def cleanup(guild):
    try:
        await guild.voice_client.disconnect()
    except AttributeError:
        pass

    try:
        global players
        del players[guild.id]
    except KeyError:
        pass

async def __local_check(ctx):
    if not ctx.guild:
        raise commands.NoPrivateMessage
    return True

async def __error(ctx, error):
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

def get_player(ctx):
    global player
    global auto_now
    while(auto_now!=0):
        yy=5
    auto_now=auto_now-1
    try:
        player = players[ctx.guild.id]
    except KeyError:
        player = MusicPlayer(ctx)
        players[ctx.guild.id] = player
    auto_now=auto_now+1

    return player


@commands.command(name='connect', aliases=['join'])
async def connect_(ctx, *, channel: discord.VoiceChannel=None):
    try:
        if not channel:
            try:
                channel = ctx.author.voice.channel
                print(channel)
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
    except Exception as e:
        yy=5
@commands.command(name='play', aliases=['sing','p'])
async def play_( ctx, search):
    global temp_ctx
    temp_ctx=ctx
    global auto_now

    try:
        await ctx.message.delete()
    except Exception as e:
        print(e)
    await ctx.trigger_typing()
    

    vc = ctx.voice_client

    if not vc:
        await ctx.invoke(connect_)

    player = get_player(ctx)
    

    source = await YTDLSource.create_source(ctx, search, loop=client.loop, download=False)

    await player.queue.put(source)
    await player.searchqueue.put(source["webpage_url"])
    await now_playing_(ctx)
    

    yy=5
@commands.command(name='resume', aliases=['r','res'])
async def resume_( ctx):
    vc = ctx.voice_client

    if not vc or not vc.is_connected():
        return #await ctx.send('I am not currently playing anything!', delete_after=10)
    elif not vc.is_paused():
        return

    vc.resume()
    await ctx.send(f'**`{ctx.author}`**: Resumed the song!',delete_after=10)
    await ctx.message.delete()
    



@commands.command(name='skip')
async def skip_( ctx):
    vc = ctx.voice_client

    if not vc or not vc.is_connected():
        return #await ctx.send('I am not currently playing anything!', delete_after=10)

    if vc.is_paused():
        pass
    elif not vc.is_playing():
        return
    try:
        player=get_player(ctx)
        await player.np.delete()
        await player.que.delete()
        await ctx.message.delete()
    except Exception as e:
        print("skip",e)
    vc.stop()
    await ctx.send(f'**`{ctx.author}`**: Skipped the song!',delete_after=10)
    


@commands.command(name='queue_info', aliases=['q', 'playlist','queue'])
async def queue_info( ctx):
    player = get_player(ctx)
    await player.showw(ctx)
    await ctx.message.delete()
    


@commands.command(name='now_playing', aliases=['np', 'current', 'currentsong', 'playing'])
async def now_playing_( ctx):

    player = get_player(ctx)
    if not player.current:
        return #await ctx.send('I am not currently playing anything!',delete_after=10)
    await player.showw(ctx)
    try:
        await ctx.message.delete()
    except Exception as e:
        print(e)
    yy=5
    

@commands.command(name='change_volume', aliases=['vol','volume'])
async def change_volume( ctx, vol: float):
    
    vc = ctx.voice_client

    if not vc or not vc.is_connected():
        return #await ctx.send('I am not currently connected to voice!', delete_after=10)

    if not 0 < vol < 101:
        return await ctx.send('Please enter a value between 1 and 100.',delete_after=10)

    player = get_player(ctx)

    if vc.source:
        vc.source.volume = vol / 100

    player.volume = vol / 100
    await ctx.send(f'**`{ctx.author}`**: Set the volume to **{vol}%**',delete_after=10)
    await ctx.message.delete()
    


@commands.command(name='stop')
async def stop_( ctx):
    vc = ctx.voice_client

    if not vc or not vc.is_connected():
        return #await ctx.send('I am not currently playing anything!', delete_after=10)
    try:
        player=get_player(ctx)
        await player.np.delete()
        await player.que.delete()
        await ctx.message.delete()
    except Exception as e:
        print("stop",e)

    await cleanup(ctx.guild)
    

    

@commands.command(name='seek')
async def seek_( ctx, search: int):
    global sflag
    sflag=1
    player=get_player(ctx)
    await player.seek(ctx)
    vc = ctx.voice_client
    
    global timeestamp
    #print(timeestamp)
    timeestamp=search
    #print(timeestamp)
    if not vc or not vc.is_connected():
        return #await ctx.send('I am not currently playing anything!', delete_after=10)
    
    vc.stop()


@commands.command(name="pause", aliases=["pausee"])
async def pause_( ctx):
    vc = ctx.voice_client

    if not vc or not vc.is_playing():
        return #await ctx.send('I am not currently playing anything!', delete_after=10)
    elif vc.is_paused():
        return

    vc.pause()
    await ctx.send(f'**`{ctx.author}`**: Paused the song!',delete_after=10)
    await ctx.message.delete()
    


@commands.command(name='remove', aliases=['rem'])
async def remove_( ctx,index:int):
    vc = ctx.voice_client

    if not vc or not vc.is_playing():
        return #await ctx.send('I am not currently playing anything!', delete_after=10)
    elif vc.is_paused():
        return

    player=get_player(ctx)
    try:
        tsize=0
        temp=asyncio.Queue()
        temp2=asyncio.Queue()
        tsize=player.queue.qsize()
        while(tsize>0):
            t=await player.queue.get()
            t2=await player.searchqueue.get()
            await temp2.put(t2)
            await temp.put(t)
            tsize=tsize-1
        player.queue=None
        player.queue = asyncio.Queue()
        player.searchqueue=None
        player.searchqueue = asyncio.Queue()
        tsize=temp.qsize()
        tflag=1
        while(tsize>0):
            if tflag!=index:
                t=await temp.get()
                t2=await temp2.get()
                await player.searchqueue.put(t2)
                await player.queue.put(t)
            else:
                await temp.get()
                await temp2.get()
            tsize=tsize-1
            tflag=tflag+1
        yy=5
    except Exception as e:
        yy=5
    await player.showw(ctx)
    
    await ctx.send(f'**`{ctx.author}`**: Removed the song!',delete_after=40)
    await ctx.message.delete()
      
#####################################   save
@commands.command(name="save", aliases=["savee"])
async def save_(ctx=None):
    global players
    

    try:

        access_key=os.environ.get('access_key')
        access_secret=os.environ.get('access_secret')
        bucket_name=os.environ.get('bucket_name')
        
        client_s3=boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=access_secret
        )
        
        
        ctxs=list(players.keys())
        print(ctxs)
        dbfile = open(f'./storage/ctxs', 'wb')
        pickle.dump(ctxs, dbfile)
        dbfile.close()
        
        data_file_folder=os.path.join(os.getcwd(),'storage')

        for kk in ctxs:
            await players[kk].pk(kk,ctx)
            
            
        for file in os.listdir(data_file_folder):
            client_s3.upload_file(
            os.path.join(data_file_folder,file),
            bucket_name,
             file
            )
        
        
        
    except Exception as e:
        print(e)



@tasks.loop(seconds = 300)
async def sav():
  await asyncio.sleep(200)
  global temp_ctx
  await save_(temp_ctx)
  print('saved')
##################    load

@client.event
async def on_message(message):
  ctx = await client.get_context(message)
  msg=str(message.content)
  if message.content.lower().startswith(';playy') or message.content.lower().startswith(';play'):

    second = msg.split(' ', 1)[1]
    await play_(ctx,second)

  elif message.content.lower().startswith(';connect') or message.content.lower().startswith(';join'):
    #second = msg.split(' ', 1)[1]
    await ctx.invoke(connect_)

  elif message.content.lower().startswith(';resume') or message.content.lower().startswith(';resumee'):
    #second = msg.split(' ', 1)[1]
    await resume_(ctx)

  elif message.content.lower().startswith(';skip'):
    #second = msg.split(' ', 1)[1]
    await skip_(ctx)

  elif message.content.lower().startswith(';np') or message.content.lower().startswith(';now_playing'):
    #second = msg.split(' ', 1)[1]
    await now_playing_(ctx)

  elif message.content.lower().startswith(';vol') or message.content.lower().startswith(';volume'):
    second = msg.split(' ', 1)[1]
    second=flot(second)
    await change_volume(ctx,second)

  elif message.content.lower().startswith(';stop'):
    #second = msg.split(' ', 1)[1]
    await stop_(ctx)

  elif message.content.lower().startswith(';seek'):
    second = msg.split(' ', 1)[1]
    second=int(second)
    await seek_(ctx,second)

  elif message.content.lower().startswith(';pause'):
    #second = msg.split(' ', 1)[1]
    await pause_(ctx)

  elif message.content.lower().startswith(';rem') or message.content.lower().startswith(';remove'):
    second = msg.split(' ', 1)[1]
    second=int(second)
    await remove_(ctx,second)

  elif message.content.lower().startswith(';save'):
    #second = msg.split(' ', 1)[1]
    await save_(ctx)
  elif ctx.message.channel.id==826233359087960085:
    if message.author != client.user:
      await play_(ctx,str(message.content))

  

#client.load_extension('music')

keep_alive()


client.run(os.environ.get('token'))


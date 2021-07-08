import discord
import os
from os import environ
from keep_alive import keep_alive
from discord.ext import commands, tasks
import pickle
import boto3
#Daksh
import time
from datetime import datetime
seek_flag=0
#temp_ctx=None
#auto_now=0
client=commands.Bot(command_prefix=';')
status="♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥"
@client.event
async def on_ready():
  print("Ready Daksh. Hey ",client.user)
  await client.change_presence(activity=discord.Game(status))
  #await load()
  #sav.start()
  #autorestart.start()
  get_members.start()
timeestamp=0
#ctx_data={}
#ctx_data_flag=0
async def load():
    global ctx_data_flag
    global timeestamp
    try:
      global ctx_data

      access_key=''
      access_secret=''
      bucket_name=''
      client_s3=boto3.client(
      's3',
      aws_access_key_id=access_key,
      aws_secret_access_key=access_secret
      )
      
      client_s3.download_file(bucket_name,'ctxs',os.path.join('./storage/','ctxs'))
      #
      dbfile = open('./storage/ctxs', 'rb')     
      ctxs = pickle.load(dbfile)
      #print(ctxs)
      dbfile.close()
      for x in ctxs:
          client_s3.download_file(bucket_name,f'{x}',os.path.join('./storage/',f'{x}'))

      for x in ctxs:
          dbfile=open(f'./storage/{x}', 'rb')
          ctx_dataa=pickle.load(dbfile)
          ctx_data[x]=ctx_dataa
          dbfile.close()
          channelid=ctx_data[x][2]
          channel = client.get_channel(int(channelid))
          vc_channel = client.get_channel(824253644718997514)
          await vc_channel.connect()
          #print(channel)
          nowp=ctx_data[x][0]
          elp=ctx_data[x][3]
          #print(elp)
          #if not elp is None:
          #  timeestamp=int(elp)
          await channel.send(f';play {str(nowp)}')
          await asyncio.sleep(5)
          searchqueue=ctx_data[x][1]
          size=len(searchqueue)
          #print(searchqueue)
          j=1
          for que in searchqueue:
              j=j+1
              await channel.send(f';play {str(que)}')
              await asyncio.sleep(7)
      ctx_data_flag=1
    except Exception as e:
      yy=5
    finally:
      ctx_data_flag=1



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


playliststart=1

sflag=0






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
    async def create_source(cls, ctx, search: str, *, loop, download=False,isplaylist=True):
        loop = loop or asyncio.get_event_loop()
        global sflag
        global playliststart
        #print(playliststart)
        ytdlopts={}
        if isplaylist==False:
          #print('\n\n')
          ytdlopts = {
              'format': 'worstaudio/worst',
              'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
              'restrictfilenames': True,
              'nocheckcertificate': True,
              'ignoreerrors': True,
              'noplaylist':True,
              'logtostderr': False,
              'quiet': True,
              'no_warnings': True,
              'default_search': 'ytsearch',
              'extract_audio':True,
              'source_address': '0.0.0.0',# ipv6 addresses cause issues sometimes
              """
              'postprocessors': [{
                  'key': 'FFmpegExtractAudio',
                  'preferredcodec': 'mp3',
                  'preferredquality': '64',
              }],
              """
              
              'skipdownload':True,
              'simulate': True,
              'nooverwrites': True,
              'keepvideo': False,
              'flatplaylist':True,
              
              
              }
        else:
          ytdlopts = {
              'format': 'worstaudio/worst',
              'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
              'restrictfilenames': True,
              'playliststart':playliststart,
              'playlistend':playliststart+1,
              'yesplaylist': isplaylist,
              'nocheckcertificate': True,
              'ignoreerrors': True,
              'logtostderr': False,
              'quiet': True,
              'no_warnings': True,
              'default_search': 'auto',
              'extract_audio':True,
              'source_address': '0.0.0.0',# ipv6 addresses cause issues sometimes
              """
              'postprocessors': [{
                  'key': 'FFmpegExtractAudio',
                  'preferredcodec': 'mp3',
                  'preferredquality': '64',
              }],
              """
              
              'skipdownload':True,
              'simulate': True,
              'nooverwrites': True,
              'keepvideo': False,
              'flatplaylist':True,
              
              
          }
        ytdl = YoutubeDL(ytdlopts)
        
        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)
        
        #print(data)
        ffmpegopts = {
        'before_options': f'-nostdin -ss {timeestamp} -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 10' ,
        'options': f'-vn -preset veryfast'
        }
        #print(data)
        if download:
            source = ytdl.prepare_filename(data)
        else:
            if sflag==1:
              #print('seeking')
              if 'entries' in data:
                  # take first item from a playlist
                  data = data['entries'][0]
              return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}
            else:
              return data

        return cls(discord.FFmpegPCMAudio(source,**ffmpegopts), data=data, requester=ctx.author)

    async def create_source2(cls, ctx, search: str, *, loop, download=False):
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
              'skipdownload':True,
              'simulate': True,
              'nooverwrites': True,
              'keepvideo': False,
              'flatplaylist':True,
            
            
            }
        ytdl = YoutubeDL(ytdlopts)
      
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
            global timeestamp
        
        ffmpegopts = {
        'before_options': f'-vn -nostdin -ss {timeestamp} -threads 12 -probesize 32 -analyzeduration 0 -fflags nobuffer -thread_queue_size 10000' ,
        'options': f'-vn -preset ultrafast -ab 64 -tune zerolatency'
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
        global playliststart
        ytdlopts = {
            'format': 'worstaudio/worst',
            'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'yesplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch',
            'extract_audio':True,
            'source_address': '0.0.0.0',# ipv6 addresses cause issues sometimes
            
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '64',
            }],
            
            'skip_download':True,
            "simulate": True,
            "nooverwrites": True,
            "keepvideo": False,
            "flat_playlist":True,
            #"playlist_start":f'{playliststart}',
            
        }
        ytdl = YoutubeDL(ytdlopts)
        
        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)
        global timeestamp
        ffmpegopts = {
        'before_options': f'-nostdin -ss {timeestamp} -fflags nobuffer -flags low_delay -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 10 -age limit 30',
        'options': f'-threads 0 -vn -preset ultrafast -r 60 -segment_wrap 5'
        }

        return cls(discord.FFmpegPCMAudio(data['url'],**ffmpegopts), data=data, requester=requester)


class MusicPlayer:

    __slots__ = ('bot', '_guild', '_channel','isautopaused','isplaylist','_cog','ispaused','idd', 'queue','startt','stopt', 'next', 'current', 'np', 'volume','que','embed','nowp','searchqueue','cttx','elapsed')

    def __init__(self, ctx):
        self.startt=None
        self.stopt=None
        self.elapsed=0.0
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog
        self.cttx=ctx
        self.ispaused=0
        self.isautopaused=0
        #self.ispaused=False
        self.idd=ctx.message.channel.id
        self.queue = asyncio.Queue()
        self.next = asyncio.Event()
        self.isplaylist=0

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
                #print("EEE",e)
                yy=5
            self.que=await self._channel.send(f'--------------------------------------------------------------------------------------------------------------------------------\nUpcoming - Next {len(upcoming)}\n{fmt}')
            self.np = await self._channel.send(f'Requested by @{vc.source.requester} {vc.source.webpage_url}')
            #auto_now=0
        except Exception as e:
            await self._channel.send(f'NO songs in queue: {e}',delete_after=10)
            yy=5
            
            
            
            
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
            await ctx.message.delete()


            

            
        except Exception as e:
            yy=5
        
        
    async def player_loop(self,ctx):
        await self.bot.wait_until_ready()
        #global ctx_data_flag
        #global ctx_data

        while not self.bot.is_closed():
            self.next.clear()
            try:

              try:
                  async with timeout(99999999):  # 5 minutes...
                      source = await self.queue.get()
                      ssearch=await self.searchqueue.get()
                      self.nowp=ssearch
              except asyncio.TimeoutError:
                  return self.destroy(self._guild)
              global sflag
              global timeestamp
              """
              if sflag==1:
                yy=5
              else:
                timeestamp=0
                self.elapsed=0.0
              """
                
                
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
              self.startt=datetime.now().timestamp()
              if self.isautopaused==1:
                await pause_(ctx,1)
              #if ctx_data_flag==0:
              #  await seek_(ctx,int(ctx_data[ctx.guild.id][3]))
              #  await asyncio.sleep(10)
              #  #if self.ispaused==True:
              #  # await pause_(ctx)
              #else:
              await self.showw(ctx)
              
              
              await self.next.wait()
              #self.ispaused=False
              #print('ssss',sflag)
              if sflag==0:
                  timeestamp=0
                  self.elapsed=0.0
              else:
                  sflag=0
              source.cleanup()
              self.current = None

              try:
                  await self.que.delete()
                  await self.np.delete()
              except Exception as e:
                  #print(e)
                  yy=5
              yy=5
            except Exception as e:
              yy=5
              #print(e)

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

    #print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

def get_player(ctx):
    global players
    #global auto_now
    #while(auto_now!=0):
    #    yy=5
    #auto_now=auto_now-1
    try:
        player = players[ctx.guild.id]
    except KeyError:
        player = MusicPlayer(ctx)
        players[ctx.guild.id] = player
    #auto_now=auto_now+1

    return player


@commands.command(name='connect', aliases=['join'])
async def connect_(ctx, *, channel: discord.VoiceChannel=None):
    try:
        if not channel:
            try:
                channel = ctx.author.voice.channel
                #print(channel)
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
        #print(e)
        yy=5
@commands.command(name='play', aliases=['sing','p'])
async def play_( ctx, search,isplaylist=0):
    try:
        #global temp_ctx
        #global ctx_data
        #global ctx_data_flag
        #temp_ctx=ctx
        #global auto_now
        await ctx.trigger_typing()
        

        vc = ctx.voice_client

        if not vc:
            await ctx.invoke(connect_)

        player = get_player(ctx)
        global playliststart
        player.ispaused=0
        player.ispaused=0
        serr=search.lower()
        list_ind=serr.find('&list=')
        if list_ind==-1:
          list_ind=serr.find('?list=')
        #print(list_ind)
        ind_ind=0
        
        if not list_ind==-1:

          ind_ind=serr.find('&index=')
          if ind_ind==-1:
            ind_ind=serr.find('&start_radio=')
            if ind_ind==-1:
              ind_ind=len(search)
              search=search+'&index=1'
              serr=serr+'&index=1'
              ind_ind=ind_ind+7
            else:
              ind_ind=ind_ind+13
          else:
            ind_ind=ind_ind+7
          #print(serr[ind_ind::])
          ind_ind=serr[ind_ind::]
          ind_ind=int(ind_ind)
          playliststart=ind_ind
          #print(playliststart)
          
          isplaylist=1
          player.isplaylist=1
          list_ind=list_ind+6
          listt=''
          temp_list=list_ind
          while True:
            if serr[temp_list]=='&':
              break
            listt=listt+search[temp_list]
            temp_list=temp_list+1



          
          #if ctx_data_flag==0:
          #  player.elapsed=ctx_data[ctx.guild.id][3]
          #  player.startt=ctx_data[ctx.guild.id][4]
          #  player.stopt=ctx_data[ctx.guild.id][5]
          #  player.ispaused=ctx_data[ctx.guild.id][6]
          source = await YTDLSource.create_source(ctx, search, loop=client.loop, download=False)
          l=0
          if 'entries' in source:
            try:
              temp={}
              # take first item from a playlist
              temp['webpage_url']=source['entries'][0]["webpage_url"]
              temp['requester']=ctx.author
              temp['title']=source['entries'][0]["title"]
              await player.queue.put(temp)
              await player.searchqueue.put(source['entries'][0]["webpage_url"])
              l=l+1
              serr=str(source['entries'][1]["webpage_url"])+f'&list={listt}&index={ind_ind+1}'
              #print('ssssssssssssssssssssssss',serr)
              
              await play_(ctx,serr,1)
            except Exception as e:
              await now_playing_(ctx)
            #await asyncio.sleep(2)
          else:
            #print('ppppppppppppppppppppppppppppp')
            temp={}
            temp['webpage_url']=source["webpage_url"]
            temp['requester']=ctx.author
            temp['title']=source["title"]
            await player.queue.put(temp)
            await player.searchqueue.put(source["webpage_url"])
            await now_playing_(ctx)
        else:
          source = await YTDLSource.create_source2(cls=None,ctx=ctx, search=search, loop=client.loop, download=False)
          #print(source)
          await player.queue.put(source)
          await player.searchqueue.put(source['webpage_url'])
          await now_playing_(ctx)
        await ctx.message.delete()
    except Exception as e:
        #print('playyy',e)
        yy=5
@commands.command(name='resume', aliases=['r','res'])
async def resume_( ctx):
  try:
      vc = ctx.voice_client

      if not vc or not vc.is_connected():
          return #await ctx.send('I am not currently playing anything!', delete_after=10)
      elif not vc.is_paused():
          return
      player=get_player(ctx)
      player.ispaused=0
      player.isautopaused=0
      vc.resume()
      
      #player.ispaused=False
      await ctx.send(f'**`{ctx.author}`**: Resumed the song!',delete_after=10)
      
      try:
          player=get_player(ctx)
          player.startt=datetime.now().timestamp()
      except Exception as e:
        #print(e)
        yy=5
      await ctx.message.delete()
  except Exception as e:
    #print(e)
    yy=5


@commands.command(name='skip')
async def skip_( ctx):
  try:
    vc = ctx.voice_client

    if not vc or not vc.is_connected():
        return #await ctx.send('I am not currently playing anything!', delete_after=10)

    if vc.is_paused():
        pass
    elif not vc.is_playing():
        return
    try:
        global timeestamp
        timeestamp=0
        player=get_player(ctx)
        await player.np.delete()
        await player.que.delete()
        await ctx.message.delete()
    except Exception as e:
        #print("skip",e)
        yy=5
        pass
    vc.stop()
    await ctx.send(f'**`{ctx.author}`**: Skipped the song!',delete_after=10)
  except Exception as e:
    #print(e)
    yy=5


@commands.command(name='queue_info', aliases=['q', 'playlist','queue'])
async def queue_info( ctx):
    try:
        player = get_player(ctx)
        await player.showw(ctx)
        await ctx.message.delete()
    except Exception as e:
      #print(e)
      yy=5


@commands.command(name='now_playing', aliases=['np', 'current', 'currentsong', 'playing'])
async def now_playing_( ctx):

    player = get_player(ctx)
    if not player.current:
        return #await ctx.send('I am not currently playing anything!',delete_after=10)
    await player.showw(ctx)
    try:
        await ctx.message.delete()
    except Exception as e:
        #print(e)
        yy=5
        pass
    yy=5
    

@commands.command(name='change_volume', aliases=['vol','volume'])
async def change_volume( ctx, vol: float):
    try:
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
    except Exception as e:
      #print(e)
      yy=5


@commands.command(name='stop')
async def stop_( ctx):
    vc = ctx.voice_client
    global timeestamp
    timeestamp=0.0
    global sflag
    sflag=0
    if not vc or not vc.is_connected():
        return #await ctx.send('I am not currently playing anything!', delete_after=10)
    try:
        player=get_player(ctx)
        player.ispaused=0
        player.isautopaused=0
        await player.np.delete()
        await player.que.delete()
        await ctx.message.delete()
    except Exception as e:
        #print("stop",e)
        pass
    

    await cleanup(ctx.guild)
    

    

@commands.command(name='seek')
async def seek_( ctx, search: int):
    global sflag
    sflag=1
    player=get_player(ctx)
    await player.seek(ctx)
    vc = ctx.voice_client
    player.startt=datetime.now().timestamp()
    player.elapsed=search
    global timeestamp
    #print(timeestamp)
    timeestamp=search
    #print(timeestamp)
    if not vc or not vc.is_connected():
        return #await ctx.send('I am not currently playing anything!', delete_after=10)
    
    vc.stop()


@commands.command(name="pause", aliases=["pausee"])
async def pause_( ctx,pflag=0):
    vc = ctx.voice_client
    
    if not vc or not vc.is_playing():
        return #await ctx.send('I am not currently playing anything!', delete_after=10)
    elif vc.is_paused():
        return
    await time_(ctx)
    vc.pause()
    player=get_player(ctx)
    if pflag==0:
      player.ispaused=1
    player.isautopaused=1
    #player.ispaused=True
    await ctx.send(f'**`{ctx.author}`**: Paused the song!',delete_after=10)
    try:
        
        player=get_player(ctx)
        player.stopt=datetime.now().timestamp()
        player.elapsed=player.elapsed+player.stopt-player.startt
        player.startt=datetime.now().timestamp()
        await ctx.message.delete()
        
    except Exception as e:
        #print(e)
        yy=5
    yy=5
@commands.command(name="time", aliases=["timee"])
async def time_( ctx):
    
    try:
      vc = ctx.voice_client
      player=get_player(ctx)
      
      if not vc.is_playing():
        player.stopt=datetime.now().timestamp()
        
        player.startt=datetime.now().timestamp()
        
      else:
        player.stopt=datetime.now().timestamp()
        player.elapsed=player.elapsed+player.stopt-player.startt
        #print(player.elapsed)
        player.startt=datetime.now().timestamp()
      
      await ctx.send(f'**`{ctx.author}`**: Elapsed Time is {player.elapsed}!',delete_after=10)
      await ctx.message.delete()
    except Exception as e:
      #print(e)
      yy=5
    yy=5
@commands.command(name='remove', aliases=['rem'])
async def remove_( ctx,index:int):
    try:
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
            #print(e)
            yy=5
        await player.showw(ctx)
        
        await ctx.send(f'**`{ctx.author}`**: Removed the song!',delete_after=40)
        await ctx.message.delete()
    except Exception as e:
      #print(e)
      yy=5




"""
#####################################   save
@commands.command(name="save", aliases=["savee"])
async def save_(ctx=None):
    global players
    

    try:
        
        access_key=''
        access_secret=''
        bucket_name=''
        
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
            
            temp=[]
            await time_(players[kk].cttx)
            print(players[kk].elapsed)
            tsize=players[kk].searchqueue.qsize()
            while(tsize>0):
                t=await players[kk].searchqueue.get()
                temp.append(str(t))
                tsize=tsize-1
            ctx_data=[]
            ctx_data.append(str(players[kk].nowp))
            ctx_data.append(temp)
            ctx_data.append(int(players[kk].idd))
            
            ctx_data.append(players[kk].elapsed)
            print('save elapsed',players[kk].elapsed)
            ctx_data.append(players[kk].startt)
            ctx_data.append(players[kk].stopt)
            paused = players[kk].ispaused
            #print(paused)
            ctx_data.append(paused)
            dbfile = open(f'./storage/{kk}', 'wb')
            pickle.dump(ctx_data, dbfile)
            dbfile.close()
        for file in os.listdir(data_file_folder):
            client_s3.upload_file(
            os.path.join(data_file_folder,file),
            bucket_name,
             file
            )
        await ctx.send(f'**`{ctx.author}`**:State Saved !',delete_after=30)
        print('saved')
        await ctx.message.delete()
        
    except Exception as e:
        print('save',e)
        pass
    yy=5

"""

yy=5
@tasks.loop(seconds=7200)
async def autorestart():
  try:
    global players
    for x in players:
      ctx=players[x].cttx
      player=get_player(ctx)
      await time_(ctx)
      await asyncio.sleep(2)
      await seek_(ctx,player.elapsed)
    print('restarted')
  except Exception as e:
    print('can not restart',e)

@tasks.loop(seconds = 10)
async def get_members():
  try:
    global players
    for x in players:
      ctx=players[x].cttx
      player=get_player(ctx)
      if player.ispaused==1:
        yy=5
      else:
        channel = ctx.voice_client.channel
        member_ids = channel.voice_states.keys()
        if ctx.voice_client.is_playing():
          if(len(member_ids)==1):
            await pause_(ctx,1)
        elif ctx.voice_client.is_paused():
          if(len(member_ids)>1):
            await resume_(ctx)
        #print(member_ids)
        yy=5
  except Exception as e:
    #print(e)
    yy=5
#@tasks.loop(seconds = 60)
#async def sav():
#  global ctx_data_flag
#  await asyncio.sleep(70)
#  global temp_ctx
#  await save_(temp_ctx)
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
  elif message.content.lower().startswith(';time'):
    #second = msg.split(' ', 1)[1]
    await time_(ctx)
  elif message.content.lower().startswith(';save'):
    #second = msg.split(' ', 1)[1]
    await save_(ctx)
  elif ctx.message.channel.id==826233359087960085:
    if message.author != client.user:
      await play_(ctx,str(message.content))

  

#client.load_extension('music')

keep_alive()


client.run(os.environ.get('token'))


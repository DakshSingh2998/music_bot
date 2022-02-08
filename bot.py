import discord
import os
from os import environ
from keep_alive import keep_alive
from discord.ext import commands, tasks
#import pickle
#import boto3
#Daksh
import ctypes
import tracemalloc
import gc
import psutil
import time
from datetime import datetime
ctx_save={'d':'d'}
#temp_ctx=None
#auto_now=0
client=commands.Bot(command_prefix=';')
status=""
daksh_yt="https://www.youtube.com/channel/UCEL4AUYHQnq2RJivLg_NoQw"
@client.event
async def on_ready():
  global status
  status=str(len(client.guilds))+" servers"
  print("Ready Daksh. Hey ",client.user)
  await client.change_presence(activity=discord.Streaming(platform='YouTube',name=status, url="https://www.youtube.com/watch?v=NHnT9NEuDWo"))
  try:
    for x in client.voice_clients:
      try:
        await x.disconnect()
      except Exception as e:
        #print(e)
        pass
  except Exception as e:
    #print(e)
    pass
  #await load()
  #sav.start()
  #autorestart.start()
  global players
  players={}
  await asyncio.sleep(5)
  await get_membersss()
  await clearram.start()
#ctx_data={}
#ctx_data_flag=0
"""
async def load():
    global ctx_data_flag
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
      pass
    finally:
      ctx_data_flag=1
"""
from discord.ext import commands
import asyncio
import itertools
import sys
import traceback
from async_timeout import timeout
from functools import partial
from youtube_dl import YoutubeDL
#import boto3
#import pickle
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
    self.duration=data.get('duration')
    # YTDL info dicts (data) have other useful information you might want
    # https://github.com/rg3/youtube-dl/blob/master/README.md
  def __getitem__(self, item: str):
    return self.__getattribute__(item)
  
  @classmethod
  async def create_source(cls, ctx, search: str, *, loop, download=False,isplaylist=True):
    loop = loop or asyncio.get_event_loop()
    global ctx_save
    #print(ctx_save[int(ctx.guild.id)][2])
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
        #'agelimit':30,
        'keepvideo': False,
        'flatplaylist':True,
        
        'cachedir': False,
        'cookies':'cookies.txt',
        }
    else:
      ytdlopts = {
        'format': 'worstaudio/worst',
        'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'playliststart':ctx_save[int(ctx.guild.id)][2],
        'playlistend':ctx_save[int(ctx.guild.id)][2]+1,
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
        #'agelimit':30,
        'keepvideo': False,
        'flatplaylist':True,
        'cachedir': False,
        
        'cookies':'cookies.txt',
      }
    ytdl = YoutubeDL(ytdlopts)
    to_run = partial(ytdl.extract_info, url=search, download=download)
    data = await loop.run_in_executor(None, to_run)
    #print(data)
    ffmpegopts = {
    'before_options': f'-nostdin -ss {ctx_save[int(ctx.guild.id)][0]} -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 10' ,
    'options': f'-vn -preset veryfast'
    }
    #print(data)
    try:
      del loop
      #del requester
      del ytdlopts
      del ytdl
      del to_run
      #del data
      #del ffmpegopts
    except Exception as e:
      pass
    if download:
      pass
    else:
      if ctx_save[int(ctx.guild.id)][1]==1:
        #print('seeking')
        if 'entries' in data:
          # take first item from a playlist
          data = data['entries'][0]
        return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title'],'duration':data['duration']}
      else:
        return data
    #return cls(discord.FFmpegPCMAudio(source,**ffmpegopts), data=data, requester=ctx.author)
    pass
  
  async def create_source2(cls, ctx, search: str, *, loop, download=False):
    ytdlopts = {
      'format': 'worstaudio/worst',
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
        #'agelimit':30,
        'flatplaylist':True,
      'cachedir': False,
        'cookies':'cookies.txt',
    }
    ytdl = YoutubeDL(ytdlopts)
    loop = loop or asyncio.get_event_loop()
    to_run = partial(ytdl.extract_info, url=search, download=download)
    data = await loop.run_in_executor(None, to_run)
    global ctx_save
    if 'entries' in data:
      # take first item from a playlist
      data = data['entries'][0]
    ffmpegopts = {
    'before_options': f'-vn -nostdin -ss {ctx_save[int(ctx.guild.id)][0]} -threads 12 -probesize 32 -analyzeduration 0 -fflags nobuffer -thread_queue_size 10000' ,
    'options': f'-vn -preset ultrafast -ab 64 -tune zerolatency'
    }
    try:
      del loop
      #del requester
      del ytdlopts
      del ytdl
      del to_run
      #del data
      #del ffmpegopts
    except Exception as e:
      pass
    if download:
        pass
    else:
      return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title'],'duration':data['duration']}
    #return cls(discord.FFmpegPCMAudio(source,**ffmpegopts), data=data, requester=ctx.author)
    pass
  
  @classmethod
  async def regather_stream(cls, data, *, loop,ctx):
    loop = loop or asyncio.get_event_loop()
    requester = data['requester']
    ytdlopts = {
      'format': 'bestaudio/best',
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
          #'preferredquality': '64',
      }],
      'skip_download':True,
      "simulate": True,
      "nooverwrites": True,
      "keepvideo": False,
      "flat_playlist":True,
      'cachedir': False,
      
      'cookies':'cookies.txt',
      #'agelimit':30,
      #"playlist_start":f'{ctx_save[int(ctx.guild.id)][2]}',
    }
    ytdl = YoutubeDL(ytdlopts)
    global ctx_save
    to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
    data = await loop.run_in_executor(None, to_run)
    ffmpegopts = {
    'before_options': f'-nostdin -ss {ctx_save[int(ctx.guild.id)][0]} -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 10',
    'options': f'-vn'
    }
    try:
      del loop
      #del requester
      del ytdlopts
      del ytdl
      del to_run
      #del data
      #del ffmpegopts
    except Exception as e:
      pass
    return cls(discord.FFmpegPCMAudio(data['url'],**ffmpegopts), data=data, requester=requester)
  pass

class MusicPlayer:
  __slots__ = ('bot', '_guild','before', '_channel','isautopaused','isplaylist','_cog','ispaused','idd', 'queue','startt','stopt', 'next', 'current', 'np', 'volume','que','embed','nowp','searchqueue','cttx','elapsed')
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
    self.before=None
    try:
      ctx.bot.loop.create_task(self.player_loop(ctx))
    except Exception as e:
      pass
    pass
  
  """
  async def reset(self,ctx):
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
    self.before=None
  """
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
    global ctx_save
    try:
      await ctx_save[int(ctx.guild.id)][4].acquire()
      # Grab up to 5 entries from the queue...
      vc = self.cttx.voice_client
      if not vc or not vc.is_connected():
        return #await ctx.send('I am not currently connected to voice!',delete_after=10)
      upcoming = list(itertools.islice(self.queue._queue, 0, 999999))
      ii=0
      #fmt = '\n'.join(f'{_["title"]}' for _ in upcoming)
      fmt=''
      tt=None
      temp=None
      tdur=None
      for temp in upcoming:
        tt=temp["title"]
        tdur=temp["duration"]
        if len(tt)>31:
          tt=tt[0:30]
          tt=tt+'...'
        ii=ii+1
        fmt=fmt+f'{ii}. {tt} [{tdur}s]\n'
        #print(temp)
        #print("##########")
      #self.embed = discord.Embed(title=f'Upcoming - Next {len(upcoming)}', description=fmt)
      #self.embed=await self._channel.send(f'Upcoming - Next {len(upcoming)}\n{fmt}')
      try:
        await self.que.delete()
        await self.np.delete()
      except Exception as e:
        #print("EEE",e)
        pass
      dur=int(vc.source.duration)
      #self.que=await self._channel.send(f'--------------------------------------------------------------------------------------------------------------------------------\nUpcoming - Next {len(upcoming)}\n{fmt}')
      #self.np = await self._channel.send(f'Requested by @{vc.source.requester} {vc.source.webpage_url} [{dur}s]')
      #auto_now=0
      self.que=await self.cttx.send(f'--------------------------------------------------------------------------------------------------------------------------------\nUpcoming - Next {len(upcoming)}\n{fmt}')
      self.np = await self.cttx.send(f'Requested by @{vc.source.requester} {vc.source.webpage_url} [{dur}s]')
      await self.np.add_reaction('⏯️')
      await self.np.add_reaction('⏸️')
      await self.np.add_reaction('⏭️')
      await self.np.add_reaction('⏹️')
      await self.np.add_reaction('⌚')
      del vc
      del upcoming
      del ii
      del tdur
      del tt
      del temp
      del dur
      del fmt
    except Exception as e:
      #print(e)
      #await self._channel.send(f'NO songs in queue: {e}',delete_after=10)
      pass
    finally:
      ctx_save[int(ctx.guild.id)][4].release()
      pass
    pass
  
  async def seek(self,ctx):
    global ctx_save
    #print(self.nowp)
    try:
      await ctx_save[int(ctx.guild.id)][5].acquire()
      # Grab up to 5 entries from the queue...
      vc = ctx.voice_client
      if not vc or not vc.is_connected():
        return #await ctx.send('I am not currently connected to voice!',delete_after=10)
      #nnp=self.nowp
      ssource = await YTDLSource.create_source(ctx, self.nowp, loop=self.bot.loop, download=False)
      #print(ssource)
      tsize=0
      #print(self.queue)
      #print('--')
      temp=asyncio.Queue()
      temp2=asyncio.Queue()
      tsize=self.queue.qsize()
      t=None
      t2=None
      while(tsize>0):
        t=await self.queue.get()
        t2=await self.searchqueue.get()
        await temp2.put(t2)
        await temp.put(t)
        tsize=tsize-1
      #self.queue=None
      while(self.queue.qsize()>0):
        await self.queue.get()
        await self.searchqueue.get()
      #self.queue = asyncio.Queue()
      #self.searchqueue=None
      #self.searchqueue = asyncio.Queue()
      src=ssource
      await self.queue.put(src)
      await self.searchqueue.put(self.nowp)
      tsize=temp.qsize()
      while(tsize>0):
        t=await temp.get()
        t2=await temp2.get()
        await self.searchqueue.put(t2)
        await self.queue.put(t)
        tsize=tsize-1
      pass
      #print(self.queue)
      await self.np.delete()
      await self.que.delete()
      #await ctx.message.delete()
      del vc
      del ssource
      del tsize
      del temp
      #del nnp
      del src
      #del nnp
      del temp2
      del t
      del t2
    except Exception as e:
      pass
    finally:
      ctx_save[int(ctx.guild.id)][5].release()
    pass
  
  async def player_loop(self,ctx):
    try:
      await self.bot.wait_until_ready()
      #global ctx_data_flag
      #global ctx_data
      while not self.bot.is_closed():
        self.next.clear()
        global ctx_save
        try:
          try:
            async with timeout(99999999):  # 5 minutes...
              source = await self.queue.get()
              ssearch=await self.searchqueue.get()
              self.nowp=ssearch
          except asyncio.TimeoutError:
            return self.destroy(self._guild)
          """
          if ctx_save[int(ctx.guild.id)][1]==1:
            pass
          else:
            ctx_save[int(ctx.guild.id)]['timeestamp']=0
            self.elapsed=0.0
          """
          if not isinstance(source, YTDLSource):
            # Source was probably a stream (not downloaded)
            # So we should regather to prevent stream expiration
            try:
              source = await YTDLSource.regather_stream(source, loop=self.bot.loop,ctx=ctx)
            except Exception as e:
              await ctx.send(f'There was an error processing your song.\n'
                                        f'```css\n[{e}]\n```',delete_after=10)
              continue
          source.volume = self.volume
          self.current = source
          try:
            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            pass
          except Exception as e:
            try:
              self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
              pass
            except Exception as e:
              try:
                self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
                pass
              except Exception as e:
                pass
          bef=discord.utils.get(client.voice_clients, guild=ctx.guild)
          bef=bef.channel.id
          self.before=bef
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
          #print('ssss',ctx_save[int(ctx.guild.id)][1])
          if ctx_save[int(ctx.guild.id)][1]==0:
              ctx_save[int(ctx.guild.id)][0]=0
              self.elapsed=0.0
          else:
              ctx_save[int(ctx.guild.id)][1]=0
          source.cleanup()
          self.current = None
          try:
            del source
            del ssearch
            await self.que.delete()
            await self.np.delete()
          except Exception as e:
            #print(e)
            pass
          pass
        except Exception as e:
          pass
          #print(e)
    except Exception as e:
      pass
  def destroy(self, guild):
    return self.bot.loop.create_task(self._cog.cleanup(guild))
  pass

players = {}
async def cleanup(guild):
  try:
    await guild.voice_client.disconnect()
  except AttributeError:
    pass
  try:
    global players
    global ctx_save
    #del ctx_save[int(guild.id)]
    #del players[guild.id]
    #player[guild.id]=None
    #ctx_save[int(guild.id)]=None
    #players[guild.id].reset()
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
  #    pass
  #auto_now=auto_now-1
  try:
    player = players[ctx.guild.id]
    #print('try',ctx.guild.id)
  except KeyError:
    #print('except',ctx.guild.id)
    global ctx_save
    player = MusicPlayer(ctx)
    players[ctx.guild.id] = player
    #print(ctx.guild.id)
    #ctx_save[int(ctx.guild.id)].append(0)
    #ctx_save[int(ctx.guild.id)].append(0)
    #ctx_save[int(ctx.guild.id)].append(1)
    lock=asyncio.Lock()
    lockp=asyncio.Lock()
    templist=[0.0,0,1,1,lock,lockp]#####time,,4-show lock, 5 pause lock
    ctx_save[int(ctx.guild.id)]=templist
    #print(ctx_save[int(ctx.guild.id)][0])
    pass
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
    del vc
    await ctx.send(f'Connected to: **{channel}**')
    #await ctx.message.delete()
  except Exception as e:
    #print(e)
    pass
  pass

@commands.command(name='play', aliases=['sing','p'])
async def play_( ctx, search,isplaylist=0,listsize=0):
  #await showram(ctx)
  global ctx_save
  try:
    player = get_player(ctx)
    #await ctx_save[int(ctx.guild.id)][5].acquire()
    #print('success')
    if listsize==10:
      #await player.showw(ctx)
      del player
      return
    """
    if ctx.message.author.id!=356012950298951690:
      if int(player.queue.qsize())>30:
        await ctx.send("Max playlist length reached")
        return
    """
    #global temp_ctx
    #global ctx_data
    #global ctx_data_flag
    #temp_ctx=ctx
    #global auto_now
    #print("DDD")
    await ctx.trigger_typing()
    vc = ctx.voice_client
    await ctx.invoke(connect_)
    l=None
    temp=None
    source=None
    listt=None
    temp_list=None
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
      ctx_save[int(ctx.guild.id)][2]=ind_ind
      #print(ctx_save[int(ctx.guild.id)][2])
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
      source=None
      try:
        source = await YTDLSource.create_source(ctx, search, loop=client.loop, download=False)
        pass
      except Exception as e:
        try:
          source = await YTDLSource.create_source(ctx, search, loop=client.loop, download=False)
          pass
        except Exception as e:
          try:
            source = await YTDLSource.create_source(ctx, search, loop=client.loop, download=False)
            pass
          except Exception as e:
            return
          pass
        pass
      l=0
      if 'entries' in source:
        try:
          temp={}
          # take first item from a playlist
          temp['webpage_url']=source['entries'][0]["webpage_url"]
          temp['duration']=source['entries'][0]["duration"]
          temp['requester']=ctx.author
          temp['title']=source['entries'][0]["title"]
          await player.queue.put(temp)
          await player.searchqueue.put(source['entries'][0]["webpage_url"])
          l=l+1
          serr=str(source['entries'][1]["webpage_url"])+f'&list={listt}&index={ind_ind+1}'
          #print('ssssssssssssssssssssssss',serr)
          
          await play_(ctx,serr,1,listsize+1)
        except Exception as e:
          pass
          #await now_playing_(ctx)
        #await asyncio.sleep(2)
      else:
        #print('ppppppppppppppppppppppppppppp')
        temp={}
        temp['webpage_url']=source["webpage_url"]
        temp['duration']=source["duration"]
        temp['requester']=ctx.author
        temp['title']=source["title"]
        await player.queue.put(temp)
        await player.searchqueue.put(source["webpage_url"])
        ####await now_playing_(ctx)
    else:
      try:
        source = await YTDLSource.create_source2(cls=None,ctx=ctx, search=search, loop=client.loop, download=False)
        pass
      except Exception as e:
        try:
          source = await YTDLSource.create_source2(cls=None,ctx=ctx, search=search, loop=client.loop, download=False)
          pass
        except Exception as e:
          try:
            source = await YTDLSource.create_source2(cls=None,ctx=ctx, search=search, loop=client.loop, download=False)
            pass
          except Exception as e:
            return
      #print(ctx_save)
      await player.queue.put(source)
      await player.searchqueue.put(source['webpage_url'])
      ####await now_playing_(ctx)
    #await ctx.message.delete()
    #print('ss')
    del player
    del vc
    del serr
    del list_ind
    del ind_ind
    del listt
    del temp_list
    del source
    del temp
    del l
  except Exception as e:
    print('playyy',e)
    pass
  finally:
    pass
    #ctx_save[int(ctx.guild.id)][5].release()
  #await showram(ctx)
  pass

@commands.command(name='insert', aliases=['ins'])
async def insert_(ctx,search,isplaylist=0,position=0,listsize=0):
  global ctx_save
  try:
    player = get_player(ctx)
    #await ctx_save[int(ctx.guild.id)][5].acquire()
    if listsize==10:
      await player.showw(ctx)
      return
    """
    if ctx.message.author.id!=356012950298951690:
      if int(player.queue.qsize())>30:
        await ctx.send("Max playlist length reached")
        return
    """
    #global temp_ctx
    #global ctx_data
    #global ctx_data_flag
    #temp_ctx=ctx
    #global auto_now
    await ctx.trigger_typing()
    vc = ctx.voice_client
    await ctx.invoke(connect_)
    #print(position)
    if position-1>player.queue.qsize():
      return
    l=None
    temp=asyncio.Queue()
    source=None
    listt=None
    temp_list=None
    tempp=None
    temp2=asyncio.Queue()
    tsize=None
    t=None
    t2=None
    pos=None
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
      ctx_save[int(ctx.guild.id)][2]=ind_ind
      #print(ctx_save[int(ctx.guild.id)][2])
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
          tempp={}
          # take first item from a playlist
          tempp['webpage_url']=source['entries'][0]["webpage_url"]
          tempp['duration']=source['entries'][0]["duration"]
          tempp['requester']=ctx.author
          tempp['title']=source['entries'][0]["title"]
          ### insert code
          #print(source)
          while(temp.qsize()>0):
            temp.get()
            temp2.get()
          #temp=asyncio.Queue()
          #temp2=asyncio.Queue()
          tsize=player.queue.qsize()
          while(tsize>0):
            t=await player.queue.get()
            t2=await player.searchqueue.get()
            await temp2.put(t2)
            await temp.put(t)
            tsize=tsize-1
          pos=0
          while(player.queue.qsize()>0):
            await player.queue.get()
            await player.searchqueue.get()
          #player.queue=asyncio.Queue()
          #player.searchqueue=asyncio.Queue()
          while(pos<position-1):
            t=await temp.get()
            await player.queue.put(t)
            t2=await temp2.get()
            await player.searchqueue.put(t2)
            pos=pos+1
          await player.queue.put(tempp)
          await player.searchqueue.put(source['entries'][0]['webpage_url'])
          tsize=temp.qsize()
          pos=0
          while(pos<tsize):
            t=await temp.get()
            await player.queue.put(t)
            t2=await temp2.get()
            await player.searchqueue.put(t2)
            pos=pos+1
          #print(source['entries'][0]['webpage_url'])
          ####11
          l=l+1
          serr=str(source['entries'][1]["webpage_url"])+f'&list={listt}&index={ind_ind+1}'
          #print('ssssssssssssssssssssssss',serr)
          await insert_(ctx=ctx,search=serr,isplaylist=1,position=position+1,listsize=listsize+1)
        except Exception as e:
          pass
          #await now_playing_(ctx)
        #await asyncio.sleep(2)
      else:
        #print('ppppppppppppppppppppppppppppp')
        tempp={}
        tempp['webpage_url']=source["webpage_url"]
        tempp['duration']=source["duration"]
        tempp['requester']=ctx.author
        tempp['title']=source["title"]
        #print(source)
        while(temp.qsize()>0):
          temp.get()
          temp2.get()
        #temp=asyncio.Queue()
        #temp2=asyncio.Queue()
        #tsize=player.queue.qsize()
        while(tsize>0):
          t=await player.queue.get()
          t2=await player.searchqueue.get()
          await temp2.put(t2)
          await temp.put(t)
          tsize=tsize-1
        pos=0
        while(player.queue.qsize()>0):
          await player.queue.get()
          await player.searchqueue.get()
        #player.queue=asyncio.Queue()
        #player.searchqueue=asyncio.Queue()
        while(pos<position-1):
          t=await temp.get()
          await player.queue.put(t)
          t2=await temp2.get()
          await player.searchqueue.put(t2)
          pos=pos+1
        await player.queue.put(source)
        await player.searchqueue.put(source['webpage_url'])
        tsize=temp.qsize()
        pos=0
        while(pos<tsize):
          t=await temp.get()
          await player.queue.put(t)
          t2=await temp2.get()
          await player.searchqueue.put(t2)
          pos=pos+1
        #await now_playing_(ctx)
    else:
      source = await YTDLSource.create_source2(cls=None,ctx=ctx, search=search, loop=client.loop, download=False)
      #print(source)
      while(temp.qsize()>0):
        temp.get()
        temp2.get()
      #temp=asyncio.Queue()
      #temp2=asyncio.Queue()
      tsize=player.queue.qsize()
      while(tsize>0):
        t=await player.queue.get()
        t2=await player.searchqueue.get()
        await temp2.put(t2)
        await temp.put(t)
        tsize=tsize-1
      pos=0
      while(player.queue.qsize()>0):
        await player.queue.get()
        await player.searchqueue.get()
      #player.queue=asyncio.Queue()
      #player.searchqueue=asyncio.Queue()
      while(pos<position-1):
        t=await temp.get()
        await player.queue.put(t)
        t2=await temp2.get()
        await player.searchqueue.put(t2)
        pos=pos+1
      await player.queue.put(source)
      await player.searchqueue.put(source['webpage_url'])
      tsize=temp.qsize()
      pos=0
      while(pos<tsize):
        t=await temp.get()
        await player.queue.put(t)
        t2=await temp2.get()
        await player.searchqueue.put(t2)
        pos=pos+1
      #await now_playing_(ctx)
    #await ctx.message.delete()
    del player
    del vc
    del serr
    del list_ind
    del ind_ind
    del listt
    del temp_list
    del source
    del temp
    del l
    del tempp
    del t
    del t2
    del pos
    del temp2
  except Exception as e:
    #print('playyy',e)
    pass
  finally:
    pass
    #ctx_save[int(ctx.guild.id)][5].release()
  pass

#########################################

@commands.command(name='resume', aliases=['r','res'])
async def resume_(ctx):
  try:
    #vc = ctx.voice_client
    vc=discord.utils.get(client.voice_clients, guild=ctx.guild)
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
      pass
    #await ctx.message.delete()
    del vc
    del player
  except Exception as e:
    #print(e)
    pass
  pass

@commands.command(name='skip')
async def skip_( ctx):
  try:
    vc = ctx.voice_client
    player=None
    if not vc or not vc.is_connected():
      return #await ctx.send('I am not currently playing anything!', delete_after=10)

    if vc.is_paused():
      pass
    elif not vc.is_playing():
      return
    try:
      global ctx_save
      ctx_save[int(ctx.guild.id)][0]=0
      player=get_player(ctx)
      player.ispaused=0
      player.isautopaused=0
      await player.np.delete()
      await player.que.delete()
      #await ctx.message.delete()
    except Exception as e:
      #print("skip",e)
      pass
    await ctx.send(f'**`{ctx.author}`**: Skipped the song!',)
    vc.stop()
    del vc
    del player
  except Exception as e:
    #print(e)
    pass
  pass

@commands.command(name='queue_info', aliases=['q', 'playlist','queue'])
async def queue_info( ctx):
  try:
    player = get_player(ctx)
    await player.showw(ctx)
    del player
    #await ctx.message.delete()
  except Exception as e:
    #print(e)
    pass
  pass

@commands.command(name='now_playing', aliases=['np', 'current', 'currentsong', 'playing'])
async def now_playing_( ctx):
  try:
    player = get_player(ctx)
    if not player.current:
      return #await ctx.send('I am not currently playing anything!',delete_after=10)
    await player.showw(ctx)
    try:
      del player
    except Exception as e:
      pass
  except Exception as e:
    print(e)
    pass
  pass

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
    #await ctx.message.delete()
    del vc
    del player
  except Exception as e:
    #print(e)
    pass
  pass

@commands.command(name='stop')
async def stop_( ctx):
  vc = ctx.voice_client
  global ctx_save
  ctx_save[int(ctx.guild.id)][0]=0.0
  ctx_save[int(ctx.guild.id)][1]=0
  if not vc or not vc.is_connected():
    return #await ctx.send('I am not currently playing anything!', delete_after=10)
  try:
    player=get_player(ctx)
    player.ispaused=0
    player.isautopaused=0
    tsize=player.queue.qsize()
    while(tsize>0):
      await player.queue.get()
      await player.searchqueue.get()
      tsize=tsize-1
    #await ctx.message.delete()
    #await player.reset(ctx)
    #player.queue = asyncio.Queue()
    #player.searchqueue = asyncio.Queue()
    await skip_(ctx)
    await asyncio.sleep(2)
    ctx_save[int(ctx.guild.id)][2]=1
    #vc.stop()
    await player.np.delete()
    await player.que.delete()
  except Exception as e:
    #print("stop",e)
    pass
  try:
    del vc
    del tsize
  except Exception as e:
    pass
  #await cleanup(ctx.guild)
  pass

@commands.command(name='seek')
async def seek_( ctx, search: int):
  try:
    global ctx_save
    ctx_save[int(ctx.guild.id)][1]=1
    player=get_player(ctx)
    await player.seek(ctx)
    player.ispaused=0
    player.isautopaused=0
    vc=discord.utils.get(client.voice_clients, guild=ctx.guild)
    player.startt=datetime.now().timestamp()
    player.elapsed=search
    #print(timeestamp)
    ctx_save[int(ctx.guild.id)][0]=search
    #print(timeestamp)
    if not vc or not vc.is_connected():
      return #await ctx.send('I am not currently playing anything!', delete_after=10)
    vc.stop()
    try:
      del vc
      del player
    except Exception as e:
      print(e)
  except Exception as e:
    print(e)
    pass
  pass
@commands.command(name="pause", aliases=["pausee"])
async def pause_( ctx,pflag=0):
  try:
    #vc = ctx.voice_client
    vc=discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not vc or not vc.is_playing():
      return #await ctx.send('I am not currently playing anything!', delete_after=10)
    elif vc.is_paused():
      return
    player=get_player(ctx)
    if pflag==0:
      player.ispaused=1
    player.isautopaused=1
    await ctx.send(f'**`{ctx.author}`**: Paused the song!')
    try:
      player=get_player(ctx)
      player.stopt=datetime.now().timestamp()
      player.elapsed=player.elapsed+player.stopt-player.startt
      player.startt=datetime.now().timestamp()
      #await ctx.message.delete()
    except Exception as e:
      #print(e)
      pass
    vc.pause()
    await time_(ctx)
    #player.ispaused=True
    del vc
    del player
  except Exception as e:
    #print(e)
    pass
  pass

@commands.command(name="time", aliases=["timee"])
async def time_( ctx,sek=0):
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
    if sek==0:
      await now_playing_(ctx)
    #await ctx.message.delete()
    del vc
    del player
  except Exception as e:
    #print(e)
    pass
  pass
@commands.command(name='remove', aliases=['rem'])
async def remove_( ctx,index:int):
  global ctx_save
  try:
    await ctx_save[int(ctx.guild.id)][5].acquire()
    vc = ctx.voice_client
    if not vc or not vc.is_playing():
      return #await ctx.send('I am not currently playing anything!', delete_after=10)
    elif vc.is_paused():
      return
    player=get_player(ctx)
    tsize=None
    temp=None
    temp2=None
    t=None
    t2=None
    tflag=None
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
      tsize=player.queue.qsize()
      while(tsize>0):
        player.queue.get()
        player.searchqueue.get()
        tsize=tsize-1
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
      pass
    except Exception as e:
      #print(e)
      pass
    #await player.showw(ctx)
    await ctx.send(f'**`{ctx.author}`**: Removed the song!')
    #await ctx.message.delete()
    del vc
    del player
    del tsize
    del temp
    del temp2
    del t
    del t2
    del tflag
  except Exception as e:
    #print(e)
    pass
  finally:
    ctx_save[int(ctx.guild.id)][5].release()
  pass

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
    pass

"""

pass
@tasks.loop(seconds=7200)
async def autorestart():
  try:
    global players
    x=None
    ctx=None
    player=None
    for x in players:
      ctx=players[x].cttx
      player=get_player(ctx)
      await time_(ctx)
      await asyncio.sleep(2)
      await seek_(ctx,player.elapsed)
    #print('restarted')
    del x
    del ctx
    del player
  except Exception as e:
    #print('can not restart',e)
    pass
  pass

async def changepresence(ctx,message):
  status=message
  await client.change_presence(activity=discord.Streaming(platform='YouTube',name=status, url="https://www.youtube.com/watch?v=NHnT9NEuDWo"))
  await ctx.send('Daksh! Status Changed')
async def showram(ctx):
  try:
    process = psutil.Process(os.getpid())
    #print('mem ',process.memory_info().rss/1024**2)
    mem=process.memory_info().rss/1024**2
    mem='mem '+str(mem)+" "
    cpu=psutil.cpu_percent()
    mem=mem+str(cpu)
    await ctx.send(str(mem))
  except Exception as e:
    pass
  pass


async def clearramm(ctx):
  try:
    await showram(ctx)
    ctypes.CDLL('libc.so.6').malloc_trim(0)
    print(' ')
    print('bef',gc.get_count())
    gc.collect()
    print('aft',gc.get_count())
    await showram(ctx)
  except Exception as e:
    pass
  pass


@tasks.loop(seconds = 1800)
async def clearram():
  try:
    ctypes.CDLL('libc.so.6').malloc_trim(0)
    print(' ')
    print('bef',gc.get_count())
    gc.collect()
    print('aft',gc.get_count())
  except Exception as e:
    pass
#@tasks.loop(seconds = 10)
async def get_membersss():
  try:
    while True:
      try:
        await get_members()
        await asyncio.sleep(2)
      except Exception as e:
        pass
      finally:
        pass
      pass
    pass
  except Exception as e:
    pass
  pass
async def get_members():
  try:
    #print('bef',gc.get_count())
    #gc.collect()
    #print('aft',gc.get_count())
    #await asyncio.sleep(3)
    global players
    global ctx_save
    if players==None:
      return
    tempp=players.copy()
    x=None
    vc=None
    player=None
    ctx=None
    ii=None
    channel=None
    member_ids=None
    member=None
    channel_ids=None
    for x in tempp:
      try:
        player=players[x]
        if player.current==None:
          continue
        if player==None:
          continue
        ctx=players[x].cttx
        
        #player=get_player(ctx)
        
        vc=None
        ii=1
        vc=discord.utils.get(client.voice_clients, guild=ctx.guild)
        if vc==None:
          try:
            del ctx_save[int(x)]
            del players[x]
          except Exception as e:
            pass
          continue
        """
        while vc==None:
          ii=ii+1
          vc=discord.utils.get(client.voice_clients, guild=ctx.guild)
          if ii==50:
            break
        """
        #print('before,,',player.before)
        #print('after,,',vc.channel.id)
        if player.before!=vc.channel.id:
          #print('vc changed')
          await time_(ctx,1)
          await seek_(ctx,int(player.elapsed))
          player.before=vc
          #await asyncio.sleep(5)
        if player.ispaused==1:
          pass
        else:
          channel = vc.channel
          member_ids = channel.voice_states.keys()
          member_ids=len(member_ids)
          for key in channel.voice_states.keys():
            member=await ctx.guild.fetch_member(key)
            #print(member.bot)
            if member.bot:
              member_ids=member_ids-1
          
          if vc.is_playing():
            if(member_ids==0):
              #print(len(member_ids))
              await pause_(ctx,1)
          elif vc.is_paused():
            if(member_ids>0):
              if player.ispaused==1:
                continue
              await time_(ctx,1)
              await seek_(ctx,int(player.elapsed))
              #await resume_(ctx)
          #print(member_ids)
          pass
      except Exception as e:
        print('inner ',e)
        pass
    del player
    del tempp
    del ii
    del vc
    del channel
    del channel_ids
    del member
    del x
    del ctx
  except Exception as e:
    print('outer ',e)
    pass
  pass


#@tasks.loop(seconds = 60)
#async def sav():
#  global ctx_data_flag
#  await asyncio.sleep(70)
#  global temp_ctx
#  await save_(temp_ctx)
##################    load
#from guppy import hpy

async def memory(ctx):
  pass

async def ping(ctx):
    await ctx.send(f'Ping is {round(client.latency * 1000)} ms')

@client.event
async def on_message(message):
  try:
    #counterr=0
    #tio=4
    ctx = await client.get_context(message)
    player=get_player(ctx)
    ########### critical
    #
    global ctx_save
    ############
    #ctx=None
    msg=None
    chanell=None
    channel_id=None
    #player=None
    second=None
    third=None
    multiline=[]
    tmultiline=""
    #
    channell = discord.utils.get(ctx.guild.channels, name='d-songs')
    channel_id = channell.id
    resflag=0
    #
    try:
      if message.author == client.user:
        return
      vc=None
      vc=discord.utils.get(client.voice_clients, guild=ctx.guild)
      if vc==None:
        resflag=1
      if resflag!=1:
        channelll = vc.channel
        member_ids = channelll.voice_states.keys()
        member_ids=len(member_ids)
        for key in channelll.voice_states.keys():
          member=await ctx.guild.fetch_member(key)
          if member.bot:
            member_ids=member_ids-1
        if(member_ids==0):
          resflag=1
      #del vc
    except Exception as e:
      resflag=1
      pass
    if resflag==0:
      try:
        if message.content.lower().startswith(';') or message.channel.id==channel_id:
          if message.author == client.user:
            #print("here")
            return
          try:
            if message.author.id!=356012950298951690:
              try:
                channel = ctx.author.voice.channel
              except Exception as e:
                await ctx.send("Someone is already listening songs")
                return
              if channel.id!=ctx.voice_client.channel.id:
                await ctx.send("Someone is already listening songs")
                return
          except Exception as e:
            pass
      except Exception as e:
        #print(e)
        pass
    #print(resflag)
    msg=str(message.content)
    #
    """
    ##############critical
    if message.content.lower().startswith(';') or ctx.message.channel.id==channel_id or message.author != client.user:
      counterr=0
      while(ctx_save[int(ctx.guild.id)][4]!=0):
        await asyncio.sleep(10)
        counterr=counterr+1
        print(ctx_save[int(ctx.guild.id)][4])
        if(counterr==10):
          tio=4
          tio=10/0
    ctx_save[int(ctx.guild.id)][4]=ctx_save[int(ctx.guild.id)][4]+1
    """
    #################
    #
    try:
      if message.content.lower().startswith(';playy') or message.content.lower().startswith(';play'):
        second = msg.split(' ', 1)[1]
        await play_(ctx,second)
        await now_playing_(ctx)
      elif message.content.lower().startswith(';connect') or message.content.lower().startswith(';join'):
        #second = msg.split(' ', 1)[1]
        await ctx.invoke(connect_)
      elif message.content.lower().startswith(';resume') or message.content.lower().startswith(';resumee'):
        #second = msg.split(' ', 1)[1]
        await time_(ctx,1)
        await seek_(ctx,int(player.elapsed))
        #await resume_(ctx)
      elif message.content.lower().startswith(';skip'):
        #second = msg.split(' ', 1)[1]
        await skip_(ctx)
      elif message.content.lower().startswith(';np') or message.content.lower().startswith(';now_playing'):
        #second = msg.split(' ', 1)[1]
        await now_playing_(ctx)
      elif message.content.lower().startswith(';vol') or message.content.lower().startswith(';volume'):
        second = msg.split(' ', 1)[1]
        second=float(second)
        await change_volume(ctx,second)
      elif message.content.lower().startswith(';ping'):
        await ping(ctx)
      elif message.content.lower().startswith(';showram'):
        if message.author.id==356012950298951690:
          await showram(ctx)
      elif message.content.lower().startswith(';changepresence'):
        if message.author.id==356012950298951690:
          second = msg.split(' ', 1)[1]
          await changepresence(ctx,second)
      elif message.content.lower().startswith(';stop'):
        #second = msg.split(' ', 1)[1]
        await stop_(ctx)
      elif message.content.lower().startswith(';clearram'):
        if message.author.id==356012950298951690:
          await ctx.send('System ram cleared',delete_after=10)
          await clearramm(ctx)
      elif message.content.lower().startswith(';memory'):
        if message.author.id==356012950298951690:
          await ctx.send('Ram',delete_after=10)
          await memory(ctx)
      elif message.content.lower().startswith(';exit'):
        #second = msg.split(' ', 1)[1]
        if message.author.id==356012950298951690:
          await ctx.send('System exit initiated',delete_after=10)
          await exitt()
      elif message.content.lower().startswith(';seek'):
        second = msg.split(' ', 1)[1]
        second=int(second)
        await seek_(ctx,second)
      elif message.content.lower().startswith(';help'):
        #second = msg.split(' ', 1)[1]
        msgg='@24/7 BOT \nIT AUTOMATICALLY PAUSES SONG WHEN VC IS EMPTY AND RESUMES IT WHEN SOMEONE JOINS \nCREATE A CHANNEL BY THE NAME OF ,d-songs,CASE SENSITIVE (IMPORTANT STEP),\n NO NEED TO WRITE ;PLAY IN d-songs CHANNEL, WRITE NAME OR LINK DIRECTLY, \nPlease do no edit permission, It breaks working of Bot, \nPermissions required-send msg, manage channel,use reactions, gifs,manage message,connect,speak. \n'
        msgg=msgg+' PLAYLISTS ARE ALSO SUPPORTED, ONLY 10 SONGS \nUSE REACTIONS EMOJI TO PLAY PAUSE SKIP OR STOP SONGS \n;rem 1 2 3, it will remove 1 2 and 3rd song from list\n;skip, to skip\n;pause, to pause\n;resume, or ;res to resume\n'
        msgg=msgg+';stop, to stop\n;invite to see bot invite link\n;seek, to seek (in seconds)\n;ping, to check ping\n;vol or ;volume, to change volume 1-100\n;np, to check now play but it is automatic\n;ins songname position, to insert song at particular position\n;time to check elapsed time of current song\n'
        msgg=msgg+'\n\n IF YOU HAVE ANY DOUBT OR ANY FUNCTION IS NOT WORKING PROPERLY, CONTACT ME ON INSTA- daksh2998'
        await ctx.send(msgg)
        await ctx.send('My discord server invite link: https://discord.gg/tPDUcFs9Et')
      elif message.content.lower().startswith(';invite'):
        msgg='24/7 Bot invite link is https://discord.com/api/oauth2/authorize?client_id=827290129004494878&permissions=1609952369&scope=bot'
        await ctx.send(msgg)
      elif message.content.lower().startswith(';pause'):
        #second = msg.split(' ', 1)[1]
        await pause_(ctx)
      elif message.content.lower().startswith(';insert') or message.content.lower().startswith(';ins'):
        second = msg.split(' ', 1)[1]
        third=second.split(' ', -1)[-1]
        second=second.split(' ', -1)
        second.pop()
        second=" ".join(second)
        #print(second)
        third=int(third)
        #print('third',third)
        #player=get_player(ctx)
        if player.queue.qsize()==0 or third==0:
          #print(player.queue.qsize())
          await play_(ctx,second)
        else:
          await insert_(ctx=ctx,search=second,position=third)
        await now_playing_(ctx)
      elif message.content.lower().startswith(';rem') or message.content.lower().startswith(';remove'):
        second = msg.split(' ', 1)[1]
        second=second.split(' ')
        #print(second)
        i=0
        for x in second:
          x=int(x)
          x=x-i
          i=i+1
          await remove_(ctx,x)
        await player.showw(ctx)
      elif message.content.lower().startswith(';time'):
        #second = msg.split(' ', 1)[1]
        await time_(ctx)
      elif message.content.lower().startswith(';save'):
        #second = msg.split(' ', 1)[1]
        #await save_(ctx)
        pass
      elif message.content.lower().startswith(';'):
        pass
      elif ctx.message.channel.id==channel_id:
        if message.author != client.user:
          player.cttx=ctx
          #print('a')\
          multiline=message.content.splitlines()
          print(multiline)
          for tmultiline in multiline:
            await play_(ctx,str(tmultiline))
          await now_playing_(ctx)
      if message.content.lower().startswith(';'):
        player.cttx=ctx
      #del ctx
    except Exception as e:
      pass
    finally:
      #ctx_save[int(ctx.guild.id)][4]=ctx_save[int(ctx.guild.id)][4]-1
      pass
    del msg
    del chanell
    del channel_id
    del player
    del second
    del third
    del resflag
    #del counterr
    #del tio
    del ctx
    del multiline
    del tmultiline
    #del player
  except Exception as e:
    print(e)
    pass
  finally:
    #ctx_save[int(ctx.guild.id)][4]=ctx_save[int(ctx.guild.id)][4]-1
    try:
      pass
      """
      del ctx
      del player
      del tio
      del msg
      del chanell
      del channel_id
      del player
      del second
      del third
      del resflag
      """
      pass
    except Exception as e:
      pass
    pass
  pass


async def exitt():
  sys.exit("Exit")

@client.event
async def on_reaction_add(reaction, user):
  global ctx_save
  ctx = await client.get_context(reaction.message)
  try:
    #await ctx_save[int(ctx.guild.id)][5].acquire()
    #counterr=0
    #tio=4
    #############critical
    
    player=get_player(ctx)
    #print(ctx.author)
    ###################
    if user == client.user:
      return
    #
    if ctx.author!=client.user:
      return
    ctx.author=player.cttx.author
    #print('rr')
    try:
      if user.id!=356012950298951690:
        try:
          channel = user.voice.channel
        except Exception as e:
          await ctx.send("Someone is already listening songs")
          return
        if channel.id!=ctx.voice_client.channel.id:
          await ctx.send("Someone is already listening songs")
          #del ctx
          return
    except Exception as e:
      pass
    #
    channell = discord.utils.get(ctx.guild.channels, name='d-songs')
    channel_id = channell.id
    #player=get_player(ctx)
    if reaction.message.channel.id == channel_id:
      #critical
      #player.cttx=ctx
      await ctx.send(f'**`{user}`**: Reacted!')
      #
      #counterr=0
      ############critical
      """
      while(ctx_save[int(ctx.guild.id)][4]!=0):
        await asyncio.sleep(10)
        counterr=counterr+1
        if(counterr==10):
          tio=4
          tio=10/0
        pass
      """
      try:
        #ctx_save[int(ctx.guild.id)][4]=ctx_save[int(ctx.guild.id)][4]+1
        ####
        #print(reaction.emoji)
        if str(reaction.emoji) =='⏯️':
          await ctx.send(f'**`{user}`**: Resumed Song!')
          #print('play rr')
          await time_(ctx,1)
          await seek_(ctx,int(player.elapsed))
          #await resume_(ctx)
          #await player.showw(ctx)
        elif str(reaction.emoji) =='⏸️':
          #print('paused')
          await pause_(ctx)
          #await player.showw(ctx)
        elif reaction.emoji =='⏭️':
          await skip_(ctx)
          #await player.showw(ctx)
        elif reaction.emoji =='⏹️':
          await stop_(ctx)
        elif reaction.emoji=='⌚':
          await time_(ctx)
      except Exception as e:
        pass
      finally:
        #ctx_save[int(ctx.guild.id)][4]=ctx_save[int(ctx.guild.id)][4]-1
        pass
    #del ctx
    del channell
    del channel_id
    del player
    #del counterr
    #del tio
  except Exception as e:
    #e)
    pass 
  finally:
    #ctx_save[int(ctx.guild.id)][5].release()
    #ctx_save[int(ctx.guild.id)][4]=ctx_save[int(ctx.guild.id)][4]-1
    try:
      #del counterr
      #del ctx
      #del tio
      #del player
      #del channell
      #del channel_id
      pass
    except Exception as e:
      pass
    pass
  pass
#client.load_extension('music')
keep_alive()

#my_secret = os.environ['token']
#client.run(str(my_secret))\

client.run(os.environ.get('token'))
#client.run("")

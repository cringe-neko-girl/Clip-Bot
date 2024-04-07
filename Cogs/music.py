import os
# Assign Task
import time
import random
import shutil

# Discord Import
import discord
from discord.ext import commands

# Youtube Import
from yt_dlp import YoutubeDL


# Music Class
class Music(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.music_queue = []
    self.current_song = None
    self.current_song_index = -1
    self.repeat = False

    self.voice_client = None

  @commands.Cog.listener()
  async def on_ready(self):
    await self.bot.change_presence(status=discord.Status.idle,activity=discord.Activity(type=discord.ActivityType.watching, name="You 👀 "))
    print("Music.py is ready!")

  def search(self, query: str, ctx):
   
    ydl_opts = {
     'format': 'bestaudio/best',
     'restrictfilenames': True,
     'noplaylist': True,
     'nocheckcertificate': True,
     'ignoreerrors': False,
     'logtostderr': False,
     'no_warnings': True,
     'default_search': 'auto',
     'source_address': '0.0.0.0',
     'quiet': True,
     'extract_flat': True,
     'audioquality': '4',  # Best audio quality
     'max_downloads': 100,  # Adjust as needed

    }


    if query.startswith("https://"):  # check if the query is a link
      with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)

        if 'entries' in info:  # if the link is a playlist link, it'll have entries
          entries = info['entries']
          return [{
              'thumbnail_url': entry['thumbnails'][0]['url'],
              'title': entry['title'],
              'source': entry['url'],
              'user_req': ctx.author
          } for entry in entries if entry['title'] != "[Deleted video]"]

        else:
          return [{
              'thumbnail_url': info['thumbnail'],
              'title': info['title'],
              'source': info['url'],
              'user_req': ctx.author
          }]

    else:  # if not then search
      with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch{4}:{query}", download=False)
        entries = info['entries']
        return [{
            'thumbnail_url': entry['thumbnails'][0]['url'],
            'title': entry['title'],
            'source': entry['url'],
            'user_req': ctx.author
        } for entry in entries]

  @commands.command(name="play",
                    help="play < song name or url > Play any song from Youtube")
  async def play(self, ctx, *args):
    """Plays a song from youtube"""
    if not ctx.author.voice:
      await ctx.send("You are not in a voice channel!")
    
  

    if self.voice_client is None:
      self.voice_client = await ctx.author.voice.channel.connect()


    # Search the song
    query = " ".join(args)

    message = await ctx.send("> `Searching...` 🔎")
    result = self.search(query, ctx)
    await message.delete()

    if not result:
      await ctx.send("> `No results found ?` ❌")
      return

    if query.startswith("https://") and len(result) > 1:  # Playlist
      await ctx.send("> `Found playlist, add songs to queue` ✅")
      for entry in result:
        self.music_queue.append(entry)

    if query.startswith("https://") and len(result) == 1:  # Single Link
      await ctx.send(f"> `Found {result[0]['title']}, adding to queue` ✅")
      self.music_queue.append(result[0])

    if not query.startswith("https://"):  # Search and Choose | By Number
      embed = discord.Embed(
          title="Song Selection",
          color=discord.Color.blue(
          )  # ctx.guild.get_member(self.bot.user.id).color
      )

      embed.set_thumbnail(url=self.bot.user.avatar.url)
      embed.set_footer(text="Choose a song: 1-4",
                       icon_url=self.bot.user.avatar)

      for i, entry in enumerate(result):
        embed.add_field(name=f"> `{i+1}`. `{entry['title']}`",
                        value=f"- Source: {entry['source']}",
                        inline=False)

      message = await ctx.send(embed=embed)

      def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

      try:
        response = await self.bot.wait_for("message", check=check, timeout=15)

        if response.content.lower() == "c":
          await message.delete()
          await ctx.send("> `Canceled Search`")
          await response.delete()  # Move this line inside the try block
          return  # Cancel the operation
        
        
        picked = 1 if not response.content else int(response.content)
        choice = int(picked) - 1
        if 0 <= choice < len(result):
          await message.delete()
          await ctx.channel.purge(limit=1)
          await ctx.send(
              f"> `{ctx.author.name}` picked `{result[choice]['title']}`")
          self.music_queue.append(result[choice])
          # Inside the play command
          try:
             await self.play_music(ctx)
          except Exception as e:
             await ctx.send(f"An error occurred while playing the song: {e}")
        
          # Inside the nowplaying command
          try:
              await self.nowplaying(ctx)
          except Exception as e:
             await ctx.send(f"An error occurred while displaying the currently playing song: {e}")

          await self.bot.change_presence(status=discord.Status.idle, activity=discord.Game(name=f"{result[choice]['title']}"))



        else:
          await ctx.send(
              "> Choice must be from options: `1 - 4`. Type 'c' to cancel.")
          return  # Cancel the operation

      except ValueError:
        await ctx.send(
            "> Choice must be from options: `1 - 4`, Type **Number**. Type 'c' to cancel."
        )

      except TimeoutError:
        await ctx.send("> `It seems you took too long to respond. Choosing the first result.`")

        # Choose the first result as a default
        choice = 0

        await message.delete()

        await ctx.send(
            f"> `{ctx.author.name}` picked `{result[choice]['title']}`"
        )
    
        self.music_queue.append(result[choice])
        await self.play_music(ctx)
        await self.nowplaying(ctx)

        await self.bot.change_presence(
          status=discord.Status.idle,
          activity=discord.Game(name=f"{result[choice]['title']}"),
        )
        try:
          await self.play_music(ctx)
        except Exception as e:
          print(e)

  async def play_music(self, ctx):
    # loop function to check for entry in que and play
    if self.voice_client.is_playing():
      return

    if self.current_song_index + 2 <= len(self.music_queue):
      self.current_song_index = self.current_song_index + 1
      self.current_song = self.music_queue[self.current_song_index]

      ydl_opts = {
          'format': 'bestaudio',
          'quiet': True,
          'source_address': '0.0.0.0',  # Set the source address
          'extract_flat': False,
      }
      ffmpeg_path = '/usr/bin/ffmpeg'
      path = os.path.abspath(ffmpeg_path)

      ffmpeg_opts = {
       'options': '-vn',
       # Disable video processing, use Opus codec for audio, set bitrate to 128k, compression level 10, and optimize for audio
       'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
       'executable': path  # Specify the path to FFmpeg executable

       }
       
        


      with YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url=self.current_song['source'],
                                  download=False)
      source = discord.FFmpegPCMAudio(result['url'], **ffmpeg_opts)

     
      self.voice_client.play(
          source,
          after=lambda e: self.bot.loop.create_task(self.play_music(ctx)))



    else:
      if self.repeat:
        self.current_song_index = -1
        await self.play_music(ctx)

      else:
        self.current_song_index = -1
        self.music_queue = []
        await self.bot.change_presence(status=discord.Status.idle,activity=discord.Activity(type=discord.ActivityType.listening, name=";help"))

        self.voice_client = await self.voice_client.disconnect()
  
  def get_next_song(self):
        if len(self.music_queue) > 1:
            # Return the second song in the queue (index 1)
            return self.music_queue[1]
        else:
            return None

  # Embed  | Current song title playing with the youtube image set
  async def nowplaying(self, ctx: commands.Context):
    try:
        if self.current_song is None:
            await ctx.send("No song is currently playing.")
            return

        # Get information about the next song
        next_song = self.get_next_song()
        next_song_title = next_song['title'] if next_song else "No upcoming songs"

        # Design your embed here
        embed = discord.Embed(
            title=f"Now Playing:",
            description=f"```{self.current_song['title']}```",
            color=discord.Color.from_rgb(255, 192, 203)  # Light Pink color

        )

        embed.set_image(url=self.current_song['thumbnail_url'])
        embed.set_footer(icon_url=ctx.message.author.avatar, text=f"Playing for {ctx.message.author.name}")

        # Add information about the next song
        embed.add_field(name="Next Song:", value=f"```{next_song_title}```", inline=False)

    
        await ctx.send(embed=embed, view=MusicButton(self, ctx))
    except Exception as e:
        print(f"An error occurred: {e}")
 
  @commands.command(name='nowplaying', aliases=['np'])
  async def nowplaying_command(self, ctx: commands.Context):
    if not ctx.author.voice:
        await ctx.reply("You are not in a `voice channel`.")
        return
    
    try:
        # Check if there is a currently playing song
        if self.current_song is None:
            await ctx.send("No song is currently playing.")
            return

        # Get information about the currently playing song
        current_song_title = self.current_song['title']

        # Get information about the next song
        next_song = self.get_next_song()
        if next_song:
            next_song_title = next_song['title']
        else:
            next_song_title = "No upcoming songs"

        # Design your "now playing" embed here
        embed = discord.Embed(
            title="Now Playing",
            description=f"```{current_song_title}```",
            color=discord.Color.green()  # Adjust color to match your bot theme
        )

        embed.set_image(url=self.current_song['thumbnail_url'])
        embed.add_field(name="Next Song", value=f"```{next_song_title}```", inline=False)
        embed.set_footer(icon_url=ctx.message.author.avatar, text=f"Playing for {ctx.message.author.name}")

        # Send the embed
        message = await ctx.send(embed=embed,view=MusicButton(self, ctx))

    except Exception as e:
        # Handle exceptions and inform the user
        await ctx.send(f"An error occurred: {e}")


  # Pauses currrent song
  async def toggle_pause(self):
    if self.voice_client.is_playing():
      self.voice_client.pause()
    else:
      self.voice_client.resume()

  async def toggle_repeat(self):
    self.repeat = not self.repeat

  async def skip(self):
    self.voice_client.stop()

  # Stops current song playing  
  async def stop(self):
    self.music_queue = []
    await self.voice_client.stop()

  async def shuffle(self):
    if self.music_queue:
      random.shuffle(self.music_queue)
    
  """
  @commands.command(name='playall', aliases=['pa'])
  async def playall_command(self,ctx: commands.Context):
    # Check if there are items in the search result list
    if not self.search_results:
        await ctx.send("There are no search results to play.")
        return

    # Clear the existing music queue
    self.music_queue = []

    # Add all search results to the queue
    self.music_queue.extend(self.search_results)

    # Clear the search result list
    self.search_results = []

    # Play the first item in the queue
    await self.play_music(ctx)

    # Display the now playing message
    await self.nowplaying(ctx)
  """
    
    
    
  def get_queue_songs(self):
        if len(self.music_queue) > 1:
            # Return all songs in the queue starting from index 1
            return self.music_queue[1:]
        else:
            return []  
    
  @commands.command(name='queue', aliases=['q'])
  async def queue_command(self, ctx: commands.Context):
    try:
        print("Working Queue :3")
        # Check if there are items in the queue
        if not self.music_queue:
            await ctx.send("The queue is empty.")
            return

        # Get all upcoming songs in the queue
        next_songs = self.get_queue_songs()

        # Check if there are no upcoming songs
        if not next_songs:
            await ctx.send("There are no upcoming songs in the queue.")
            return

        # Design your queue list embed here
        embed = discord.Embed(
            title="Music Queue",
            color=discord.Color.blue()  # Adjust color to match your bot theme
        )

        # Add fields for each upcoming song
        for index, song in enumerate(next_songs, start=1):
            embed.add_field(name=" ",value=f"```{index}. {song['title']}```", inline=False)

        await ctx.send(embed=embed)

    except Exception as e:
        # Handle exceptions and inform the user
        await ctx.send(f"An error occurred: {e}")









class MusicButton(discord.ui.View):
  def __init__(self, music_class: Music, ctx: commands.Context, timeout=None):
    super().__init__(timeout=timeout)

    self.music_class = music_class
    self.ctx = ctx

    # Initiate Button Pause Label
    # self.children[0].label = "Pause" if self.music_class.voice_client.is_playing() else "Resume"

    # Initiate Button Repeat Label
    # self.children[1].label = "Repeat On" if self.music_class.repeat else "Repeat Off"
    # self.children[1].style =  you can change style if you want
  
  #design your buttons

  # Embed  | Current song title playing with the youtube image set
  async def nowplaying(self, ctx: commands.Context):
    try:
        if self.current_song is None:
            await ctx.send("No song is currently playing.")
            return

        # Check if there are upcoming songs in the queue
        if len(self.music_queue) > 1:
            next_song = self.music_queue[1]
            next_song_title = next_song['title']
        else:
            next_song_title = "No upcoming songs"

        # Design your embed here
        embed = discord.Embed(
            title="Now Playing",
            description=f"```{self.current_song['title']}```",
            color=discord.Color.green()  # Adjust color to match your bot theme
        )

        embed.set_image(url=self.current_song['thumbnail_url'])
        embed.add_field(name="Next Song", value=f"```{next_song_title}```", inline=False)
        embed.set_footer(icon_url=ctx.message.author.avatar, text=f"Playing for {ctx.message.author.name}")

        await ctx.send(embed=embed)

    except Exception as e:
        # Handle exceptions and inform the user
        await ctx.send(f"An error occurred: {e}")


    except Exception as e:
        # Handle exceptions and inform the user
        await ctx.send(f"An error occurred: {e}")

 
  @discord.ui.button(
    label= "Pause",
    style=discord.ButtonStyle.primary,
  )
  async def toggle_pause(self, interaction: discord.Interaction, button: discord.ui.Button):
    if not interaction.user.voice:
            await interaction.response.send_message("You are not in a voice channel bro?", ephemeral=True)
            return
    await self.music_class.toggle_pause()
    button.emoji = "<:pause2:1176772089764651009>" if self.music_class.voice_client.is_playing() else "<:resume:1176772087059316858>"

    await interaction.response.edit_message(view=self)

  
  @discord.ui.button(
    label= "Repeat",
    style=discord.ButtonStyle.primary,
  )
  async def toggle_repeat(self, interaction: discord.Interaction, button: discord.ui.Button):
    if not interaction.user.voice:
            await interaction.response.send_message("You are not in a voice channel bro?", ephemeral=True)
            return
    await self.music_class.toggle_repeat()
    self.children[1].style = discord.ButtonStyle.green if self.music_class.repeat else discord.ButtonStyle.primary
    await interaction.response.edit_message(view=self)
  
  @discord.ui.button(
    label= "Skip",
    style=discord.ButtonStyle.primary,
   )
  async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
    if not interaction.user.voice:
      await interaction.response.send_message("My apologises, but your are not in a voice channel.", ephemeral=True)
      return
    try:
        # Get information about the user who skipped
        skipper_name = interaction.user.name
        skipper_avatar_url = interaction.user.avatar

        # Skip the current song
        await self.music_class.skip()

        # Send an embed indicating who skipped and include the now playing information
        await interaction.response.send_message(
            embed=discord.Embed(
                title=f"{skipper_name} skipped the song!",
                color=discord.Color.red(),  # Adjust color to match your bot theme
            ).set_thumbnail(url=skipper_avatar_url)
        )

        # Wait for a moment to ensure the skip operation is complete
        await asyncio.sleep(1)

        # Update the now playing information
        await Music.nowplaying(ctx)

        await self.music_class.nowplaying(self.ctx)
        

    except Exception as e:
        # Handle exceptions and inform the user
        await interaction.response.send_message(f"An error occurred: {e}")

    except Exception as e:
        # Handle exceptions and inform the user
        await interaction.response.send_message(f"An error occurred: {e}")
  
  @discord.ui.button(
    label="Stop",
    style=discord.ButtonStyle.danger,
  )
  async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
    try:
        # Check if the user is in a voice channel
        if not interaction.user.voice:
            await interaction.response.send_message("You are not in a voice channel bro?", ephemeral=True)
            return

        # Get the name and avatar of the user who stopped the music
        stopper_name = interaction.user.name
        stopper_avatar_url = interaction.user.avatar

        # Stop the music
        await self.music_class.stop()

        # Create an ephemeral embed indicating the music has been stopped
        stop_embed = discord.Embed(
            title="Music Stopped",
            description=f"Music has been stopped by {stopper_name}!",
            color=discord.Color.red(),  # Adjust color to match your bot theme
        )
        stop_embed.set_thumbnail(url=stopper_avatar_url)  # Set user's avatar as thumbnail

        # Send the ephemeral embed
        await interaction.response.send_message(embed=stop_embed, ephemeral=True)

    except Exception as e:
        # Handle exceptions and inform the user
        await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)
    
async def setup(bot):
  await bot.add_cog(Music(bot))
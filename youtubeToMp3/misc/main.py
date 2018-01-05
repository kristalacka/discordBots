from __future__ import unicode_literals
import youtube_dl

ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s', 'quiet':True, 'ignoreerrors': True,})
yt_url = "https://www.youtube.com/playlist?list=PLz_Nf9rhWA3pMShjidf3uYFsVfijGrHjw"

vid_list=[]
with ydl:
    result = ydl.extract_info \
    (yt_url,
     download=False) #We just want to extract the info

    if 'entries' in result:
        # Can be a playlist or a list of videos
        video = result['entries']

        #loops entries to grab each video_url
        for i, item in enumerate(video):
            vid_list.append(result['entries'][i]['webpage_url'])
      
ydl_opts = {
    'format': 'bestaudio/best',
    'ignoreerrors': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    try:
        ydl.download(vid_list)
    except:
        pass

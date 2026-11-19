"""3D animated Turkish Shorts. PRIVATE only, uploads disabled until explicit setup."""
import asyncio, json, math, os, pathlib, subprocess, sys, tempfile, datetime
from zoneinfo import ZoneInfo
from PIL import Image,ImageDraw,ImageFont
ROOT=pathlib.Path(__file__).resolve().parent
STORIES=[
 ('Mırmır ve Gizemli Düğme','Mırmır bu sabah ofiste kırmızı bir düğme buldu.|Merakına yenildi ve düğmeye basınca ekranda yeni patron geldi yazdı.|Herkes şaşkındı. Mırmır kendini bir anda müdür zannetmeye başladı.|Meğer düğme kahve makinesini çalıştırıyormuş. Bugünün gerçek patronu kahveydi!'),
 ('Kedi Patronun İlk Toplantısı','Ofiste bugünkü toplantının başkanı Mırmır seçildi.|Mırmır bilgisayarı açtı. Ekranda kocaman bir ton balığı fotoğrafı belirdi.|Herkes sunumun sırrını çözmeye çalışırken Mırmır ciddi ciddi başını salladı.|Meğer bu bir iş planı değil, öğle yemeği sipariş listesiymiş!'),
 ('Ofisin Kayıp Telefonu','Mırmır ofiste telefonunu bulamıyordu. Bütün masalara baktı.|Çekmeceler açıldı, bilgisayarlar kapatıldı. Telefon hiçbir yerde yoktu.|Tam vazgeçecekken masasından tanıdık bir zil sesi yükseldi.|Telefon zaten kendi oturduğu minderin altındaydı. Mırmır bütün gün onu aramıştı!')
]
def run(*command):
 p=subprocess.run(list(map(str,command)),text=True,capture_output=True)
 if p.returncode:raise RuntimeError(p.stderr[-2000:])
 return p.stdout.strip()
def length(p):return float(run('ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',p))
async def say(text,path):
 import edge_tts
 await edge_tts.Communicate(text,os.getenv('TTS_VOICE','tr-TR-EmelNeural'),rate='+0%').save(str(path))
 if not path.exists() or path.stat().st_size<5000 or length(path)<1.5:raise RuntimeError('Turkish neural voice unavailable. Upload aborted.')
def caption(text,path):
 im=Image.new('RGBA',(720,1280),(0,0,0,0));d=ImageDraw.Draw(im)
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',40)
 words=text.upper().split();lines=[];line=[]
 for word in words:
  if len(' '.join(line+[word]))>23 and line:lines.append(' '.join(line));line=[]
  line.append(word)
 if line:lines.append(' '.join(line))
 if len(lines)>5:raise ValueError('Caption too long: quality gate stops publication')
 top=950-len(lines)*32
 d.rounded_rectangle((35,top-20,685,top+len(lines)*65+18),radius=30,fill=(8,14,30,230))
 for i,text in enumerate(lines):
  bbox=d.textbbox((0,0),text,font=font,stroke_width=2)
  d.text(((720-(bbox[2]-bbox[0]))/2,top+i*65),text,font=font,fill='white',stroke_width=2,stroke_fill=(0,0,0))
 im.save(path)
def upload_private(path,title):
 from google.oauth2.credentials import Credentials
 from google.auth.transport.requests import Request
 from googleapiclient.discovery import build
 from googleapiclient.http import MediaFileUpload
 required=('YOUTUBE_CLIENT_ID','YOUTUBE_CLIENT_SECRET','YOUTUBE_REFRESH_TOKEN')
 if any(not os.getenv(k) for k in required):raise RuntimeError('YouTube OAuth missing, no upload')
 cred=Credentials(token=None,refresh_token=os.environ['YOUTUBE_REFRESH_TOKEN'],token_uri='https://oauth2.googleapis.com/token',client_id=os.environ['YOUTUBE_CLIENT_ID'],client_secret=os.environ['YOUTUBE_CLIENT_SECRET'],scopes=['https://www.googleapis.com/auth/youtube.upload'])
 cred.refresh(Request())
 client=build('youtube','v3',credentials=cred,cache_discovery=False)
 body={'snippet':{'title':title[:75]+' #Shorts','description':'Özgün kurgu 3D komedi animasyonu #Shorts','categoryId':'24'},'status':{'privacyStatus':'private','selfDeclaredMadeForKids':False}}
 request=client.videos().insert(part='snippet,status',body=body,media_body=MediaFileUpload(str(path),resumable=True,mimetype='video/mp4',chunksize=5*1024*1024))
 response=None
 while response is None:_,response=request.next_chunk()
 print('PRIVATE upload:',response.get('id'))
def story():
 today=datetime.datetime.now(ZoneInfo('Europe/Istanbul')).date()
 # Built-in stories are strictly for previews, not repeated daily publication.
 if not os.getenv('GROQ_API_KEY'):
  if os.getenv('ENABLE_UPLOAD')=='true':
   raise RuntimeError('GROQ_API_KEY required for original daily stories. Upload aborted.')
  title,raw=STORIES[today.toordinal()%len(STORIES)]
  return title,raw.split('|')
 import requests
 history_path=ROOT/'history.json'
 history=json.loads(history_path.read_text()) if history_path.exists() else []
 past=[x.get('title','') for x in history[-30:]]
 prompt=('Türkçe, özgün ve aile dostu komik 3D kısa hikâye oluştur. Ana karakter Mırmır adlı turuncu kedi. '
         'Bütün sahneler aynı modern ofiste geçsin; görsel olarak yalnızca kedi, masa, ekran ve ofis var. '
         'Dört kısa anlatıcı sahnesi yaz. Her sahne 8-15 kelime, toplam 40-60 kelime. '
         'Başta dikkat çekici olay, sonda sürpriz ve eğlenceli sonuç. '
         'Şiddet, bahis, telifli karakter ve yetişkin içeriği olmasın. '
         'Yalnızca JSON: {"title":"...", "scenes":["...","...","...","..."]}. '
         'Son başlıkları tekrarlama: '+json.dumps(past,ensure_ascii=False))
 for attempt in range(3):
  try:
   response=requests.post('https://api.groq.com/openai/v1/chat/completions',
    headers={'Authorization':'Bearer '+os.environ['GROQ_API_KEY']},
    json={'model':'openai/gpt-oss-20b',
          'messages':[{'role':'system','content':'Yalnızca geçerli JSON üret.'},
                      {'role':'user','content':prompt}],
          'response_format':{'type':'json_object'},'max_completion_tokens':1000,
          'temperature':.95},timeout=90)
   response.raise_for_status()
   data=json.loads(response.json()['choices'][0]['message']['content'])
   scenes=data['scenes'];title=str(data['title'])[:75]
   if len(scenes)!=4 or any(not 7<=len(str(x).split())<=17 for x in scenes):raise ValueError('Invalid scene structure')
   if title.casefold() in [str(x).casefold() for x in past]:raise ValueError('Repeated title')
   return title,[str(x) for x in scenes]
  except Exception as exc:
   if attempt==2:raise RuntimeError('Original story generation failed; no upload') from exc
 raise RuntimeError('Story generation failed')
def main():
 date=datetime.datetime.now(ZoneInfo('Europe/Istanbul')).date()
 title,scenes=story()
 with tempfile.TemporaryDirectory(prefix='shorts3d_') as tmp:
  tmp=pathlib.Path(tmp);files=[]
  for index,text in enumerate(scenes):
   voice=tmp/f'voice{index}.mp3'
   asyncio.run(say(text,voice))
   seconds=length(voice)
   if seconds>17:raise RuntimeError('Audio duration too long: upload aborted')
   frames=tmp/f'frames{index}'
   count=math.ceil((seconds+.25)*12)
   run(sys.executable,ROOT/'scripts'/'render_scene.py','--out',frames,'--frames',count,'--width','540','--height','960','--seed',date.toordinal(),'--shot',index)
   subs=tmp/f'caption{index}.png';caption(text,subs)
   mp4=tmp/f'shot{index}.mp4'
   run('ffmpeg','-y','-hide_banner','-loglevel','error','-framerate','12','-i',frames/'frame_%04d.png','-loop','1','-i',subs,'-i',voice,
     '-filter_complex','[0:v]scale=720:1280:flags=lanczos,fps=24[v];[v][1:v]overlay=0:0:format=auto,format=yuv420p[out]',
     '-map','[out]','-map','2:a','-t',f'{seconds+.2:.3f}','-c:v','libx264','-preset','veryfast','-crf','22','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k',mp4)
   files.append(mp4)
  concat=tmp/'concat.txt';concat.write_text(''.join("file '"+x.name+"'\n" for x in files))
  output=ROOT/'preview.mp4'
  run('ffmpeg','-y','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',concat,'-c','copy',output)
  if not 12<length(output)<70 or output.stat().st_size<150000:raise RuntimeError('Quality check failed; will not upload')
  print('3D preview successfully generated:',output)
  if os.getenv('ENABLE_UPLOAD')=='true' and os.getenv('GITHUB_EVENT_NAME')=='schedule':
   upload_private(output,title)
   history_path=ROOT/'history.json'
   previous=json.loads(history_path.read_text()) if history_path.exists() else []
   previous.append({'date':str(date),'title':title})
   history_path.write_text(json.dumps(previous,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':
 try:main()
 except Exception as e:print('Pipeline FAILED; no automatic upload:',repr(e),file=sys.stderr);raise

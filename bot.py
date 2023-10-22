from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery , ReplyKeyboardMarkup, ForceReply , InputMediaDocument , MessageEntity
from pyrogram import Client , filters 
from config import API_HASH,API_ID,BOT_TOKEN,ID_ACC
import os
from json import loads, dumps
from os.path import exists
from time import sleep, time
from random import randint
from pathlib import Path
from tools import *
import aiohttp
import requests
import bs4
import shutil
from urllib.parse import unquote_plus

#for render
import logging
logging.basicConfig(filename="/var/www/html/log.txt",format='[%(levelname) 5s/%(asctime)s] %(name)s: %(msg)s',level=logging.ERROR)
logging.error("Waiting 30 minutes...")
sleep(1800)
logging.error("Running app now")

#local_variabl
Temp_dates = {}
Config_temp = {}
DB_accs = {'accesos':[]}
admins = ['Yama_Tsukami','tumulatico98', 'Maykol0102']

bot = Client("bot",api_id=API_ID,api_hash=API_HASH,bot_token=BOT_TOKEN)


@bot.on_message(filters.private)
async def start(client: Client, message: Message):
    async def worker(client: Client, message: Message):
        username = message.from_user.username
        user_id = message.from_user.id
        send = message.reply
        out_message = message.text
        
        #! Crear carpeta download si no existe
        if exists('downloads/'+str(username)+'/'):pass
        else:os.makedirs('downloads/'+str(username)+'/')
        try: Temp_dates[username]
        except: Temp_dates[username] = {'downlist' : [],'file':'','ocupado':False, 'mess':''}
        try: Config_temp[username]
        except: Config_temp[username] = {'zips':1999}

        if Temp_dates[username]['ocupado']:
            await send('Ya tiene un proceso activo, espere...')
            return

        #xd = {'accesos':['Yama_Tsukami','tumulatico98']}
        #await bot.send_message(ID_ACC,text=dumps(xd,indent=4))
        msg_conf = await bot.get_messages(ID_ACC,message_ids=6)
        #print(msg_conf)
        DB_accs.update(loads(msg_conf.text))

        if username not in DB_accs['accesos']:
            await send('**⛔️No tienes acceso al BOT⛔️**')
            return
        
        if message.audio or message.document or message.animation or message.sticker or message.photo or message.video:
            Temp_dates[username]['ocupado'] = True
            filesize = int(str(message).split('"file_size":')[1].split(",")[0])
            try:
                filename = str(message).split('"file_name": ')[1].split(",")[0].replace('"',"")	
            except:
                try:
                    mime_type = str(message).split('"mime_type": ')[1].split(",")[0].replace('"',"").split("/")[1]
                    filename = loads(str(message))
                    filename = filename["caption"]
                    filename = f"{filename}.{mime_type}".replace("\n\n","_").replace("\n","_")
                except:
                    filename = str(randint(11111,999999))+".mp4"
            try:filename = filename.replace(' ','_')
            except:pass		
            start = time()	
            msg = await send(f"𝑷𝒓𝒆𝒑𝒂𝒓𝒂𝒏𝒅𝒐 𝑫𝒆𝒔𝒄𝒂𝒓𝒈𝒂\n\n`{filename}`")
            try:
                file = await message.download(file_name=f'downloads/{username}/{filename}',progress=downloadmessage_progres,progress_args=(filename,start,msg))
        
                if Path(f'downloads/{username}/{filename}').stat().st_size == filesize:
                    Temp_dates[username]['ocupado'] = False
                    await msg.delete()
                    Temp_dates[username]['file'] = file
                    #await uploads_options(filename,filesize,username)
                    ls = await files_formatter('downloads/'+str(username)+'/',username)
                    await send(ls[0])
            except Exception as ex:
                Temp_dates[username]['ocupado'] = False
                await send(ex)

        if out_message.startswith('http'):
            
            msg = await send('**Preparando descarga**')
            url = out_message
            if "youtu.be/" in out_message or "youtube.com/" in out_message or "twitch.tv/" in out_message:
                Temp_dates[username]['streaming_list'] = url
                await msg.edit(f"`💻 Elija una de las calidades disponibles`",reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("360p","360")], 
                    [InlineKeyboardButton("480p","480")],
                    [InlineKeyboardButton("720p","720")],
                    [InlineKeyboardButton("1080p","1080")]
                    ]))
            
            elif "mediafire.com" in out_message:
                session = aiohttp.ClientSession()
                page = bs4.BeautifulSoup(requests.get(url).content, 'lxml')
                info = page.find('a', {'aria-label': 'Download file'})
                url = info.get('href') 
                download = await session.get(url,timeout=aiohttp.ClientTimeout(total=1800)) 
                file_size = int(download.headers.get("Content-Length")) 
                file_name = download.headers.get("Content-Disposition").split("filename=")[1]
                try: file_name = file_name.replace('"','')
                except:pass
                downloaded = 0
                file_path = f"downloads/{username}/{file_name}"
                start = time()
                Temp_dates[username]['ocupado'] = True
                await asyncio.sleep(1)
                with open(file_path,"wb") as file:
                    while True:
                        chunk = await download.content.read(1024*1024)
                        downloaded+=len(chunk)
                        if not chunk:
                            break
                        await mediafiredownload(downloaded,file_size,file_name,start,msg)
                        file.write(chunk) 
                    file.close()
                Temp_dates[username]['file'] = f'downloads/{username}/{file_name}'
                await msg.delete()
                Temp_dates[username]['ocupado'] = False
                #await uploads_options(file_name,file_size,username)
            
            else:
                timeout = aiohttp.ClientTimeout(total=60 * 60)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(url,ssl=False,timeout=timeout) as r:
                        try:filename = unquote_plus(url.split("/")[-1])
                        except:filename = r.content_disposition.filename	
                        if "?" in filename:filename = filename.split("?")[0]
                        fsize = int(r.headers.get("Content-Length"))
                        file_path = f"downloads/{username}/{filename}"
                        f = open(file_path,"wb")
                        newchunk = 0
                        start = time()
                        Temp_dates[username]['ocupado'] = True
                        await asyncio.sleep(1)
                        async for chunk in r.content.iter_chunked(1024*1024):
                            newchunk+=len(chunk)
                            await mediafiredownload(newchunk,fsize,filename,start,msg)
                            f.write(chunk)
                        f.close()
                    Temp_dates[username]['file'] = f'downloads/{username}/{filename}'
                    Temp_dates[username]['ocupado'] = False
                    await msg.delete()
                    #await uploads_options(filename,fsize,username)
            ls = await files_formatter('downloads/'+str(username)+'/',username)
            await send(ls[0])
        
        if out_message.startswith('/zip_all'):
            msg = await send('Comprimiendo carpeta base, porfavor espere')
            try:zipear = shutil.make_archive(base_name=f"{username}", format = "zip", root_dir='downloads/'+str(username)+'/')
            except Exception as ex: await send(ex)
            await msg.edit("Operacion terminada con exito, subiendo archivo")
            Temp_dates[username]['file'] = zipear
            fsize = Path(zipear).stat().st_size
            print(fsize)
            try:await uploads_options(username,fsize,username)
            except:pass
            os.unlink(zipear)
            try: shutil.rmtree(f'downloads/{username}')
            except:pass

        if out_message.startswith('/all_up'):
            Temp_dates[username]['ocupado'] = True
            for nombre_archivo in os.listdir('downloads/'+str(username)):
                ruta_archivo = os.path.join('downloads/'+str(username), nombre_archivo)
                filename = Path(ruta_archivo).name
                filesize = Path(ruta_archivo).stat().st_size
                Temp_dates[username]['file'] = ruta_archivo
                try:await uploads_options(filename,filesize,username)
                except:pass
                os.unlink(ruta_archivo)
            Temp_dates[username]['ocupado'] = False
        
        if out_message.startswith('/zips'):
            zips = out_message.split(' ')[1]
            Config_temp[username]['zips'] = int(zips)
            await send('**Operacion realizada**') 
        
        if out_message.startswith('/start'):
            await send('Hola, bienvenido. Envie algun archivo para comenzar :)')

        if out_message.startswith('/cancel'):
            Temp_dates[username]['ocupado'] = False  
            await send('Procesos liberados')
        
        #administrator commands
        if out_message.startswith('/add') and username in admins: #ok
            print(DB_accs)
            lista = out_message.split(' ')
            print(lista)
            DB_accs['accesos'].append(lista[1])
            await bot.edit_message_text(ID_ACC,message_id=6,text=dumps(DB_accs,indent=4))
            await send('**Operacion realizada**')
        
        if out_message.startswith('/ban') and username in admins: #ok
            lista = out_message.split(' ')
            DB_accs['accesos'].remove(lista[1])
            await bot.edit_message_text(ID_ACC,message_id=6,text=dumps(DB_accs,indent=4))
            await send('**Operacion realizada**')
    
    bot.loop.create_task(worker(client, message))

@bot.on_callback_query()
async def callback_handler(client: Client, callback_query: CallbackQuery):
    username = callback_query.from_user.username
    user_id = callback_query.from_user.id
    input_mensaje: str = str(callback_query.data)
    
    if input_mensaje == "144" or input_mensaje == "240" or input_mensaje == "360"  or input_mensaje == "480"  or input_mensaje == "720" or input_mensaje == "1080":
        msg = callback_query.message
        url = Temp_dates[username]['streaming_list']
        await msg.delete()
        msg = await client.send_message(username,"__Descargando__")
        download = await ytdlp_downloader(url,user_id,msg,username,lambda data: download_progres(data,msg,input_mensaje),input_mensaje,f'downloads/{username}/')
        size = os.path.getsize(download)
        await msg.delete()
        Temp_dates[username]['streaming_list'] = ''
        Temp_dates[username]['file'] = download
        #await uploads_options('Youtube Video',size,username)
        ls = await files_formatter('downloads/'+str(username)+'/',username)
        await bot.send_message(username, ls[0])

    if input_mensaje == 'cancel':
        await Temp_dates[username]['mess'].delete()
        Temp_dates[username]['ocupado'] = False
        await bot.send_message(username, 'Proceso cancelado!!')

async def uploads_options(name,size,username):
    path = Temp_dates[username]['file'] 
    msg = await bot.send_message(username, f"𝑺𝒆𝒍𝒆𝒄𝒄𝒊𝒐𝒏𝒂𝒅𝒐 {path}")
    Temp_dates[username]['ocupado'] = True
    Temp_dates[username]['mess'] = msg
    if size-1048 > Config_temp[username]['zips']*1024*1024:
        await msg.edit(f"📦 **Comprimiendo en zips**")
        files = await bot.loop.run_in_executor(None, sevenzip, path, None, Config_temp[username]['zips']*1024*1024) 
    else:
        files = []
        files.append(Temp_dates[username]['file']) 
    
    for element in files:
        filenamex = Path(element).name
        try:
            start = time()
            await asyncio.sleep(1)
            r = await bot.send_document(username,element,file_name=filenamex,progress=downloadmessage_progres,
                        progress_args=(filenamex,start,msg))  
        except Exception as ex:
            Temp_dates[username]['ocupado'] = False
            await bot.send_message(username, ex)
            return
        
    await msg.edit("𝑺𝒖𝒃𝒊𝒅𝒂 𝑪𝒐𝒎𝒑𝒍𝒆𝒕𝒂𝒅𝒂")
    Temp_dates[username]['ocupado'] = False
    #os.unlink('downloads/'+str(username)+'/')
    return

async def files_formatter(path,username):
    rut = str(path)
    filespath = Path(str(path))
    result = []
    dirc = []
    final = []
    for p in filespath.glob("*"):
        if p.is_file():
            result.append(str(Path(p).name))
        elif p.is_dir():
            dirc.append(str(Path(p).name))
    result.sort()
    dirc.sort()
    msg = f'𝑫𝒊𝒓𝒆𝒄𝒕𝒐𝒓𝒊𝒐 𝒂𝒄𝒕𝒖𝒂𝒍\n\n'
    if result == [] and dirc == [] :
        return msg , final
    for k in dirc:
        final.append(k)
    for l in result:
        final.append(l)
    i = 0
    for n in final:
        try:
            size = Path(str(path)+"/"+n).stat().st_size
        except: pass
        msg+=f"**{i}** `{n}` `|` `{sizeof_fmt(size)}` \n"
        i+=1
    msg+= f"\n\n**Comprimir el directorio: /zip_all\nSubir todos los elementos independientes: /all_up**"
    print(msg)
    print(final)
    return msg , final

#Run...
print("started")
bot.start()
bot.loop.run_forever()
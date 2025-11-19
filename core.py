import database
from models.exceptions import MyAppError
from config import sarvam, gemini, model, main_config, search_stock_config

from google.genai import types

import os
import time
import json
import aiohttp
import aiofiles
import tempfile
import soundfile as sf
from datetime import datetime
from starlette.concurrency import run_in_threadpool




class Treeyaa:
    def __init__(self, user_id):
        self.user_id = user_id
        self.prev_conv = []
        
    async def download_file(self, audio_link, ogg_file_path):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(audio_link) as res:
                    data = await res.content.read()
                    async with aiofiles.open(ogg_file_path, mode = "wb") as f:
                        await f.write(data)
            print("✅ Download user audio")
            
        except Exception as e:
            raise MyAppError("DownloadUserAudioError", e)
        
    def convert_ogg_to_wav(self, ogg_file_path):
        try:
            data, sr = sf.read(ogg_file_path) 
            wav_file_path = ogg_file_path[:-4] + ".wav" 
            sf.write(wav_file_path, data, sr) 
            print("✅ Convert ogg to wav")     
            return wav_file_path  
        
        except Exception as e:
            raise MyAppError("convertOggToWavError", e)
    
    def stt(self, file_path):
        t1 = time.time()
        with open(file_path, "rb") as f:
            res = sarvam.speech_to_text.transcribe(
                file = f,
                model = "saarika:v2.5",
                language_code = "unknown"    #"ta-IN"
            )
        t2 = time.time()
        print(f"✅ stt: {(t2-t1)*1000:2f} ms")
        return res.transcript
    
    async def speech_to_text(self, audio_link):
        with tempfile.TemporaryDirectory() as temp_dir:
                # Download audio file to local                 
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3] 
                ogg_file_path = os.path.join(temp_dir, f"{timestamp}.ogg")  
                await self.download_file(audio_link, ogg_file_path)
                
                # Convert 'ogg' audio to 'wav' audio format
                wav_file_path = await run_in_threadpool(self.convert_ogg_to_wav, ogg_file_path)
                
                # Convert speech-to-text
                try:
                    text = await run_in_threadpool(self.stt, wav_file_path)
                    return text
                
                except Exception as e:
                    err_msg = e.body['error']['code']
                    if err_msg == 'invalid_request_error':
                        return {"type" : "failure", "data" : """Audio is more than 30 seconds.
                                Please speak less than 30 seconds."""}
                    else:
                        error = e.body['error']['message']
                        raise MyAppError("SttError", {"type" : "SttError", "data" : error})
        
    def wrap_in_gemini_format(self, role, data):
        return types.Content(role = role, parts = [types.Part.from_text(text = data)])
       
    def add_content(self, role, data):
        # Appends the conversation to previous conversations
        try:
            self.prev_conv += [json.dumps({"role" : role, "data" : data}, indent = 2, ensure_ascii = False)]
        except Exception as e:
            raise MyAppError("AddContentError", e)
          
    async def call_ai(self, gemini_inputs, config):
        try:
            t1 = time.time()
            res = await gemini.aio.models.generate_content(
                    model = model,
                    contents = gemini_inputs,
                    config = config
                )
            t2 = time.time()
            time_taken = (t2-t1)*1000
            return res.text, time_taken
        
        except Exception as e:
            raise MyAppError("GeminiError", e)
        
    async def search_stock(self, user_requested_items):
        # Fetch Stock DB
        stock_json, time_taken = await database.get_items_table()
        print(f"✅ Fetch Stock DB: {time_taken:.2f} ms")
        
        try:
            query = json.dumps({"stock_db" : stock_json, "user_requested_items" : user_requested_items}, indent = 2, ensure_ascii = False)
            gemini_contents = [self.wrap_in_gemini_format(role = 'user', data = query)]
            res, time_taken = await self.call_ai(gemini_contents, search_stock_config)
            print(f"✅ SearchStock: {time_taken:.2f} ms")
            return res
    
        except Exception as e:
            raise MyAppError("SearchStockError", e)
           
    async def ttt(self, gemini_inputs):
        try:
            # Call AI
            res, time_taken = await self.call_ai(gemini_inputs, main_config)
            print(f"✅ ttt: {time_taken:.2f} ms")
            
            # Parse AI Json response
            try:
                res_obj = json.loads(res)
            except json.JSONDecodeError as e:
                print(f"❌ JsonError:\n{res}")
                raise MyAppError(f"JsonError", f"AI Response(MainPrompt): {res}\n\nError Raised: {str(e)}")

            self.add_content("model", res_obj)
            
            # Call AI to find if user requested items are present in store db.
            if res_obj['type'] == "search_stock":
                search_stock_res = await self.search_stock(res)
                
                self.add_content(role = "user", data = json.loads(search_stock_res))
                gemini_inputs += [self.wrap_in_gemini_format(role = 'model', data = res)]
                gemini_inputs += [self.wrap_in_gemini_format(role = 'user', data = search_stock_res)]
                
                # Call ai with the search stock result
                res_obj = await self.ttt(gemini_inputs)
            return res_obj
        
        except Exception as e:
            raise MyAppError("TTTError", e)
                          
    async def process(self, audio_link, text, audio):
        t1 = time.time()
        self.prev_conv, prev_conv_count = await database.get_prev_conv(self.user_id)
        t2 = time.time()
        print(f"✅ Fetch UsersInProcess Table: {(t2-t1)*1000:2f} ms")
        
        # Convert speech-to-text
        if audio:
            text = await run_in_threadpool(self.stt, audio)
        elif audio_link: 
            text = await self.speech_to_text(audio_link)   
                    
        if self.prev_conv:
            # Wrapping current query and previous conversations in gemini input format
            prev_conv_obj = [json.loads(conv) for conv in self.prev_conv]
            gemini_inputs = [self.wrap_in_gemini_format(conv['role'], json.dumps(conv['data'], ensure_ascii = False) if isinstance(conv['data'], dict) else conv['data']) for conv in prev_conv_obj]
            gemini_inputs += [self.wrap_in_gemini_format(role = 'user', data = text)] 
            # Adding current query to previous conversations
            self.add_content("user", text)
        else:
            gemini_inputs = [self.wrap_in_gemini_format(role = 'user', data = text)]
            self.add_content(role = "user", data = text)
            
        res_obj = await self.ttt(gemini_inputs)
        
        print("✅ Chat:")
        i = 0
        for c in self.prev_conv:
            if i%2 == 0:
                print("-"*120)
            c = json.loads(c)
            data = json.dumps(c['data'], indent = 4, ensure_ascii = False) if isinstance(c['data'], dict) else c['data']
            print(f"{c['role']}: {data}\n")
            i += 1
        
        # Update the conversations table
        await database.update_prev_conv(self.user_id, self.prev_conv, prev_conv_count)
        
        return res_obj
    

  
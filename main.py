import config
import db_ops
from search_stock import search_stock
import RequestModel
from error_handler import MyAppError

import os
import time
import json
import copy
import aiohttp
import aiofiles
import tempfile
import soundfile as sf
from datetime import datetime
from dotenv import load_dotenv

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from google import genai
from google.genai import types
from sarvamai import SarvamAI

load_dotenv()
    
def error_response(content):
    return JSONResponse(
        status_code = 400,
        content = content
    )
    
def success_response(content):
   return JSONResponse(
        status_code = 200,
        content = content
    )
    
class TREEYA:
    
    async def download_file(self, audio_link, ogg_file_path):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(audio_link) as response:
                    data = await response.content.read()
                    async with aiofiles.open(ogg_file_path, mode = "wb") as f:
                        await f.write(data)
            print("Downloaded the user audio successfully.")
        except Exception as e:
            raise MyAppError("downloadAudioError", e)
        
    def convert_ogg_to_wav(self, ogg_file_path):
        try:
            data, sr = sf.read(ogg_file_path) 
            wav_file_path = ogg_file_path[:-4] + ".wav" 
            sf.write(wav_file_path, data, sr) 
            print("converted ogg to wav successfully.")     
            return wav_file_path  
        except Exception as e:
            raise MyAppError("convertOggToWavError", e)
    
            
    def add_previous_conversation(self, prev_conv, query):
        try:
            contents = []
            query = types.Content(role = "user", parts = [types.Part.from_text(text = query)])
            
            for conv in prev_conv:
                conv = json.loads(conv)
                role = conv['role'] 
                data = json.dumps(conv['data'])
                content = types.Content(role = role, parts = [types.Part.from_text(text = data)])
                contents.append(content)
                
            contents += [query]
            return contents
        except Exception as e:
            raise MyAppError("AddPreviousConversationError", e)
       
    async def add_content(self, prev_contents, role, data):
        try:
            prev_contents = prev_contents + [json.dumps({"role" : role, "data" : data}, indent = 4, ensure_ascii = False)]
            return prev_contents
        except Exception as e:
            raise MyAppError("AddContentError", e)
       
       
             
    def STT(self, file_path):
        t1 = time.time()
        response = sarvam.speech_to_text.transcribe(
            file = open(file_path, "rb"),
            model = "saarika:v2.5",
            language_code = "unknown"    #"ta-IN"
        )
        t2 = time.time()
        print(f"STT: {(t2-t1)*1000:2f} ms")
        return response.transcript
                 
    async def TTT(self, contents, prev_contents):
        try:
            response = await gemini.aio.models.generate_content(
                model = config.ttt.model,
                contents = contents,
                config = config.ttt.config_1,
            )
            response = response.text
            try:
                res_obj = json.loads(response)
            except Exception as e:
                print("❌ ERROR RESPONSE:\n", response)
                raise MyAppError(f"JsonError:\nAI response:\n{response}", e)
            
            print(response)
            prev_contents = await self.add_content(prev_contents, "model", res_obj)
            
            if res_obj['type'] == "search_stock":
                response = await search_stock(response)
                res_obj = json.loads(response)
                contents = self.add_previous_conversation(prev_conv = prev_contents, query = response)
                prev_contents = await self.add_content(prev_contents, "user", res_obj)
                response, prev_contents = await self.TTT(contents, prev_contents)
            
            return response, prev_contents
        except Exception as e:
            raise MyAppError("TTTError", e)
                   
       
                   
    async def main(self, user_id, audio_link, text, audio):
        t1 = time.time()
        user_in_process_data, conversation_count = await db_ops.get_user_in_process_data(user_id)
        t2 = time.time()
        print(f"Fetch UsersInProcess data: {(t2-t1)*1000:2f} ms")
        
        if audio:
            text = await run_in_threadpool(self.STT, audio)
            
        if audio_link:    
            with tempfile.TemporaryDirectory() as temp_dir:                 
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3] 
                ogg_file_path = os.path.join(temp_dir, f"{timestamp}.ogg")  
                await self.download_file(audio_link, ogg_file_path)
                wav_file_path = await run_in_threadpool(self.convert_ogg_to_wav, ogg_file_path)
                try:
                    text = await run_in_threadpool(self.STT, wav_file_path)
                except Exception as e:
                    if e.body['error']['code'] == 'invalid_request_error':
                        return success_response({"type" : "failure", "data" : "Audio is more than 30 seconds.\n\nPlease speak less than 30 seconds."})
                    else:
                        error = e.body['error']['message']
                        return error_response(error)
                
    
        query = json.dumps(text, ensure_ascii = False)
    
        if user_in_process_data:
            contents = self.add_previous_conversation(prev_conv = user_in_process_data, query = query)
            prev_contents = copy.deepcopy(user_in_process_data)
            prev_contents = await self.add_content(prev_contents, "user", query)
        else:
            contents = [types.Content(role = "user", parts = [types.Part.from_text(text = query)])]
            prev_contents = await self.add_content([], "user", query)
            
        t1 = time.time()
        TTT_response, prev_contents = await self.TTT(contents, prev_contents)
        t2 = time.time()
        print(f"TTT: {(t2-t1)*1000:2f} ms")
        
        
        for c in prev_contents:
            c = json.loads(c)
            print(f"{c['role']}: {json.dumps(c['data'], indent = 4, ensure_ascii = False)}", "\n")
            
        await db_ops.update_user_in_process_data(user_id, prev_contents, conversation_count)
        return TTT_response
    
  

sarvam = SarvamAI(api_subscription_key = os.environ['SARVAM_API_KEY'])  
gemini = genai.Client(api_key = os.environ.get("GOOGLE_API_KEY"),)
treeya = TREEYA() 
app = FastAPI()    
    
    
@app.post("/user_request/") 
async def main(request: RequestModel.user_request):
    return await treeya.main(request.user_id, request.audio_link, request.text, request.audio)

@app.post("/delete_user_in_process/") 
async def main(request: RequestModel.delete_user_in_process):
    await db_ops.delete_user_in_process(request.user_id)
    return success_response({"type" : "success", "data" : f"Deleted UsersInProcess data"})
    
@app.exception_handler(MyAppError)
async def myapp_error_handler(request: Request, exc: MyAppError):
    print(exc)
    return error_response(exc.to_dict())

if __name__ == '__main__':
    uvicorn.run("main:app", host = "localhost", port = 8000, reload = True)

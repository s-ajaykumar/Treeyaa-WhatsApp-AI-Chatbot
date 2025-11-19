import database
from core import Treeyaa
from models.exceptions import MyAppError 
from models.request import UserRequest, DeletePrevConv
from models.response import error_response, success_response

import uvicorn
from fastapi import FastAPI, Request

clients = {}
app = FastAPI()    
    
        
    
@app.post("/user_request/") 
async def main(request: UserRequest):
    conn = Treeyaa(request.user_id)
    response = await conn.process(request.audio_link, request.text, request.audio)
    return success_response(response)
    
    
@app.post("/delete_user_in_process/") 
async def delete(request: DeletePrevConv):
    response = await database.delete_prev_conv(request.user_id)
    return success_response(response)
    
    
@app.exception_handler(MyAppError)
async def myapp_error_handler(request: Request, exc: MyAppError):
    print(exc)
    return error_response(exc.to_dict())


if __name__ == '__main__':
    uvicorn.run("main:app", host = "0.0.0.0", port = 8000, reload = True)

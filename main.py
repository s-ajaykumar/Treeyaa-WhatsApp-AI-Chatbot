import database
from core import Treeyaa
from models.exceptions import MyAppError 
from models.request import UserRequest, DeletePrevConv
from models.response import error_response, success_response
from auth.dependencies import validate_user

import uvicorn
from fastapi import FastAPI, Request, Depends

clients = {}
app = FastAPI()    
    
        
    
@app.post("/user_request/") 
async def main(request: UserRequest, valid_user = Depends(validate_user)):
    conn = Treeyaa(request.user_id)
    response = await conn.main(request.audio_link, request.text, request.audio, request.is_catalogue_mode)
    return success_response(response)
    
    
@app.post("/delete_user_in_process/") 
async def delete(request: DeletePrevConv, valid_user = Depends(validate_user)):
    response = await database.delete_prev_conv(request.user_id)
    return success_response(response)
    
    
@app.exception_handler(MyAppError)
async def myapp_error_handler(request: Request, exc: MyAppError):
    print(exc)
    return error_response(exc.to_dict())


if __name__ == '__main__':
    uvicorn.run("main:app", host = "0.0.0.0", port = 8000, reload = True)

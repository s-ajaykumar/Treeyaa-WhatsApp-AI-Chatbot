from fastapi.responses import JSONResponse


def error_response(content):
    return JSONResponse(
        status_code = 500,
        content = content
    )
    
def success_response(content):
   return JSONResponse(
        status_code = 200,
        content = content
    )
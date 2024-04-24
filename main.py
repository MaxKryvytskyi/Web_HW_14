import uvicorn
from fastapi import FastAPI, APIRouter, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.routes import contacts
from src.routes import auth 
from src.routes import users
from fastapi.templating import Jinja2Templates
from src.services.limiter import limiter
from src.services.auth import auth_service
from src.database.models import User


server = FastAPI()
templates = Jinja2Templates(directory='templates/quotes')

origins = ["https://localhost:8000"]



server.include_router(auth.router, prefix='/api')
server.include_router(contacts.router, prefix='/api')
server.include_router(users.router, prefix='/api')

server.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @server.get("/api/healthchaker")
# def healthchaker(db: Session = Depends(get_db)):
#     """
#     The healthchaker function is a simple function that returns a JSON object with the message &quot;Hello World&quot;.
#     This function is used to test if the API server is running.
    
    
#     :param db: Session: Access the database
#     :return: A dictionary with a message
#     :doc-author: Trelent
#     """
#     return {"message": "Hello World"}

@server.get("/")
@limiter.limit("100/minute")
async def home(request: Request, db: Session = Depends(get_db)): #, current_user: User = Depends(auth_service.get_current_user)
    """
    The home function is the default route for our application.
    It returns a TemplateResponse object, which renders the home.html template
    and passes it a context containing the title of our app and request object.
    
    :param request: Request: Pass the request object to the template
    :return: A templateresponse object
    :doc-author: Trelent
    """
    user = {"is_authenticated": False}
    return templates.TemplateResponse("base.html", {"request": request, "user": user})



if __name__ == "__main__":
    uvicorn.run(server, host="0.0.0.0", port=8000)
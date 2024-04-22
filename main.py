import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routes import contacts
from src.routes import auth 
from src.routes import users


server = FastAPI()

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


if __name__ == "__main__":
    uvicorn.run(server, host="0.0.0.0", port=8000)
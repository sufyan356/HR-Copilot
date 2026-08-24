from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from BACKEND.Database.database import Base, engine
from BACKEND.Routes.signup import signupRouter
from BACKEND.Routes.login import loginRouter
from BACKEND.Routes.chat import chatRouter
from BACKEND.Routes.chat_history import chatHistoryRouter
from BACKEND.Models.model import User,ChatHistory

Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(signupRouter)
app.include_router(loginRouter)
app.include_router(chatRouter)
app.include_router(chatHistoryRouter)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Allow all domains (change in production)
    allow_credentials=True,
    allow_methods=["*"],          # Allow all methods: GET, POST, PUT, DELETE
    allow_headers=["*"],          # Allow all headers
)

@app.get("/")
def root():
    return{"status":"Server is Running.."}


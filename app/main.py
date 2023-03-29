from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.routers import auth, book, review
from app.db import engine, Base
import app.models as models
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(auth.router)
app.include_router(book.router)
app.include_router(review.router)
models.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return RedirectResponse("/docs")

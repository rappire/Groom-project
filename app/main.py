from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.routers import auth, book, review
from app.db import engine, Base
import app.models as models

app = FastAPI()
app.include_router(auth.router)
app.include_router(book.router)
app.include_router(review.router)
models.Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    return RedirectResponse("/docs")

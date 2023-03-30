from fastapi import APIRouter, Request, Depends, HTTPException
from app.db import SessionLocal
from app.models import Books, Reviews, Votes
from app.scraper import BookScraper
from sqlalchemy.orm import Session
from app.routers.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/book", tags=["book"])
scraper = BookScraper()


class Review(BaseModel):
    id: str
    rate: str
    like: str
    dislike: str
    isbn: str
    contents: str
    userCheck: int


class RecentReviewBook(BaseModel):
    isbn: str
    thumbnail: str
    rate: float
    title: str


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/search/{book_name}")
async def search(book_name: str, num: int = 20, db: Session = Depends(get_db)):
    result = await scraper.scraper(book_name)
    for i, book in enumerate(result):
        dbBook = db.query(Books).filter(Books.isbn == book.isbn).first()
        if dbBook:
            result[i].rate = dbBook.rate
    return {"data": result}


@router.get("/recent")
async def showRecentReview(db: Session = Depends(get_db)):
    result = db.query(Books).order_by(Books.updatetime.desc()).limit(5).all()
    booklist = []
    for i in result:
        book = RecentReviewBook(
            isbn=result.isbn,
            thumbnail=result.thumbnail,
            rate=result.rate,
            title=result.title,
        )
        booklist.append(book)

    return booklist


@router.get("/{isbn}")
async def bookInfo(
    isbn: str, id: str = Depends(get_current_user), db: Session = Depends(get_db)
):
    book = db.query(Books).filter(Books.isbn == isbn).first()
    if not book:
        result = await scraper.scraper(isbn)
        result = result[0]
        return result

    reviews = db.query(Reviews).filter(Reviews.isbn == isbn).all()
    reviewlist = []
    # voteList = db.query(Votes).filter(Votes.id == id).all()
    for re in reviews:
        vote = None
        if id:
            vote = db.query(Votes).filter((Votes.id == id), (Votes.rK == re.pk)).first()
        if vote:
            review = Review(
                id=re.id,
                rate=re.rate,
                like=re.like,
                dislike=re.dislike,
                isbn=re.isbn,
                contents=re.contents,
                userCheck=vote.like,
            )

        else:
            review = Review(
                id=re.id,
                rate=re.rate,
                like=re.like,
                dislike=re.dislike,
                isbn=re.isbn,
                contents=re.contents,
                userCheck=1,
            )
        reviewlist.append(review)

    book.review = reviewlist
    return book

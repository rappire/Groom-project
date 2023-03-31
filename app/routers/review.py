from fastapi import APIRouter, Request, Depends, HTTPException
from app.db import SessionLocal
from app.models import Books, Reviews, Votes
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.routers.auth import get_current_user, get_user_exception
from app.scraper import BookScraper
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/review", tags=["review"])
scraper = BookScraper()


class Review(BaseModel):
    id: str
    rate: float
    like: int
    dislike: int
    isbn: str
    contents: str
    userCheck: int


class GetReview(BaseModel):
    contents: str
    rate: float


class UserReview(BaseModel):
    title: str
    rate: float
    contents: str
    like: int
    dislike: int
    thumbnail: str
    isbn: str


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def plusRate(isbn, rate, db):
    book = db.query(Books).filter(Books.isbn == isbn).first()
    if book.reviewCount != 0:
        book.rate = (book.rate * book.reviewCount + rate) / (book.reviewCount + 1)
        book.reviewCount += 1
    else:
        book.reviewCount = 1
        book.rate = rate
    book.updatetime = datetime.now()
    db.add(book)
    db.commit()


def editRate(isbn, rateOld, rate, db):
    book = db.query(Books).filter(Books.isbn == isbn).first()
    book.updatetime = datetime.now()
    book.rate = (book.rate * book.reviewCount + rate - rateOld) / book.reviewCount
    db.add(book)
    db.commit()


def deleteRate(isbn, rate, db):
    book = db.query(Books).filter(Books.isbn == isbn).first()
    if book.reviewCount != 1:
        book.rate = (book.rate * book.reviewCount - rate) / (book.reviewCount - 1)
        book.reviewCount -= 1
        db.add(book)
    else:
        db.delete(book)
    db.commit()


async def plusBook(isbn, db):
    book = db.query(Books).filter(Books.isbn == isbn).first()
    if not book:
        result = await scraper.scraper(isbn)
        result = result[0]
        book = Books()
        book.isbn = result.isbn
        book.title = result.title
        book.authors = result.authors
        book.contents = result.contents
        book.thumbnail = result.thumbnail
        book.url = result.url
        book.rate = 0
        book.reviewCount = 0
        db.add(book)
        db.commit()


@router.post("/{isbn}/create")
async def createReview(
    isbn: str,
    review: GetReview,
    id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rate = review.rate
    contents = review.contents
    if id is None:
        raise get_user_exception()
    if rate < 0 or rate > 5:
        raise HTTPException(status_code=400, detail="rate is not appropriate")

    reviewModel = (
        db.query(Reviews).filter(Reviews.id == id, Reviews.isbn == isbn).first()
    )
    if reviewModel is None:
        reviewModel = Reviews()
        await plusBook(isbn, db)
        plusRate(isbn, rate, db)
    else:
        editRate(isbn, reviewModel.rate, rate, db)
    reviewModel.id = id
    reviewModel.contents = contents
    reviewModel.rate = rate
    reviewModel.isbn = isbn
    reviewModel.dislike = 0
    reviewModel.like = 0
    db.add(reviewModel)
    db.commit()


@router.delete("/{isbn}/delete")
async def deleteReview(
    isbn: str, id: str = Depends(get_current_user), db: Session = Depends(get_db)
):
    if id is None:
        raise get_user_exception()
    review = db.query(Reviews).filter(Reviews.id == id, Reviews.isbn == isbn).first()
    db.query(Votes).filter(Votes.id == id, Votes.rK == review.pk).delete()
    deleteRate(isbn, review.rate, db)
    db.query(Reviews).filter(Reviews.id == id, Reviews.isbn == isbn).delete()
    db.commit()


@router.get("/{isbn}/like")
async def likeReview(
    isbn: str,
    id: str,
    userid: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if id is None:
        raise get_user_exception()
    # 유저가 본인 자신에게는 투표 불가능
    # if id == userid:
    #     raise HTTPException(status_code=404, detail="Cannot vote user's review")
    review = db.query(Reviews).filter(Reviews.id == id, Reviews.isbn == isbn).first()
    vote = db.query(Votes).filter(Votes.rK == review.pk, Votes.id == userid).first()
    if not vote:
        vote = Votes()
        review.like += 1
    elif vote.like == 3:
        review.dislike -= 1
        review.like += 1

    vote.id = userid
    vote.rK = review.pk
    vote.like = 2
    db.add(vote)
    db.commit()


@router.get("/{isbn}/dislike")
async def dislikeReview(
    isbn: str,
    id: str,
    userid: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if id is None:
        raise get_user_exception()
    # 유저가 본인 자신에게는 투표 불가능
    # if id == userid:
    #     raise HTTPException(status_code=404, detail="Cannot vote user's review")

    review = db.query(Reviews).filter(Reviews.id == id, Reviews.isbn == isbn).first()
    vote = db.query(Votes).filter(Votes.rK == review.pk, Votes.id == userid).first()
    if not vote:
        vote = Votes()
        review.dislike += 1
    elif vote.like == 2:
        review.like -= 1
        review.dislike += 1

    vote.id = userid
    vote.rK = review.pk
    vote.like = 3
    db.add(vote)
    db.commit()


@router.delete("/{isbn}/like")
async def deleteReview(
    isbn: str,
    id: str,
    userid: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if id is None:
        raise get_user_exception()
    # 유저가 본인 자신에게는 투표 불가능
    # if id == userid:
    #     raise HTTPException(status_code=404, detail="Cannot vote user's review")

    review = db.query(Reviews).filter(Reviews.id == id, Reviews.isbn == isbn).first()
    vote = db.query(Votes).filter(Votes.rK == review.pk, Votes.id == userid).first()
    if not vote:
        return
    if vote.like == 2:
        review.like -= 1
    else:
        review.dislike -= 1
    db.add(review)
    db.delete(vote)
    db.commit()


@router.get("/user")
async def showUserReview(
    id: str = Depends(get_current_user), db: Session = Depends(get_db)
):
    reviews = db.query(Reviews).filter(Reviews.id == id).all()
    reviewList = []
    for review in reviews:
        book = db.query(Books).filter(Books.isbn == review.isbn).first()
        result = UserReview(
            contents=review.contents,
            like=review.like,
            dislike=review.dislike,
            rate=review.rate,
            thumbnail=book.thumbnail,
            title=book.title,
            isbn=review.isbn,
        )
        reviewList.append(result)
    return reviewList

from operator import countOf
from typing import List, Optional

import enum

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic.main import BaseModel
from sqlalchemy.sql.schema import Table
from sqlmodel import SQLModel, func
import sqlmodel
from sqlmodel import Field, Relationship,Session, SQLModel, create_engine, default, select, Column, Enum
from sqlalchemy import func

class AuthorBase(sqlmodel.SQLModel):
     name: str
     country: str


class Author(AuthorBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    books: List["Book"] = Relationship(back_populates="author")


class AuthorCreate(AuthorBase):
    pass

class AuthorRead(AuthorBase):
     id: int


class AuthorUpdate(AuthorBase):
    id: Optional[int] = None
    name: Optional[str] = None
    country: Optional[str] =None



#



class ReaderBase(SQLModel):
    #readerbook_id: Optional[int] = Field(default=None, foreign_key="readerbook.id")
    name: str
    email: str
    

class Reader(ReaderBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    #reader: List["Reader"] = Relationship(back_populates="readerbooks") 

    #books: List["Book"] = Relationship(back_populates="author")

class ReaderCreate(ReaderBase):
    pass


class ReaderRead(ReaderBase):
    id: int



class ReaderUpdate(ReaderBase):
    id: Optional[int] = None
    name: Optional[str] = None
    email: Optional[str] = None




#




class BookBase(SQLModel):
    title: str
    genre: str
    copies: Optional[int] = None

    author_id: Optional[int] = Field(default=None, foreign_key="author.id")


class Book(BookBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    author: Optional[Author] = Relationship(back_populates="books")


# class BookCreate(BookBase):
#     pass

class BookCreateMany(BaseModel):
    data: List[BookBase]


class BookRead(BookBase):
    id: int

class BookReadMany(BaseModel):
    count : int = 0
    data: List[BookRead] = []


class BookUpdate(SQLModel):
    title: Optional[str] = None
    genre: Optional[str] = None
    copies: Optional[int] = None
    author_id: Optional[int] = None



#



class ReaderStatus(enum.Enum):
    FINISHED_READING = 1
    READING = 2
    WILL_READ = 3





class ReaderBookBase(SQLModel):

    book_id: Optional[int] = Field(default=None, foreign_key="book.id")
    reader_id: Optional[int] = Field(default=None, foreign_key="reader.id")

    reader_status: str

    


    #reader_status: Column(Enum(ReaderStatus))
    #reader_status = Field(sa_column=Column(Enum(ReaderStatus)))
    reader_status: ReaderStatus = Field(
        sa_column=Column(
            Enum(ReaderStatus),
            default=None,
            nullable=True,
            index=True
        )   
    )

    
class ReaderBook(ReaderBookBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    #readerbooks: Optional["ReaderBook"] = Relationship(back_populates="readers")

    #author: Optional[Author] = Relationship(back_populates="books")

class ReaderBookCreate(ReaderBookBase):
    pass


class ReaderBookRead(ReaderBookBase):
    id: int



class ReaderBookUpdate(ReaderBookBase):
    id: Optional[int] = None
    reader_status: Optional[int] = None
    


#

class ReaderBookWithReader(ReaderBook):
    reader: Optional[ReaderRead] = None


class ReaderReadWithReaderBook(ReaderRead):
    readerbooks: List[ReaderBookRead] = []



class BookReadWithAuthor(BookRead):
    author: Optional[AuthorRead] = None


class AuthorReadWithBooks(AuthorRead):
    books: List[BookRead] = []




    

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
    

app = FastAPI()    


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# @app.post("/book/", response_model=BookRead)
# def create_book(*, session: Session = Depends(get_session), book: BookCreate):
#         db_book = Book.from_orm(book)
#         session.add(db_book)
#         session.commit()
#         session.refresh(db_book)
#         return db_book

@app.post("/books/", response_model=dict)
def create_book(*, session: Session = Depends(get_session), booksRequest: BookCreateMany):

        countOfBooks = len(booksRequest.data)

        for b in booksRequest.data:
            db_book = Book.from_orm(b)
            session.add(db_book)

        session.commit()

        responseBooks = {
            "count" : countOfBooks
        }
        return responseBooks


@app.get("/books/", response_model=List[BookRead])
def read_books(
    *, 
    session: Session = Depends(get_session),
    offset: int = 0, limit: int = Query(default=100, lte=100),
):
        books = session.exec(select(Book).offset(offset).limit(limit)).all()
        return books


@app.get("/books/{book_id}", response_model=BookReadWithAuthor)
def read_book(*, session: Session = Depends(get_session), book_id: int):
        book = session.get(Book, book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        return book


@app.patch("/books/{book_id}", response_model=BookRead)
def update_book(*, session: Session = Depends(get_session),book_id: int, book: BookUpdate):
        db_book = session.get(Book, book_id)
        if not db_book:
            raise HTTPException(status_code=404, detail="Book not found")
        book_data = book.dict(exclude_unset=True)
        for key, value in book_data.items():
            setattr(db_book, key, value)
        session.add(db_book)
        session.commit()
        session.refresh(db_book)
        return db_book


@app.delete("/books/{book_id}")
def delete_book(*, session: Session = Depends(get_session),book_id: int):
        book = session.get(Book, book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        session.delete(book)
        session.commit()
        return {"ok": True}



#




@app.post("/authors/", response_model=AuthorRead)
def create_author(*, session: Session = Depends(get_session), author: AuthorCreate):
    db_author = Author.from_orm(author)
    session.add(db_author)
    session.commit()
    session.refresh(db_author)
    return db_author


@app.get("/authors/", response_model=List[AuthorRead])
def read_authors(
    *, 
    session: Session = Depends(get_session), 
    offset:int = 0, limit: int = Query(default=100, lte=100),
):
    authors = session.exec(select(Author).offset(offset).limit(limit)).all()
    return authors


@app.get("/authors/{author_id}", response_model=AuthorReadWithBooks)
def read_author(*, author_id: int, session: Session = Depends(get_session)):
    author = session.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@app.patch("/authors/{author_id}", response_model=AuthorRead)
def update_author(
    *, 
    session: Session = Depends(get_session),
    author_id: int,
    author: AuthorUpdate, 
):
    db_author = session.get(Author, author_id)
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")
    author_data = author.dict(exclude_unset=True)
    for key, value in author_data.items():
        setattr(db_author, key, value)
    session.add(db_author)
    session.commit()
    session.refresh(db_author)
    return db_author


@app.delete("/authors/{author_id}")
def delete_author(*, session: Session = Depends(get_session), author_id: int):
    author = session.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    session.delete(author)
    session.commit()
    return{"ok": True}




#





@app.post("/reader/", response_model=ReaderRead)
def create_reader(*, session: Session = Depends(get_session), reader: ReaderCreate):
    db_reader = Reader.from_orm(reader)
    session.add(db_reader)
    session.commit()
    session.refresh(db_reader)
    return db_reader


@app.get("/readers/", response_model=List[ReaderRead])
def read_readers(
    *, 
    session: Session = Depends(get_session), 
    offset:int = 0, limit: int = Query(default=100, lte=100),
):
    readers = session.exec(select(Reader).offset(offset).limit(limit)).all()
    return readers


@app.get("/readers/{reader_id}", response_model=ReaderReadWithReaderBook)
def read_reader(*, reader_id: int, session: Session = Depends(get_session)):
    reader = session.get(Reader, reader_id)
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")
    return reader




@app.get("/readers/{reader_id}/summary", response_model=ReaderBookWithReader)
def reader_summary(*, reader_id: int, session: Session = Depends(get_session)):
    statement = select(ReaderBook.reader_status, func.count(ReaderBook.book_id).label("count").group_by(Reader.reader_id, ReaderBook.reader_status).where(reader_id=reader_id))
    results = session.exec(statement)
    readers = results.all()
    print(readers)





@app.patch("/readers/{reader_id}", response_model=ReaderRead)
def update_reader(
    *, 
    session: Session = Depends(get_session),
    reader_id: int,
    reader: ReaderUpdate, 
):
    db_reader = session.get(Reader, reader_id)
    if not db_reader:
        raise HTTPException(status_code=404, detail="Reader not found")
    reader_data = reader.dict(exclude_unset=True)
    for key, value in reader_data.items():
        setattr(db_reader, key, value)
    session.add(db_reader)
    session.commit()
    session.refresh(db_reader)
    return db_reader


@app.delete("/readers/{reader_id}")
def delete_reader(*, session: Session = Depends(get_session), reader_id: int):
    reader = session.get(Reader, reader_id)
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")
    session.delete(reader)
    session.commit()
    return{"ok": True}



    #




@app.post("/readerbook/", response_model= ReaderBookRead)
def create_readerbook(*, session: Session = Depends(get_session), readerbook: ReaderBookCreate):
    db_readerbook = ReaderBook.from_orm(readerbook)
    session.add(db_readerbook)
    session.commit()
    session.refresh(db_readerbook)
    return db_readerbook


@app.get("/readerbooks/", response_model=List[ReaderBookRead])
def read_readerbooks(
    *, 
    session: Session = Depends(get_session), 
    offset:int = 0, limit: int = Query(default=100, lte=100),
):
    readerbooks = session.exec(select(ReaderBook).offset(offset).limit(limit)).all()
    return readerbooks



@app.get("/readerbooks/{readerbook_id}", response_model=ReaderBookWithReader)
def read_readerbook(*, readerbook_id: int, session: Session = Depends(get_session)):
    readerbook = session.get(ReaderBook, readerbook_id)
    if not readerbook:
        raise HTTPException(status_code=404, detail="ReaderBook not found")
    return readerbook



@app.patch("/readerbooks/{readerbook_id}", response_model=ReaderBookRead)
def update_readerbook(
    *, 
    session: Session = Depends(get_session),
    readerbook_id: int,
    readerbook: ReaderBookUpdate, 
):
    db_readerbook = session.get(ReaderBook, readerbook_id)
    if not db_readerbook:
        raise HTTPException(status_code=404, detail="ReaderBook not found")
    readerbook_data = readerbook.dict(exclude_unset=True)
    for key, value in readerbook_data.items():
        setattr(db_readerbook, key, value)
    session.add(db_readerbook)
    session.commit()
    session.refresh(db_readerbook)
    return db_readerbook



@app.delete("/readerbooks/{readerbook_id}")
def delete_readerbook(*, session: Session = Depends(get_session), readerbook_id: int):
    readerbook = session.get(ReaderBook, readerbook_id)
    if not readerbook:
        raise HTTPException(status_code=404, detail="ReaderBook not found")
    session.delete(readerbook)
    session.commit()
    return{"ok": True}
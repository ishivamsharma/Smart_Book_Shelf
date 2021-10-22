from typing import List, Optional

from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


class BookAuthorLink(SQLModel, table=True):
    author_id: Optional[int] = Field(
        default=None, foreign_key="author.id", primary_key=True
    )
    book_id: Optional[int] = Field(
        default=None, foreign_key="book.id", primary_key=True
    )
    is_writing: bool = False

    author: "Author" = Relationship(back_populates="book_links")
    book: "Book" = Relationship(back_populates="author_links")

class Author(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    country: str

    book_links: List[BookAuthorLink] = Relationship(back_populates="book")


class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    genre: str
    copies: Optional[int] = None

    author_links: List[BookAuthorLink] = Relationship(back_populates="book")


sqlite_file_name = "example.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def create_books():
    with Session(engine) as session:
        author_thriller = Author(name="J.D. Salinger", country="USA")
        author_romance = Author(name="Jane Austen", country="UK")
        author_drama = Author(name="Scott Hanselman", country="UK")
        author_action = Author(name="Pranav Rastogi", country="India")

        book_aliens = Book(
            title="Aliens", 
            genre="Thriller"
        )

        book_nine_stories = Book(
            title="Nine Stories",
            genre="Romance",
            copies=3521
        )  

        book_deliverance = Book(
            title="Deliverance",
            genre="Drama"
        )
        aliens_author_jd_link = BookAuthorLink(author=author_thriller, book=book_aliens)
        aliens_pranav_link = BookAuthorLink(
            author=author_action, book=book_aliens, is_writing=True
        )
        deliverance_scott_link = BookAuthorLink(
            author=author_romance, book=book_deliverance, is_writing=True
        )
        nine_stories_jane_link = BookAuthorLink(
            author=author_drama, book=book_nine_stories, is_writing=True
        )
        session.add(aliens_author_jd_link)
        session.add(aliens_pranav_link)
        session.add(deliverance_scott_link)
        session.add(nine_stories_jane_link)
        session.commit()

        for link in author_action.book_links:
            print("Action Book:", link.book, "is writing:", link.is_writing)

        for link in author_action.book_links:
            print("Action Book:", link.book, "is writing:", link.is_writing)


def update_books():
    with Session(engine) as session:
        book_deliverance = session.exec(
            select(Book).where(Book.title == "Deliverance")
        ).one()
        author_romance = session.exec(select(Author).where(Author.name == "Jane Austen")).one()

        author_romance.books.append(book_deliverance)
        session.add(author_romance)
        session.commit()

        print("Updated Deliverance:", book_deliverance.authors)
        print("Jane Austen books:", author_romance.books)



def main():
    create_db_and_tables()
    create_books()
    update_books()
    

if __name__ == '__main__':
    main()
    
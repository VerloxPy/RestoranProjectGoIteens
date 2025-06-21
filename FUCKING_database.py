from sqlalchemy import create_engine, String, Float, Integer, ForeignKey, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import List

from flask_login import UserMixin

import bcrypt

PGUSER = "postgres"
PGPASSWORD = "1"

engine = create_engine(f"postgresql+psycopg2://{PGUSER}:{PGPASSWORD}@localhost:5432/restaurant", echo=True)
Session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    def create_db(self):
        Base.metadata.create_all(engine)

    def drop_db(self):
        Base.metadata.drop_all(engine)



class Users(Base, UserMixin):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nickname : Mapped[str] = mapped_column(String(100), unique=True)
    password : Mapped[str] = mapped_column(String(200))
    email : Mapped[str] = mapped_column(String(50), unique=True)

    orders : Mapped[list["Orders"]] = relationship(back_populates='user')


    def set_password(self, password: str):
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))



class Menu(Base):

    __tablename__ = "menu"

    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    positions : Mapped[str] = mapped_column(String(100), unique=True)
    price : Mapped[int] = mapped_column(nullable=True)

    orders: Mapped[List["Orders"]] = relationship(back_populates="menu_item")

class Orders(Base):

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    position_id: Mapped[int] = mapped_column(ForeignKey("menu.id"))
    quantity: Mapped[int] = mapped_column()

    user: Mapped["Users"] = relationship(back_populates="orders")
    menu_item: Mapped["Menu"] = relationship(back_populates="orders")


# base = Base()
# base.create_db()
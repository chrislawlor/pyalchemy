from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, validator

from pyalchemy import create_table, PyAlchemy

import sqlalchemy as sa

meta = sa.MetaData()


class Roles(Enum):
    RECRUITER = "recruiter"
    CANDIDATE = "candidate"


users_explicit = sa.Table(
    "user_explicit",
    meta,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("username", sa.String, nullable=False),
    sa.Column("password", sa.String, nullable=False),
    sa.Column("email", sa.String, nullable=False),
    sa.Column("created", sa.DateTime, default=datetime.utcnow),
    sa.Column("active", sa.Boolean),
    sa.Column("role", sa.Enum(Roles)),
    sa.Column("score", sa.Float),
)


# Our test model


class User(BaseModel):
    id: Optional[int]
    username: str
    password: str
    email: str
    created: Optional[datetime]
    active: bool = True
    role: Roles = Roles.RECRUITER
    score: float = 1.123

    @validator("created", always=True)
    def default_created_to_now(cls, value):
        print(f"value={value}")
        if value is None:
            return datetime.utcnow()
        return value


users = create_table(meta, User)


class UserMagic(User):
    __metaclass__ = PyAlchemy
    # objects = users


# cross your fingers

if __name__ == "__main__":
    eng = sa.create_engine("sqlite:///:memory:")

    user = User(username="testuser", password="123456", email="test@example.com")

    with eng.connect() as conn:
        meta.create_all(eng)
        user_data = user.dict()
        print(f"User data: {user_data}")

        # Try our dynamically created table
        print()
        ins = users.insert().values(**user_data)
        print(ins)
        result = conn.execute(ins)
        user_id = result.lastrowid
        select = users.select().where(users.c.id == user_id)
        retrieved = conn.execute(select).fetchone()
        print(f"Created User: {retrieved}")

        # And the normal table
        print()
        ins = users_explicit.insert().values(**user_data)
        print(ins)
        result = conn.execute(ins)
        user_id = result.lastrowid
        select = users.select().where(users.c.id == user_id)
        retrieved = conn.execute(select).fetchone()
        print(f"Created User: {retrieved}")

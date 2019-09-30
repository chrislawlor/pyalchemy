# PyAlchemy

Pydantic + SQLAlchemy

Dynamically create SQLAlchemy tables from Pydantic models.


## Example

```python
from typing import Optional
import sqlalchemy as sa
from pydantic import BaseModel
from pyalchemy import create_table

meta = sa.MetaData()

class User(BaseModel):
    id: Optional[int]
    username: str
    email: str

users = create_table(meta, User)

eng = sa.create_engine("sqlite:///:memory:")

user = User(username="testuser", email="test@example.com")

with eng.connect() as conn:
    meta.create_all(eng)

    # Write our user to the database
    ins = users.insert().values(**user.dict())
    result = conn.execute(ins)
    user_id = result.lastrowid

    # Retrieve the user
    select = users.select().where(users.c.id == user_id)
    retrieved = conn.execute(select).fetchone()
    retrieved_user = User(*retrieved)
```

## TODO:

1. Convert data retrieved from the SQLAlchemy table back into a Pydantic model.
2. Automate the ``create_table`` call and give it a better API. Perhaps use
   a metaclass on the Pydantic model.
3. A way to optionally specify specific SQL field types for a given attribute.


License: MIT

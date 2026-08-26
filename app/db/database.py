from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession  
from sqlalchemy.orm import DeclarativeBase # Declarative base
from app.core.config import DATABASE_URL  # as  we load (define) the db url there from .env
# We use create_async_engine because we want our app to be non-blocking
engine = create_async_engine(   # connection manager to your database.  (it manages  the pool of connections)
    DATABASE_URL,
    echo=True   #echo=True means SQLAlchemy prints the SQL queries it executes
)
#Session is a higher-level SQLAlchemy object that manages your database work 
SessionLocal=async_sessionmaker(  # it  did not create seeeion it create obj of  async_sessionmaker class  which is  a  function whenever called return session
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
class Base(DeclarativeBase):   # it allow  SQLAlchemy understands to understood  that it is  defining  tabel  not just a  regular class  and  when we do create all it got created
    pass
async def get_db():
    async with SessionLocal() as session:
        yield session  #  why there is  yield insted of return :  bcz  the  session i been created with the  contextmannager  with 
        # it will automaticalley  got   closed   whenever  it got out from with  block   and  when we do return it get out of with block  but  uing  yeild   execution stops  at  yield  


        #yield pauses execution at that point, so the session remains inside the async with block while the endpoint uses it. Then, when FastAPI finishes with the dependency, execution continues after yield; since there's nothing there, the async with exits and cleans up the session.
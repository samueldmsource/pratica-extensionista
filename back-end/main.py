from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime

# Configuração do Banco de Dados SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Definição do Modelo do Banco de Dados
class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    date = Column(DateTime, default=datetime.now)

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    responsavel = Column(String)
    local = Column(String)
    recorrencia = Column(JSON)

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Modelo Pydantic para validação de dados de entrada/saída
class EventBase(BaseModel):
    title: str
    description: str | None = None
    date: datetime | None = None

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: int

    class Config:
        orm_mode = True

class ActivityBase(BaseModel):
    nome: str
    responsavel: str
    local: str
    recorrencia: dict

class ActivityCreate(ActivityBase):
    pass

class ActivityResponse(ActivityBase):
    id: int
    class Config:
        orm_mode = True

# Inicialização do FastAPI
app = FastAPI()

# Configuração do CORS para permitir requisições do Next.js
origins = [
    "http://localhost",
    "http://localhost:3000",  # Porta padrão do Next.js
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    # Adicione outras origens do seu frontend em produção, se houver
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Função para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rotas da API
@app.post("/events/", response_model=EventResponse)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    db_event = Event(title=event.title, description=event.description, date=event.date)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.get("/events/", response_model=list[EventResponse])
def read_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    events = db.query(Event).offset(skip).limit(limit).all()
    return events

@app.post("/activities/", response_model=ActivityResponse)
def create_activity(activity: ActivityCreate, db: Session = Depends(get_db)):
    try:
        # Compatibilidade com Pydantic v1 e v2
        activity_data = activity.model_dump() if hasattr(activity, "model_dump") else activity.dict()
        db_activity = Activity(**activity_data)
        db.add(db_activity)
        db.commit()
        db.refresh(db_activity)
        return db_activity
    except Exception as e:
        db.rollback()
        print(f"ERRO NO SERVIDOR: {e}") # Verifique o terminal do Python para ver o erro real
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/activities/", response_model=list[ActivityResponse])
def read_activities(db: Session = Depends(get_db)):
    return db.query(Activity).all()
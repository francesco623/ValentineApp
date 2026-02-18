from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import DeclarativeBase, Session
import random

# --- Database setup ---
engine = create_engine("sqlite:///instance/test.db")

class Base(DeclarativeBase):
    pass

class Reason(Base):
    __tablename__ = "reasons"
    id = Column(Integer, primary_key=True)
    content = Column(String(200), nullable=False)
    hidden = Column(Boolean, default=False)

Base.metadata.create_all(engine)

# --- App setup ---
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# --- Routes ---

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    with Session(engine) as session:
        reasons = session.query(Reason).filter_by(hidden=False).all()
        if not reasons:
            return RedirectResponse("/admin", status_code=302)
        reason = random.choice(reasons)
    return templates.TemplateResponse("index.html", {"request": request, "reason": reason})


@app.get("/admin", response_class=HTMLResponse)
def admin_get(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})


@app.post("/admin")
def admin_post(reason: str = Form(...)):
    with Session(engine) as session:
        new_reason = Reason(content=reason)
        session.add(new_reason)
        session.commit()
    return RedirectResponse("/", status_code=303)


@app.post("/delete/{reason_id}")
def delete_reason(reason_id: int):
    with Session(engine) as session:
        reason = session.get(Reason, reason_id)
        if reason:
            reason.hidden = True
            session.commit()
    return RedirectResponse("/", status_code=303)

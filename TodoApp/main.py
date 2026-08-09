import os
from fastapi import FastAPI, Request, status
from .models import Base
from .database import engine
from .routers import auth, todos, admin, users
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

app = FastAPI()

Base.metadata.create_all(bind=engine)

# تحديد مسار مجلد static تلقائياً بالنسبة لمكان ملف main.py
script_dir = os.path.dirname(__file__)
static_abs_path = os.path.join(script_dir, "static")

app.mount("/static", StaticFiles(directory=static_abs_path), name="static")


@app.get("/")
def teest(request: Request):
    return RedirectResponse(url="/todos/todo-page",
                            status_code=status.HTTP_302_FOUND)


@app.get("/healthy")
def health_check():
    return {"status": "Healthy"}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
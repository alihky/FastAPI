from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Path, HTTPException, Request, templating, status
from starlette import status
from ..models import Todos
from ..database import SessionLocal
from pydantic import BaseModel, Field
from .auth import get_current_user
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="TodoApp/templates")

router = APIRouter(
    prefix="/todos",
    tags=["todos"]

)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page",
                                         status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access-token")
    return redirect_response


### Pages ###

@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()

        todos = db.query(Todos).filter(Todos.owner_id == user.get('id')).all()

        # التعديل الصحيح والمتوافق بدون عكرتة
        return templates.TemplateResponse(
            request=request,
            name="todo.html",
            context={"todos": todos, "user": user}
        )
    except:
        return redirect_to_login()


@router.get("/add-todo-page")
async def render_add_todo_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()

        # التعديل الصحيح: ترتيب المدخلات وفقاً للإصدار الحديث
        return templates.TemplateResponse(
            request=request,
            name="add-todo.html",
            context={"user": user}
        )
    except Exception as e:
        # هذه الطباعة في الـ Terminal ستكشف لك أي خطأ مستقبلي بدلاً من أن يختفي في الـ except
        print(f"تعكرت الدالة بسبب: {e}")
        return redirect_to_login()


@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()

        # 1. جلب المهمة بشرط أن تكون موجودة وتخص هذا المستخدم بالتحديد
        todo = db.query(Todos)\
            .filter(Todos.id == todo_id)\
            .filter(Todos.owner_id == user.get('id'))\
            .first()

        # إذا لم يتم العثور على المهمة (أو كانت لا تخصه)، نعيده لصفحة المهام الرئيسية
        if todo is None:
            return redirect_to_login()

        # 2. استدعاء القالب بالطريقة الحديثة والآمنة
        return templates.TemplateResponse(
            request=request,
            name="edit-todo.html",
            context={"todo": todo, "user": user}
        )
    except Exception as e:
        print(f"حدث خطأ في صفحة التعديل: {e}")
        return redirect_to_login()


### Endpoints ###

@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency,
                    todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
                  .filter(Todos.owner_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
    # ✅ تم التعديل لتطابق التست
    raise HTTPException(status_code=404, detail="Todo not found.")


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency,
                      db: db_dependency,
                      todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    todo_model = Todos(**todo_request.dict(),
                       owner_id=user.get('id'))

    db.add(todo_model)
    db.commit()

@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency,
                      todo_request: TodoRequest,
                      todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        # ✅ تم التعديل لتطابق التست
        raise HTTPException(status_code=404, detail="Todo not found")
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency,
                      todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        # ✅ تم التعديل لتطابق التست
        raise HTTPException(status_code=404, detail="Todo not found")
    db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).delete()

    db.commit()
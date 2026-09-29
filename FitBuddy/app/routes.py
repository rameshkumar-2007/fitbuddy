from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session
from uuid import uuid4
from .database import get_db
from .dependencies import require_admin
from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .gemini_generator import generate_workout_gemini
from .models import User
from .schemas import FeedbackRequest, UserInput
from .updated_plan import update_workout_plan
from .languages import LANGUAGES, normalize_language
from .starter_plan import build_starter_plan, build_starter_tip
from .config import get_settings

router=APIRouter()
templates=Jinja2Templates(directory="templates")
templates.env.globals["languages"] = LANGUAGES

def render_error(request,message,status=400,language="en-US"):
    return templates.TemplateResponse(request=request,name="index.html",context={"error":message,"language":language},status_code=status)

def ai_error_message(exc):
    if getattr(exc,"code",None) in (429,503):
        return "Gemini is temporarily unavailable or over quota. Please try again later."
    return f"AI generation failed: {exc}"

@router.get("/",response_class=HTMLResponse)
def home(request:Request): return templates.TemplateResponse(request=request,name="index.html",context={"error":None,"language":"en-US"})

@router.post("/generate-workout",response_class=HTMLResponse)
def generate_workout(request:Request,name:str=Form(...),age:int=Form(...),weight:float=Form(...),goal:str=Form(...),intensity:str=Form(...),language:str=Form("en-US"),db:Session=Depends(get_db)):
    language=normalize_language(language)
    try: data=UserInput(name=name,user_id=uuid4().hex,age=age,weight=weight,goal=goal,intensity=intensity)
    except Exception as e: return render_error(request,str(e),422,language)
    if not get_settings().gemini_api_key:
        plan=build_starter_plan(data.goal,data.intensity,data.age)
        tip=build_starter_tip(data.goal,data.age)
        language="en-US"
        generation_notice="Gemini is not configured. This is an English local starter plan, not an AI-generated plan."
    else:
        try:
            plan=generate_workout_gemini(data.name,data.age,data.weight,data.goal,data.intensity,language)
            tip=generate_nutrition_tip_with_flash(data.goal,data.age,language)
            generation_notice=None
        except Exception as e:
            if getattr(e,"code",None) not in (429,503):
                return render_error(request,ai_error_message(e),502,language)
            plan=build_starter_plan(data.goal,data.intensity,data.age)
            tip=build_starter_tip(data.goal,data.age)
            language="en-US"
            generation_notice="Gemini is temporarily unavailable or over quota. This is an English local starter plan, not an AI-generated plan."
    user=User(user_id=data.user_id,name=data.name,age=data.age,weight=data.weight,goal=data.goal,intensity=data.intensity,original_plan=plan,nutrition_tip=tip)
    db.add(user)
    db.commit(); db.refresh(user)
    return templates.TemplateResponse(request=request,name="result.html",context={"user":user,"plan":user.updated_plan or user.original_plan,"is_updated":bool(user.updated_plan),"error":None,"language":language,"generation_notice":generation_notice})

@router.post("/submit-feedback",response_class=HTMLResponse)
def submit_feedback(request:Request,user_id:str=Form(...),feedback:str=Form(...),language:str=Form("en-US"),db:Session=Depends(get_db)):
    language=normalize_language(language)
    try: data=FeedbackRequest(user_id=user_id,feedback=feedback)
    except Exception as e: raise HTTPException(status_code=422,detail=str(e))
    user=db.scalar(select(User).where(User.user_id==data.user_id))
    if not user: raise HTTPException(status_code=404,detail="User ID not found.")
    current=user.updated_plan or user.original_plan
    try:
        revised=update_workout_plan(current,data.feedback,user.age,user.goal,user.intensity,language)
        user.updated_plan=revised; user.feedback=data.feedback
        user.nutrition_tip=generate_nutrition_tip_with_flash(user.goal,user.age,language)
        db.commit(); db.refresh(user)
        msg="Your plan was updated from the feedback."
    except Exception as e:
        message=ai_error_message(e) if getattr(e,"code",None) in (429,503) else f"Could not update the plan: {e}"
        return templates.TemplateResponse(request=request,name="result.html",context={"user":user,"plan":current,"is_updated":bool(user.updated_plan),"error":message,"language":language},status_code=502)
    return templates.TemplateResponse(request=request,name="result.html",context={"user":user,"plan":user.updated_plan,"is_updated":True,"error":msg,"language":language})

@router.get("/view-all-users",response_class=HTMLResponse,dependencies=[Depends(require_admin)])
def view_all_users(request:Request,db:Session=Depends(get_db)):
    users=list(db.scalars(select(User).order_by(User.created_at.desc())).all())
    return templates.TemplateResponse(request=request,name="all_users.html",context={"users":users})

@router.get("/api/users",dependencies=[Depends(require_admin)])
def api_users(db:Session=Depends(get_db)):
    return [{"id":u.id,"user_id":u.user_id,"name":u.name,"age":u.age,"weight":u.weight,"goal":u.goal,"intensity":u.intensity,"has_updated_plan":bool(u.updated_plan)} for u in db.scalars(select(User).order_by(User.created_at.desc())).all()]

@router.get("/api/users/{user_id}",dependencies=[Depends(require_admin)])
def api_user(user_id:str,db:Session=Depends(get_db)):
    u=db.scalar(select(User).where(User.user_id==user_id))
    if not u: raise HTTPException(status_code=404,detail="User not found.")
    return {"user_id":u.user_id,"name":u.name,"age":u.age,"weight":u.weight,"goal":u.goal,"intensity":u.intensity,"original_plan":u.original_plan,"updated_plan":u.updated_plan,"feedback":u.feedback,"nutrition_tip":u.nutrition_tip}

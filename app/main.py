from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse

from app.core.config import get_settings
from app.api.routes import auth, pacientes, historias, citas, contabilidad, dashboard
from app.core.security import decode_token # <--- Importa esto

settings = get_settings()

app = FastAPI(
    title="Sistema de Gestión Médica",
    description="SaaS para consultorio médico - Paraguay",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url=None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.environment == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files y templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Registrar rutas de API
app.include_router(auth.router, prefix="/api")
app.include_router(pacientes.router, prefix="/api")
app.include_router(historias.router, prefix="/api")
app.include_router(citas.router, prefix="/api")
app.include_router(contabilidad.router, prefix="/api")
app.include_router(dashboard.router)


# ─── Rutas de páginas HTML ────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    token = request.cookies.get("access_token")
    print(f"DEBUG: Token detectado en cookie: {token is not None}")
    
    payload = decode_token(token) if token else None
    print(f"DEBUG: Payload válido: {payload is not None}")
    
    if payload:
        print("DEBUG: Redirigiendo a /dashboard porque el token ES VALIDO")
        return RedirectResponse(url="/dashboard")
    
    print("DEBUG: Mostrando login.html porque NO HAY token o es INVALIDO")
    response = templates.TemplateResponse("login.html", {"request": request})
    if token:
        response.delete_cookie("access_token")
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def pagina_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/pacientes", response_class=HTMLResponse)
async def pagina_pacientes(request: Request):
    return templates.TemplateResponse("pacientes.html", {"request": request})


@app.get("/agenda", response_class=HTMLResponse)
async def pagina_agenda(request: Request):
    return templates.TemplateResponse("agenda.html", {"request": request})


@app.get("/contabilidad", response_class=HTMLResponse)
async def pagina_contabilidad(request: Request):
    return templates.TemplateResponse("contabilidad.html", {"request": request})


@app.get("/health")
async def health():
    return {"status": "ok"}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.timing_middleware import TimingMiddleware
from app.api.auth import router as auth_router
from app.api.user import router as user_router
from app.api.post import router as post_router

def get_app() -> FastAPI:
    _app = FastAPI(
        title="Users, Post y Tags"
    )    
    _app.include_router(auth_router, prefix="/api/v1/auth", tags=["Autorizacion"])
    _app.include_router(user_router, prefix="/api/v1/users", tags=["Usuários"])
    _app.include_router(post_router, prefix="/api/v1/posts", tags=["Post"])
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )        
    _app.add_middleware(
        TimingMiddleware
    )
    return _app
app = get_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

from fastapi import FastAPI

from api.api import router as user_router

if __name__ == "main":
    app = FastAPI(
        routers=[]
    )

    @app.get('/')
    def root():
        return 'Welcome to User Profiles'

    app.include_router(user_router)

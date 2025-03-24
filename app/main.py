from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, links
from app.database import engine, Base
import uvicorn


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="url shortener app"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(links.router)

app.add_api_route("/{short_code}", links.redirect_to_original, methods=["GET"])

@app.get("/")
async def root():
    return {"message": "url shortener app"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

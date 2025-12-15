from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from coreview3d.routers.data_router import data_router
from coreview3d.routers.session_router import session_router

app = FastAPI(
    title="CoreView3D Backend",
    version="1.0.0",
    description="Mining visualization API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(session_router)
app.include_router(data_router)

@app.get("/")
async def health_check():
    return {"status": "online", "service": "CoreView3D"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
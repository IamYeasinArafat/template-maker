from api.v2 import router as v2_router
from api.v1 import router as v1_router
from api.v3 import router as v3_router
from fastapi import FastAPI

app = FastAPI()
app.include_router(v2_router)
app.include_router(v1_router)
app.include_router(v3_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
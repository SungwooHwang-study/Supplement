
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def root():
    return {"status": "alive"}

if __name__ == "__main__":
    uvicorn.run("keepalive_server:app", host="0.0.0.0", port=8080)

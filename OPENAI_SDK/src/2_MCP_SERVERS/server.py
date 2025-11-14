# server.py
from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
from agent import browser_controller  # your updated agent
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["chrome-extension://<your-extension-id>"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserRequest(BaseModel):
    tab_url: str | None = None  
    user_message: str



@app.post("/ask")
async def ask_agent(req: UserRequest):
    """
    Receives user message and optional tab URL.
    Calls the agent and returns the response.
    """
    try:
        response_text = await browser_controller(req.tab_url, req.user_message)
        return {"response": response_text}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
# http://127.0.0.1:8000/ask



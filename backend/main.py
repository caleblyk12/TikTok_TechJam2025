# app.py
from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
from fastapi.middleware.cors import CORSMiddleware

# ------------------------------
# Initialize app
# ------------------------------
app = FastAPI(title="Tiktok Shop ChatBot Backend")

# Enable CORS for frontend calls 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend URL 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------
# Hardcoded Product Data
# ------------------------------
PRODUCTS = [
    {"name": "TikTok Hoodie", "price": "$39.99", "shipping": "3-5 days", "description": "available in blue, red, green. made of cotton"},
    {"name": "TikTok Cap", "price": "$19.99", "shipping": "2-3 days", "description": "moisture wicking, 5 panel, avail in black and white"},
    {"name": "TikTok Water Bottle", "price": "$14.99", "shipping": "5-7 days", "description": "thermal insulating, 500ml, avail in pink and grey"}
]

# ------------------------------
# Pydantic model for chat requests
# ------------------------------
class ChatRequest(BaseModel):
    message: str

# ------------------------------
# Environment variable for OpenAI API key
# ------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Please set OPENAI_API_KEY in environment variables")

# ------------------------------
# Chat endpoint
# ------------------------------
@app.post("/chat")
def chat(request: ChatRequest):
    # Format product info as text for the AI prompt
    product_text = "\n".join(
        [f"{p['name']} - Price: {p['price']}, Shipping: {p['shipping']}, Details: {p['description']}" for p in PRODUCTS]
    )

    # Build OpenAI API request
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",  
        "messages": [
            {
                "role": "system", #context for model
                "content": (
                    "You are a helpful TikTok Shop assistant. Keep responses extremely concise, only answering whats required. "
                    f"Use the following product info to answer questions:\n{product_text}"
                )
            },
            {"role": "user", "content": request.message} #actual prompt
        ],
        "max_tokens": 75
    }

    

    try:
        #call openai api
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response_json = response.json()
        #format of json response as per openai docs. Extract message and return
        ai_message = response_json["choices"][0]["message"]["content"]
        return {"response": ai_message}
    
    except: #simple catch all
        #Any errors go into here. Check if have enough credits, if url is correct, if internet no issue
        return {"response": "Sorry, I'm having trouble right now. Please try again."}
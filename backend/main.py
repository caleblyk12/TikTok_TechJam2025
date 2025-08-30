# app.py
from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
from fastapi.middleware.cors import CORSMiddleware
import re
from dotenv import load_dotenv

# ------------------------------
# Initialize app
# ------------------------------
app = FastAPI(title="Tiktok Shop AI search bot")

# Enable CORS for frontend calls 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Replace with frontend URL 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------
# Hardcoded Product Data
# ------------------------------
PRODUCTS = [
    {"id": 1, "name": "Cool Hoodie", "price": "$29.99", "shipping": "3-5 days", "colours": "blue, red, green", "description": "made of cotton", "url": "https://images-na.ssl-images-amazon.com/images/I/61q6KBg7LWL._AC_UL1339_.jpg"},
    {"id": 2, "name": "TikTok Hoodie", "price": "$39.99", "shipping": "7 days", "colours": "black", "description": "made of polyester", "url": "https://i.etsystatic.com/28439783/r/il/be5c0c/2996437775/il_1588xN.2996437775_ds1r.jpg"},
    {"id": 3, "name": "Muscle T Shirt", "price": "$49.99", "shipping": "6 days", "colours": "black, white", "description": "drifit, compression tee", "url": "https://i.pinimg.com/originals/e9/f8/0d/e9f80dbe39759cf38646450dd610a902.jpg"},
    {"id": 4, "name": "TikTok Cap", "price": "$19.99", "shipping": "2-3 days", "colours": "black, white", "description": "moisture wicking, 5 panel", "url": "https://img.joomcdn.net/9209c37d5f90bdcd70544a51d2093e37e4ccd048_original.jpeg"},
    {"id": 5, "name": "Medium Water Bottle", "price": "$14.99", "shipping": "5-7 days", "colours": "pink, green", "description": "thermal insulating, 500ml", "url": "https://img.freepik.com/premium-photo/pink-thermos-bottle-isolated-white-background_884296-42265.jpg"},
    {"id": 6, "name": "Small Water Bottle", "price": "$10.99", "shipping": "2 days", "colours": "blue", "description": "thermal insulating, 250ml", "url": "https://market.promarket-eu.com/wp-content/uploads/2020/12/Termo-AQUAPHOR.jpg"},
    {"id": 7, "name": "Large Water Bottle", "price": "$17.99", "shipping": "10 days", "colours": "blue, red", "description": "thermal insulating, 750ml", "url": "https://assets.fishersci.com/TFS-Assets/CCG/Thermo-Scientific/product-images/19-1417229-0340916D-STD-01.jpg-650.jpg"}
]

# ------------------------------
# Pydantic model for chat requests (need these schemas for body of requests)
# ------------------------------
class ChatRequest(BaseModel):
    message: str

# ------------------------------
# Environment variable for OpenAI API key
# ------------------------------
# Load .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Please set OPENAI_API_KEY in environment variables")

# ------------------------------
# Chat endpoint
# ------------------------------
@app.post("/chat")
def chat(request: ChatRequest):
    # Format product info as text for the AI prompt
    product_text = "\n".join([
        f"ID:{p['id']} | Name:{p['name']} | Price:{p['price']} | Shipping:{p['shipping']} | Colours:{p['colours']} | Description:{p['description']}"
        for p in PRODUCTS
    ])

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
                "content": f"""
                    You are a TikTok Shop search assistant. Your job is to recommend products from the following list based on the user's query. Follow these rules carefully:

                    1. Only mention metrics or characteristics explicitly requested by the user (price, shipping, colour, volume, material, etc.). Note that some info is under description in the list below.
                    2. If products are suitable, recommend 1-3 products very concisely. If not, you may recommend 0 (but ideally not). Do not include any product not relevant to the user's explicit criteria.
                    Example format for a user requesting cheap bottles with many colours and > 500ml:
                    I found 2 bottles with more than 500ml. Here they are in increasing price. The medium bottle has 2 colours, the large bottle has 3.
                    Example format for a vague request like im looking for clothing:
                    Below are some articles of clothing ive found.
                    For vague requests, just recommend 1-3 suitable products that fit the request, if they exist. If not, recommend 0. 
                    3. Include the numeric product IDs (from the 'id' field in the product list below) in this exact format at the end of ALL your responses:
                    PRODUCT_IDS: [5, 7]
                    Replace these example numbers with the actual IDs of the products you are recommending. 
                    The leftmost ID should be the most suitable product. For eg if user asks for cheap products, left most id in the PRODUCT_IDS list is the cheapest. Or if user asks for colour variety, leftmost has most colours. Remember to mention these metrics in your response. 
                    Unsuitable product ids should not be in the list at all. Remember, recommend only 0-3 products.
                    4. If the users query is irrelevant, doesn't request recommendations, or you have 0 recommendations suitable, reply only with:
                    Sorry, no matching products! PRODUCT_IDS:[]
                    5. Keep all responses extremely concise—no extra commentary.
                    6. Remember to only mention metrics queried by the user. For example if they ask for clothing, just give the names, dont mention price or colours. 
                    But if they ask for cheap bottles, then mention names and price, but dont mention irrelevant metrics (shipping, colours, etc)
                    Another example is if they ask for head wear with colour variety, then respond with the name, and colour quantity, but not price or shipping etc.
                    7. Use the following product info to answer queries:
                    {product_text}
                    """
            },
            {"role": "user", "content": request.message} #actual prompt
        ],
        "max_tokens": 200
    }

    

    try:
        #call openai api
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response_json = response.json()
        #format of json response as per openai docs. Extract message.
        ai_message = response_json["choices"][0]["message"]["content"]

        # Log the raw response for debugging
        print("AI raw response:", ai_message)

        # Extract product IDs
        ids_match = re.search(r"PRODUCT_IDS:\s*\[(.*?)\]", ai_message)
        product_ids = []
        if ids_match:
            product_ids = [int(x.strip()) for x in ids_match.group(1).split(",") if x.strip()]
        
        # Remove PRODUCT_IDS line from AI text
        clean_message = re.sub(r"PRODUCT_IDS:\s*\[.*?\]", "", ai_message).strip()

        # Filter products to return
        relevant_products = [p for p in PRODUCTS if p["id"] in product_ids]
        return {"response": clean_message, "products": relevant_products}
    
    except Exception as e: #simple catch all
        print("Error: ", e)
        #Any errors go into here. Check if have enough credits, if url is correct, if internet no issue
        return {"response": "Sorry, I'm having trouble right now. Please try again.", "products": []}
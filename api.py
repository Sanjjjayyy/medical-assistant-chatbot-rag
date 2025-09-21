# api.py

import logging
from fastapi import FastAPI, Form, HTTPException, Request, Response
from pydantic import BaseModel
from twilio.twiml.messaging_response import MessagingResponse
from chatbot_logic import chatbot_instance

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Medical Assistant Chatbot API")

# --- UPDATED: The request now includes a session_id ---
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default_session"

@app.get("/", summary="Root endpoint")
def read_root():
    return {"status": "Medical Chatbot API is running"}

@app.post("/chat", summary="Process a user query")
def chat(request: ChatRequest):
    """Endpoint for general chat. Receives JSON with 'message' and 'session_id'."""
    user_query = request.message
    session_id = request.session_id
    
    if not user_query:
        raise HTTPException(status_code=400, detail="No message provided")
    
    try:
        # Pass the session_id to the chatbot logic
        response = chatbot_instance.get_answer(query=user_query, session_id=session_id)
        return {"reply": response.get("result", "Sorry, I encountered an error.")}
    except Exception as e:
        logger.error(f"Error processing /chat request: {e}")
        raise HTTPException(status_code=500, detail="Failed to process the request")

@app.post("/twilio-webhook", summary="Webhook for Twilio")
async def twilio_webhook(request: Request):
    """Webhook for Twilio. Uses the 'From' phone number as the session_id."""
    try:
        form_data = await request.form()
        incoming_msg = form_data.get('Body', '')
        # --- NEW: Use the sender's phone number as a unique session ID ---
        session_id = form_data.get('From', 'unknown_twilio_user')

        if not incoming_msg:
            return Response(content="No message body found", status_code=400)

        # Pass the unique session_id to the chatbot logic
        answer_data = chatbot_instance.get_answer(query=incoming_msg, session_id=session_id)
        bot_reply = answer_data.get("result", "Sorry, an error occurred.")

        response = MessagingResponse()
        response.message(bot_reply)
        
        return Response(content=str(response), media_type="application/xml")
    except Exception as e:
        logger.error(f"Error processing Twilio webhook: {e}")
        response = MessagingResponse()
        response.message("We're sorry, but an internal error occurred.")
        return Response(content=str(response), media_type="application/xml", status_code=500)
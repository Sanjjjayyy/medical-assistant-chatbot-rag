# Multilingual Medical Assistant Chatbot

This project is a sophisticated, multilingual medical assistant chatbot that uses a **Retrieval-Augmented Generation (RAG)** architecture to answer medical questions based on a provided knowledge base. It leverages the power of Google's **Gemini API** for language understanding and generation, supports conversation history, an deployed  **Telegram** 

## Features

-   **Retrieval-Augmented Generation (RAG)**: The chatbot answers questions based on a custom medical knowledge base, ensuring factual and relevant responses. It uses a FAISS vector store for efficient document retrieval.
-   **Powered by Gemini**: Utilizes Google's powerful `gemini-1.5-flash` model for high-quality, fast, and context-aware responses.
-   **Multilingual Support**: Can understand and respond in multiple languages, including English, Marathi, Urdu, Tamil, and Telugu.
-   **Conversation Memory**: Remembers the context of the conversation for each user, allowing for natural, follow-up questions.
-   **Asynchronous API**: Built with **FastAPI** for a high-performance, scalable backend.

## Project Structure
```bash
├── api.py                     # FastAPI server with webhook endpoints
├── chatbot_logic.py           # Core RAG Chain
├── telegram_bot.py            # Script to connect to Telegram
├── data/
│   └── medical_text_data.csv  # Medical data
├── .env                       # Api key and Variables
└── requirements.txt           # All dependencies
```

## Getting Started

Follow these steps to set up and run the project on your local machine.


### 1. Clone the Repository

```bash
git clone <https://github.com/Sanjjjayyy/medical-assistant-chatbot-rag>
cd medical-assistant-chatbot-rag
```
### 2. Set up a Conda environment
```bash
conda create --name med-assistant python=3.10
conda activate med-assistant
```

### 3. Install Dependencies
 Install all the required Python packages using the `requirements.txt` file.

``` bash
pip install -r requirements.txt
```
### 4. Set Up Environment Variables

Create a `.env` file to store environment variables

Add your keys:
 - GOOGLE_API_KEY → from Google AI Studio
 - TELEGRAM_TOKEN → via @BotFather on Telegram
 - FASTAPI_URL → leave blank for now

### 5. Run the Application

You’ll need 3 terminals.

**Terminal 1: Start FastAPI Server**

```bash
conda activate rag-chatbot
uvicorn api.app:app --reload --port 8000
```

Wait for the message indicating the application startup is complete.

**Terminal 2: Expose with ngrok**

Authenticate ngrok (once):
```bash
ngrok config add-authtoken <YOUR_NGROK_AUTHTOKEN>
```
Start tunnel:
```bash
ngrok 8000
```
After running it,you can see a forwarding URL

Copy the https:// forwarding URL from ngrok.
Update `.env` →

```bash
FASTAPI_URL=https://<your-ngrok-url>.ngrok-free.app/chat
```
Make Sure to Add `/chat` at the end of url.

**Terminal 3: Run Telegram Bot**


```bash
python telegram_bot.py
```
Now you can ask Questions to Your Multilingual Medical Chatbot at Telegram
# chatbot_logic.py

import logging
import os
from dotenv import load_dotenv

load_dotenv()

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
INDEX_DIR = "faiss_index"
EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# --- This is the prompt that defines the bot's persona and instructions ---
custom_prompt_template = """
You are a multilingual medical assistant chatbot. Your role is to provide **accurate, safe, empathetic medical guidance** in **4–5 lines maximum**, using RAG knowledge when available.

Guidelines:
1. Detect the user’s language and respond in the same language.
2. Keep answers concise (4–5 lines).
3. Do not directly state or guess diseases. Instead:
   - Explain what the symptom might mean in simple terms.
   - Give safe self-care tips (hydration, rest, monitoring).
   - Highlight when to seek medical attention.
4. Always ensure safety:
   - No prescriptions or treatments.
   - Remind the user to consult a doctor for confirmation or serious issues.
5. If no RAG info is found, provide general safe advice and recommend professional help.

Example:
User: "Mujhe bukhar aur sore throat hai."  
Assistant: "Bukhar aur gale ka dard kabhi kabhi viral infection se juda ho sakta hai, lekin exact karan sirf doctor bata sakte hain. Aap hydration maintain karein aur rest lein. Agar bukhar 3 din se zyada rahe ya symptoms badhein, toh doctor se milna zaroori hai."

Context: {context}
Chat History: {chat_history}
Question: {question}
Answer:
"""

class Chatbot:
    """A singleton class to manage chatbot resources and conversations."""
    def __init__(self):
        logger.info("Initializing Chatbot...")
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        
        self.vect = self._load_vectorstore()
        self.llm = self._load_llm()
        self.prompt = PromptTemplate(
            template=custom_prompt_template,
            input_variables=["context", "chat_history", "question"]
        )
        self.memories = {}
        logger.info("Chatbot initialized successfully.")

    def _load_vectorstore(self):
        """Loads the FAISS vectorstore."""
        # --- THIS BLOCK IS NOW CORRECTED ---
        try:
            logger.info(f"Loading embedding model: {EMBED_MODEL}")
            embed = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
            logger.info(f"Loading FAISS index from: {INDEX_DIR}")
            return FAISS.load_local(INDEX_DIR, embed, allow_dangerous_deserialization=True)
        except Exception as e:
            logger.error(f"Failed to load vectorstore: {e}")
            raise

    def _load_llm(self):
        """Loads the Google Gemini LLM."""
        try:
            logger.info("Loading Google Gemini LLM (gemini-1.5-flash)...")
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0.4,
                convert_system_message_to_human=True
            )
        except Exception as e:
            logger.error(f"Failed to load LLM: {e}")
            raise

    def get_or_create_memory(self, session_id: str) -> ConversationBufferMemory:
        """Gets or creates a memory object for a session."""
        if session_id not in self.memories:
            logger.info(f"Creating new memory for session_id: {session_id}")
            self.memories[session_id] = ConversationBufferMemory(
                memory_key='chat_history', 
                return_messages=True,
                output_key='answer' # Ensure the output key is set
            )
        return self.memories[session_id]

    def get_conversation_chain(self, session_id: str) -> ConversationalRetrievalChain:
        """Creates a conversational chain for a given session with the custom prompt."""
        memory = self.get_or_create_memory(session_id)
        retriever = self.vect.as_retriever(search_type="similarity", search_kwargs={"k": 5})

        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=memory,
            combine_docs_chain_kwargs={"prompt": self.prompt}, # Injects our custom prompt
            return_source_documents=True
        )
        return conversation_chain

    def get_answer(self, query: str, session_id: str = "default_session") -> dict:
        """Gets an answer from the conversational chain."""
        logger.info(f"Processing query for session_id: {session_id}")
        conversation_chain = self.get_conversation_chain(session_id)
        result = conversation_chain.invoke({"question": query})
        
        return {
            "result": result["answer"],
            "sources": [d.metadata for d in result.get("source_documents", [])]
        }

# Create a single, reusable instance
chatbot_instance = Chatbot()
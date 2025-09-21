# main.py (Modified Version)

from chatbot_logic import chatbot_instance # <-- IMPORT the centralized logic
import pprint

if __name__ == "__main__":
    print("✅ Chatbot ready. Type 'exit' to quit.")

    while True:
        query = input("\n👤 You: ")
        if query.lower() in ["exit", "quit"]:
            break
        
        # Use the single chatbot instance to get the answer
        result = chatbot_instance.get_answer(query)

        print("\n🤖 Bot:", result["result"])
        print("📎 Sources:")
        pprint.pprint(result["sources"])
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def ask_llm(prompt, conversation_history=[]):
    conversation_history.append({"role": "user", "content": prompt})

    conversation_text = "\n".join(
        f"{msg['role']}: {msg['content']}" for msg in conversation_history
    )

    payload = {
        "model": "phi3",
        "prompt": conversation_text,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        data = response.json()

        # Safely grab the reply
        reply = data.get("response", "").strip()

        if not reply:
            raise ValueError("No valid response from phi3")

    except Exception as e:
        print("❌ LLM ERROR:", e)
        print("💥 Raw response text:", getattr(response, 'text', 'NO TEXT'))
        reply = "Sorry, I couldn’t understand that. Can you say it differently?"

    conversation_history.append({"role": "assistant", "content": reply})
    return reply, conversation_history

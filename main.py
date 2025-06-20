from voice_utils import record_audio, transcribe_audio, synthesize_speech
from conversation_engine import ask_llm
from calendar_utils import get_free_slots, create_event
from time_parser import parse_time_string
from memory_store import MemoryStore

# Define the assistant's persona
conversation_history = [
    {
        "role": "system",
        "content": (
            "You are a smart voice-enabled AI agent named SchedulerBot. "
            "You help users schedule meetings via Google Calendar. "
            "If something is unclear, ask follow-up questions to gather details like time, date, or duration. "
            "Speak like a helpful assistant. Do not say you're an AI made by Microsoft. "
            "Assume you CAN schedule events — your code will handle the calendar part. "
            "If the user asks for available slots, wait for the assistant's code to provide them."
        )
    }
]

memory = MemoryStore()

while True:
    record_audio("input.wav", duration=6)
    user_input = transcribe_audio("input.wav")
    print(f"User: {user_input}")

    if not user_input.strip():
        synthesize_speech("Sorry, I didn't catch that.")
        continue

    # Handle 'available slots' directly with calendar API
    if "available slot" in user_input.lower() or "free time" in user_input.lower():
        duration = memory.recall("duration") or "1 hour"
        duration_minutes = 60 if "hour" in duration else int(''.join(filter(str.isdigit, duration)))

        slots = get_free_slots(duration_minutes=duration_minutes)
        if not slots:
            response = "Sorry, no free slots were found in the upcoming week."
        else:
            top_slots = slots[:2]
            slot_strings = [s.strftime("%A at %I:%M %p") for s in top_slots]
            response = f"I found these available time slots: {slot_strings[0]} and {slot_strings[1]}. Would you like to schedule one?"

        synthesize_speech(response)
        print("Bot:", response)
        continue

    # Step 1: Parse duration
    if "minute" in user_input or "hour" in user_input:
        memory.remember("duration", user_input)
        synthesize_speech("Got it. What day and time works best for you?")
        continue

    # Step 2: Parse preferred time
    try:
        dt = parse_time_string(user_input)
        memory.remember("start_time", dt)

        duration = memory.recall("duration") or "1 hour"
        duration_minutes = 60 if "hour" in duration else int(''.join(filter(str.isdigit, duration)))
        slots = get_free_slots(duration_minutes=duration_minutes)

        available_slot = None
        for slot in slots:
            if slot >= dt:
                available_slot = slot
                break

        if not available_slot:
            synthesize_speech("Sorry, there are no available slots at that time. Please suggest another.")
            continue

        memory.remember("slot_suggestion", available_slot)
        synthesize_speech(f"I found a slot at {available_slot.strftime('%A %I:%M %p')}. Should I schedule it?")
        continue

    except Exception:
        pass  # Fall through to default

    # Step 3: Confirm
    if "yes" in user_input.lower() or "confirm" in user_input.lower():
        chosen_slot = memory.recall("slot_suggestion")
        duration = memory.recall("duration") or "1 hour"
        duration_minutes = 60 if "hour" in duration else int(''.join(filter(str.isdigit, duration)))

        create_event(chosen_slot, duration_minutes)
        synthesize_speech("Your meeting is scheduled!")
        break

    # Step 4: Let the LLM handle everything else
    bot_prompt = user_input
    response, conversation_history = ask_llm(bot_prompt, conversation_history)
    print(f"Bot: {response}")
    synthesize_speech(response)
    continue

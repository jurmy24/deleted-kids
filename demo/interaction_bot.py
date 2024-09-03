from pydantic import UUID4
from vapi_python import Vapi
from dotenv import load_dotenv
import os
import threading


class InteractionBot:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(InteractionBot, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            load_dotenv()  # Load environment variables from .env file
            api_key = os.getenv("VAPI_PUBLIC_KEY")
            if api_key is None:
                raise ValueError(
                    "API key for Vapi is not set in the environment variables."
                )
            self.vapi = Vapi(api_key=api_key)
            self._initialized = True

    def start_interaction(self, assistant_id: UUID4, first_message: str, context: str):
        """Start the interactive session using Vapi."""
        assistant_overrides = {
            "firstMessage": first_message,
            "context": context,
        }

        print("\nStarting interaction with the assistant...\n")

        self.vapi.start(
            assistant_id=assistant_id, assistant_overrides=assistant_overrides
        )

    def stop_interaction(self):
        """Stop the interactive session."""
        self.vapi.stop()
        print("Interaction stopped.")

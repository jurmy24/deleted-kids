from pydantic import UUID4
from vapi_python import Vapi
from dotenv import load_dotenv
import os


class InteractionBot:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        api_key = os.getenv("VAPI_PUBLIC_KEY")
        self.vapi = Vapi(api_key=api_key)

    def start_interaction(self, assistant_id: UUID4, context: str, first_message: str):
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

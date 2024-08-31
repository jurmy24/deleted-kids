from vapi_python import Vapi
from dotenv import load_dotenv
import os


class InteractionBot:
    def __init__(self, model: str = "gpt-3.5-turbo"):
        load_dotenv()  # Load environment variables from .env file
        api_key = os.getenv("VAPI_PUBLIC_KEY")
        self.vapi = Vapi(api_key=api_key)
        self.language = None
        self.voice_id = None
        self.model = model

    def setup(self, language: str, voice: str):
        self.language = language
        self.voice_id = voice
        # FOR NOW:
        self.voice_id = "XB0fDUnXU5powFXDhCwa"

    def start_interaction(self, context: str, first_message: str):
        """Start the interactive session using Vapi."""
        assistant = {
            "firstMessage": first_message,
            "context": context,
            "model": self.model,
            "voice": self.voice_id,
            "recordingEnabled": False,
            "interruptionsEnabled": True,
        }

        #  77c55889-6355-45e7-ac59-bd040ca3a14e

        print("\nStarting interaction with the assistant...\n")

        # Start the VAPI assistant
        self.vapi.start(assistant=assistant)

    def stop_interaction(self):
        """Stop the interactive session."""
        self.vapi.stop()
        print("Interaction stopped.")

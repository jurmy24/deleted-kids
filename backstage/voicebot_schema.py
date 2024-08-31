from pydantic import BaseModel, UUID4
from typing import List


class VoiceBot(BaseModel):
    story_id: int
    bot_id: UUID4


class VoiceBots(BaseModel):
    stories: List[VoiceBot]

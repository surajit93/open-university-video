"""
scene_schema.py
Canonical scene contract.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
import uuid


@dataclass
class VisualConfig:
    mode: str
    concept: str
    style_profile: str
    camera_motion: str


@dataclass
class TypographyConfig:
    style: str
    highlight_words: List[str]
    effect: str


@dataclass
class AudioConfig:
    bg_curve: str
    sfx: List[str]
    silence_before_reveal: bool = False


@dataclass
class RetentionConfig:
    pattern_interrupt: bool
    contrast_shift: bool


@dataclass
class Scene:
    narration: str
    duration: float
    scene_type: str
    visual: VisualConfig
    typography: TypographyConfig
    audio: AudioConfig
    retention: RetentionConfig
    scene_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    chapter: str = "unassigned"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scene_id": self.scene_id,
            "chapter": self.chapter,
            "narration": self.narration,
            "duration": self.duration,
            "scene_type": self.scene_type,
            "visual": self.visual.__dict__,
            "typography": self.typography.__dict__,
            "audio": self.audio.__dict__,
            "retention": self.retention.__dict__,
        }

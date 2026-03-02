"""
text_style_registry.py
Centralized typography style system.
"""

from dataclasses import dataclass


@dataclass
class TextStyle:
    font: str
    font_size: int
    color: str
    stroke_color: str
    stroke_width: int
    kerning: int


class TextStyleRegistry:

    def __init__(self):
        self.styles = {
            "kinetic_bold": TextStyle(
                font="Montserrat-Bold",
                font_size=90,
                color="white",
                stroke_color="black",
                stroke_width=3,
                kerning=1
            ),
            "chapter_intro": TextStyle(
                font="Montserrat-ExtraBold",
                font_size=120,
                color="#00FFC6",
                stroke_color="black",
                stroke_width=4,
                kerning=2
            ),
            "countdown": TextStyle(
                font="Montserrat-Black",
                font_size=160,
                color="#FF0055",
                stroke_color="black",
                stroke_width=5,
                kerning=2
            )
        }

    def get(self, style_name: str) -> TextStyle:
        return self.styles.get(style_name, self.styles["kinetic_bold"])

from dataclasses import dataclass, field
import copy


@dataclass
class Block:
    x0: float
    y0: float
    x1: float
    y1: float
    lines: str
    page: int

    max_font_size: float | None = None
    is_bold: bool = False

    @classmethod
    def get(
        cls,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        lines: str,
        page: int,
        max_font: float,
        is_bold: bool,
    ):
        return cls(x0, y0, x1, y1, lines, page, max_font, is_bold)

    def model_copy(self, deep: bool = True) -> "Block":
        if deep:
            return copy.deepcopy(self)
        else:
            return copy.copy(self)

    def __str__(self):
        return f"""
<Block: x0={self.x0}, y0={self.y0}, x1={self.x1}, y1={self.y1}>
{self.lines}
<\\Block>
        """


@dataclass
class Section:
    title: str

    themes: list[str] = field(default_factory=list)

    subsection: list["Subsection"] = field(default_factory=list)

    content_blocks: list[Block] = field(default_factory=list)


@dataclass
class Subsection:
    title: str

    themes: list[str] = field(default_factory=list)

    content_blocks: list[Block] = field(default_factory=list)

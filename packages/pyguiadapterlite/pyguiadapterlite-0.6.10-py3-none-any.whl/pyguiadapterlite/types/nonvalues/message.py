import dataclasses
from tkinter import Widget, Message, Label
from typing import Optional, Type, Union, Literal

from pyguiadapterlite.components.valuewidget import (
    NonValueParameterWidgetConfig,
    NonValueParameterWidget,
)


@dataclasses.dataclass(frozen=True)
class MessageLabelConfig(NonValueParameterWidgetConfig):
    text: str = ""
    width: Optional[int] = None
    bg: Optional[str] = None
    fg: Optional[str] = None
    font: Union[tuple, str, None] = None
    justify: Literal["left", "center", "right"] = None
    anchor: Literal["w", "center", "e"] = "center"
    relief: Literal["flat", "raised", "sunken", "groove", "ridge"] = None
    borderwidth: Optional[int] = None

    @classmethod
    def target_widget_class(cls) -> Type["MessageLabel"]:
        return MessageLabel


class MessageLabel(NonValueParameterWidget):

    ConfigClass = MessageLabelConfig

    def __init__(self, parent: Widget, parameter_name: str, config: MessageLabelConfig):

        self._message: Optional[Message] = None
        self._is_built = False

        super().__init__(parent, parameter_name, config)

    def build(self) -> "MessageLabel":
        if self._is_built:
            return self
        self._message = Label(
            self,
            text=self._config.text,
            bg=self._config.bg,
            fg=self._config.fg,
            font=self._config.font,
            justify=self._config.justify,
            anchor=self._config.anchor,
            width=self._config.width,
            borderwidth=self._config.borderwidth,
            relief=self._config.relief,
        )
        self._message.pack(fill="both", expand=True, padx=5, pady=5)
        self._is_built = True
        return self

import dataclasses
from tkinter import Widget
from tkinter.ttk import Button
from typing import Optional, Callable, Any, Type, Literal

from pyguiadapterlite.components.valuewidget import (
    NonValueParameterWidgetConfig,
    NonValueParameterWidget,
)


@dataclasses.dataclass(frozen=True)
class ButtonConfig(NonValueParameterWidgetConfig):
    text: str = ""
    side: Literal["left", "right", "top", "bottom"] = "left"
    fill: Literal["x", "y", "both", "none"] = "none"
    expand: bool = False
    on_click: Optional[Callable[["ButtonWidget"], Any]] = None

    @classmethod
    def target_widget_class(cls) -> Type["ButtonWidget"]:
        return ButtonWidget


class ButtonWidget(NonValueParameterWidget):
    ConfigClass = ButtonConfig

    def __init__(self, parent: Widget, parameter_name: str, config: ButtonConfig):
        self._button: Optional[Button] = None
        self._is_built = False
        super().__init__(parent, parameter_name, config)

    def build(self) -> "ButtonWidget":
        if self._is_built:
            return self
        self._button = Button(self, text=self._config.text, command=self._on_click)
        self._button.pack(
            side=self._config.side, fill=self._config.fill, expand=self._config.expand
        )
        self._is_built = True
        return self

    def _on_click(self):
        if not self._config.on_click:
            return
        self._config.on_click(self)

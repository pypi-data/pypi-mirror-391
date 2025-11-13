from django.http import HttpRequest

from pydantic import BaseModel
from newsflash.base import TextWidget


class ValueDisplayContext(BaseModel):
    id: str
    label: str
    value: str
    swap_oob: bool


class ValueDisplay(TextWidget):
    template_name: str = "text/value_display"
    label: str
    value: str

    def _build(self, request: HttpRequest) -> ValueDisplayContext:
        assert self.id is not None
        return ValueDisplayContext(
            id=self.id,
            label=self.label,
            value=self.value,
            swap_oob=self.swap_oob,
        )

    def set_value(self, value: str) -> None:
        self.value = value
        self._updated = True

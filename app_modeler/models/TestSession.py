from dataclasses import dataclass, field
from typing import Optional

from app_modeler.appium_helpers.AppiumInterface import AppiumInterface
from app_modeler.appium_helpers.elements.ElementsDiscover import ElementData
from app_modeler.models.FunctionCall import FunctionCall


@dataclass
class ClassData:
    name: str
    screenshot: bytes
    elements: [ElementData]
    class_str: str
    view: Optional[AppiumInterface] = None
    function_candidates: [FunctionCall] = field(default_factory=list)


@dataclass
class TestSession:
    classes: [ClassData] = field(default_factory=list)
    call_history: [FunctionCall] = field(default_factory=list)


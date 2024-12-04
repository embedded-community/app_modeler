import json

from app_modeler.ai.OpenAiAssistant import OpenAIAssistant, AiModel
from app_modeler.appium_helpers.elements.ElementsDiscover import ElementData


class ClassRepresentation(AiModel):
    implementation_as_str: str

class AppiumClassGenerator:
    def __init__(self, ai_assistant: OpenAIAssistant, prompt_template: str = None):
        self._ai_assistant = ai_assistant
        self._prompt_template = prompt_template

    def generate(self, class_name, elements: [ElementData]) -> str:
        """ Generate a class representation based on the elements data. """
        elements_dict = [element.asdict_custom() for element in elements]
        prompt = self._prompt_template.format(class_name=class_name, elements_json=json.dumps(elements_dict))
        class_representation: ClassRepresentation = self._ai_assistant.ask(prompt, ClassRepresentation)
        return class_representation.implementation_as_str

import json
import re
import traceback
from typing import Type, Dict, Any
from pydantic import BaseModel, Field


class SchemaParser(object):
    """
    Pydantic Schema Parser Utility
    Used to generate JSON Schema-based prompts and parse LLM responses.
    """
    def __init__(self, model_class: Type[BaseModel]):

        self.type_mapping = {
            'string': "",
            'integer': 0,
            'number': 0.0,
            'boolean': False,
            'array': [],
            'object': {}
        }

        self.model_class = model_class
        self.schema = model_class.model_json_schema()
        self.schema_generation_prompt = self._generate_prompt()

        # self.parser = JsonOutputParser(pydantic_object=model_class)

        
    def _generate_prompt(self) -> str:
        """Generate a prompt template based on the JSON Schema."""
        return f"""
Please output the result strictly in the format defined by the given JSON schema, without any additional content:

JSON schema:
{json.dumps(self.schema, ensure_ascii=False)}

Output requirements:
1. Output a valid JSON object directly inside a markdown code block.
2. Do not include any explanatory text.
3. Ensure all fields have correct types and formats.

Example format:
```json
{json.dumps(self.get_example_output(), ensure_ascii=False)}
"""

    def get_example_output(self) -> Dict[str, Any]:
        """
        Generate an example output based on the JSON Schema.

        Returns:
            Dict[str, Any]: Example data matching the schema structure.
        """
        example_data = {}
        properties = self.schema.get('properties', {})

        for field_name, field_info in properties.items():
            example_data[field_name] = self._get_field_example_value(field_info)

        return example_data

    def _get_field_example_value(self, field_info: Dict[str, Any]) -> Any:
        """
        Generate an example value based on field metadata.

        Args:
            field_info: Dictionary containing field schema information.

        Returns:
            Any: A placeholder/example value matching the expected type.
        """
        field_type = field_info.get('type')
        return self.type_mapping.get(field_type, None)

    def parse_response_to_json(self, content: str) -> dict:
        """
        Parse an LLM response string into a dictionary according to the expected schema.

        Args:
            content: Raw response string from the LLM.

        Returns:
            dict: Parsed JSON data as a dictionary.
        """

        # Try multiple parsing strategies
        matching_strategies = [
            # Strategy 1: Extract JSON from markdown code block (with optional 'json' label)
            lambda c: re.search(r'```(?:json)?\s*(\{.*?\})\s*```', c, re.DOTALL).group(1),

            # Strategy 2: Extract JSON from generic markdown code block
            lambda c: re.search(r'```\s*(\{.*?\})\s*```', c, re.DOTALL).group(1),

            # Strategy 3: Parse the entire content as raw JSON
            lambda c: c
        ]

        parsed_data = {}
        last_error = None

        for strategy in matching_strategies:
            try:
                match_data = strategy(content)
                parsed_data = json.loads(match_data)
                # parsed_data = self.parser.invoke(match_data)
                # Ensure the parsed result is a dictionary
                if isinstance(parsed_data, dict):
                    break
            except Exception as e:
                last_error = e
                continue

        if last_error is not None:
            print(traceback.format_exception(last_error))

        return parsed_data

    def parse_response_to_base_model(self, content: str) -> BaseModel:
        """Parse LLM response into an instance of the target Pydantic model."""
        parsed_data = self.parse_response_to_json(content)
        try:
            model = self.model_class(**parsed_data)
        except Exception as e:
            # Fallback: instantiate with empty dict if parsing fails
            parsed_data = {}
            model = self.model_class(**parsed_data)
            print(traceback.format_exception(e))
        return model

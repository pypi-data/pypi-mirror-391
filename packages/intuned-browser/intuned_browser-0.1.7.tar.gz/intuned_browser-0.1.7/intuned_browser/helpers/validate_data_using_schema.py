from copy import deepcopy
from typing import Any
from typing import Dict
from typing import List

from jsonschema import validate
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError

from intuned_browser.helpers.types import Attachment
from intuned_browser.helpers.types import ValidationError


def _inject_attachment_type(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inject the attachment type definition into the schema.

    Converts any property with "type": "attachment" to use a $ref to the attachment definition.
    Also ensures the attachment definition exists in the schema's $defs.

    Args:
        schema: The JSON schema to modify

    Returns:
        Modified schema with attachment type support
    """
    # Deep copy to avoid modifying the original schema
    schema = deepcopy(schema)

    # Get the attachment schema from the Pydantic model
    attachment_json_schema = Attachment.model_json_schema()

    # Ensure $defs exist in the schema
    if "$defs" not in schema:
        schema["$defs"] = {}

    # If the attachment schema has $defs, we need to move them to the root level
    # and update references accordingly
    if "$defs" in attachment_json_schema:
        # Move $defs to root level $defs with a prefix to avoid conflicts
        for def_name, def_schema in attachment_json_schema["$defs"].items():
            schema["$defs"][f"Attachment_{def_name}"] = def_schema

        # Update references in the attachment schema from #/$defs/X to #/$defs/Attachment_X
        def update_refs(node: Any) -> Any:
            if isinstance(node, dict):
                if "$ref" in node and node["$ref"].startswith("#/$defs/"):
                    ref_name = node["$ref"].split("/")[-1]
                    return {"$ref": f"#/$defs/Attachment_{ref_name}"}
                return {key: update_refs(value) for key, value in node.items()}
            elif isinstance(node, list):
                return [update_refs(item) for item in node]
            return node

        attachment_definition = update_refs(attachment_json_schema)
        # Remove $defs from the attachment definition as they're now at root level
        if "$defs" in attachment_definition:
            del attachment_definition["$defs"]
    else:
        attachment_definition = attachment_json_schema

    # Set the attachment definition
    schema["$defs"]["attachment"] = attachment_definition

    # Recursively find and replace "type": "attachment" with $ref
    def replace_attachment_type(node: Any) -> Any:
        if isinstance(node, dict):
            # If this node has "type": "attachment", replace it with a $ref
            if node.get("type") == "attachment":
                return {"$ref": "#/$defs/attachment"}
            # Otherwise, recursively process all values
            return {key: replace_attachment_type(value) for key, value in node.items()}
        elif isinstance(node, list):
            return [replace_attachment_type(item) for item in node]
        return node

    schema = replace_attachment_type(schema)

    return schema


# Export _inject_attachment_type for testing
__all__ = ["validate_data_using_schema", "_inject_attachment_type"]


def validate_data_using_schema(data: Dict[str, Any] | List[Dict[str, Any]], schema: Dict[str, Any]):
    try:
        schema = _inject_attachment_type(schema)
        validate(instance=data, schema=schema)
    except JsonSchemaValidationError as e:
        raise ValidationError(f"Data validation failed: {e.message}", data)

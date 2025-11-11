"""Secure credential typing tools for automated login workflows."""

import platform
import subprocess
from typing import Any, Dict

import pyautogui
from pydantic import Field
from realtimex_toolkit import get_credential
from realtimex_toolkit.exceptions import CredentialError


def _type_text_safe(text: str, interval: float) -> None:
    """
    Type text using the most reliable method for each platform.

    - macOS: Uses AppleScript to avoid PyAutoGUI's shift key bug
    - Windows/Linux: Uses PyAutoGUI's typewrite with interval delays
    """
    system = platform.system()

    if system == "Darwin":
        # macOS: Use AppleScript to avoid PyAutoGUI shift bug
        # Escape special characters for AppleScript
        escaped_text = text.replace("\\", "\\\\").replace('"', '\\"')

        applescript = f'''
        tell application "System Events"
            keystroke "{escaped_text}"
        end tell
        '''

        subprocess.run(
            ["osascript", "-e", applescript], check=True, capture_output=True
        )
    else:
        # Windows/Linux: Use PyAutoGUI (no shift bug on these platforms)
        pyautogui.typewrite(text, interval=interval)


def type_credential_field(
    credential_id: str = Field(description="ID of the credential to use"),
    field_name: str = Field(
        description="Field name to type. Common fields: 'username', 'password' (basic_auth); 'name', 'value' (http_header, query_auth)"
    ),
) -> Dict[str, Any]:
    """Type a credential field value securely without exposing it in responses or logs."""
    try:
        # Retrieve credential using secure toolkit
        credential = get_credential(credential_id)

        # Extract payload containing field values
        payload = credential.get("payload")
        if not payload:
            return {"status": "error", "message": "Credential has no payload"}

        # Get the requested field value
        field_value = payload.get(field_name)
        if field_value is None:
            available_fields = list(payload.keys())
            return {
                "status": "error",
                "message": f"Field '{field_name}' not found in credential",
                "available_fields": available_fields,
            }

        # Use platform-specific typing method
        # macOS: AppleScript (avoids PyAutoGUI shift bug)
        # Windows/Linux: PyAutoGUI typewrite (no shift bug on these platforms)
        _type_text_safe(field_value, interval=0.05)

        # Return success without exposing the actual value
        return {
            "status": "success",
            "message": f"Typed credential field '{field_name}'",
            "credential_id": credential_id,
            "credential_name": credential.get("name"),
            "field": field_name,
        }

    except CredentialError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to type credential field: {type(e).__name__}",
        }

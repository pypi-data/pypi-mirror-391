import os
import requests
import mimetypes
from typing import Optional, Dict, Any, Tuple
from langchain_core.messages import ToolMessage
from pathlib import Path
from fairo.settings import get_fairo_base_url, get_fairo_api_key, get_fairo_api_secret
from fairo.core.client.client import BaseClient


def setup_fairo_client(base_url: Optional[str] = None) -> BaseClient:
    """
    Setup Fairo BaseClient with authentication.

    Args:
        base_url: Optional base URL, defaults to get_fairo_base_url()

    Returns:
        Configured BaseClient instance
    """
    api_base_url = base_url or get_fairo_base_url()
    auth_token = os.environ.get("FAIRO_AUTH_TOKEN")
    api_key = get_fairo_api_key()
    api_secret = get_fairo_api_secret()

    # Initialize client following the same pattern as FairoVectorStore
    client = BaseClient(
        base_url=api_base_url.rstrip('/'),
        username=api_key,
        password=api_secret,
        fairo_auth_token=auth_token
    )

    return client


def get_file_mimetype(file_path: Path) -> str:
    """
    Get the MIME type for a file based on its extension.

    Args:
        file_path: Path to the file

    Returns:
        MIME type string
    """
    mime_type, _ = mimetypes.guess_type(str(file_path))
    return mime_type or 'application/octet-stream'


def upload_file_to_fairo(
    file_path: Path,
    deployment_id: Optional[str] = None,
    execution_id: Optional[str] = None,
    base_url: Optional[str] = None
) -> Optional[Tuple[str, str]]:
    """
    Upload a file to Fairo API using BaseClient authentication pattern.

    Args:
        file_path: Path to the file to upload
        deployment_id: Optional deployment ID for deployment_artifacts endpoint
        execution_id: Optional execution ID for deployment_artifacts endpoint
        base_url: Optional base URL, defaults to get_fairo_base_url()

    Returns:
        Tuple of (file_id, file_url) if upload successful, None otherwise
    """
    if not file_path.exists():
        return None

    try:
        # Setup client for authentication
        api_base_url = base_url or get_fairo_base_url()
        auth_token = os.environ.get("FAIRO_AUTH_TOKEN")
        api_key = get_fairo_api_key()
        api_secret = get_fairo_api_secret()

        # Setup session with authentication (same pattern as BaseClient)
        session = requests.Session()
        if auth_token:
            session.headers.update({"Authorization": f"Bearer {auth_token}"})
        elif api_key and api_secret:
            session.auth = requests.auth.HTTPBasicAuth(api_key, api_secret)
        else:
            raise ValueError("Must provide either FAIRO_AUTH_TOKEN or API credentials")

        # Determine endpoint and data based on available IDs
        if deployment_id and execution_id:
            endpoint = f"{api_base_url.rstrip('/')}/deployment_artifacts"
            upload_data = {
                'deployment': deployment_id,
                'execution_id': execution_id
            }
        else:
            endpoint = f"{api_base_url.rstrip('/')}/files"
            upload_data = {}

        # Get file info
        filename = file_path.name
        mime_type = get_file_mimetype(file_path)

        # Upload file
        with open(file_path, 'rb') as file:
            files = {'file_object': (filename, file, mime_type)}
            response = session.post(
                endpoint,
                data=upload_data,
                files=files
            )
            response.raise_for_status()

            # Get the uploaded file information from response
            upload_result = response.json()
            file_id = upload_result.get("id") or upload_result.get("file_id")
            file_url = upload_result.get("file_relative_url")

            if file_id and file_url:
                return file_id, f"{api_base_url.rstrip('/')}{file_url}"
            else:
                return None

    except requests.exceptions.RequestException as e:
        print(f"Failed to upload file {file_path}: {e}")
        return None


def process_artifact_file(
    artifact_id: str,
    file_extension: str = "html",
    deployment_id: Optional[str] = None,
    execution_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Process an artifact file by uploading it to Fairo API or returning file data.

    Args:
        artifact_id: ID of the artifact
        file_extension: File extension (defaults to 'html')
        deployment_id: Optional deployment ID
        execution_id: Optional execution ID

    Returns:
        Message content dict or None if processing fails
    """
    # Setup file path
    base_dir = Path("/tmp") if Path("/tmp").exists() else Path.cwd()
    artifact_path = base_dir / f"{artifact_id}.{file_extension}"

    if not artifact_path.exists():
        return None

    try:
        # Try to upload file
        upload_result = upload_file_to_fairo(
            artifact_path,
            deployment_id=deployment_id,
            execution_id=execution_id
        )

        if upload_result:
            file_id, file_url = upload_result
            # Get mime type before cleaning up
            mime_type = get_file_mimetype(artifact_path)

            # Clean up local file after successful upload
            artifact_path.unlink()

            return {
                "type": "file",
                "mimeType": mime_type,
                "url": file_url,
                "id": file_id
            }
        else:
            # Fallback to returning file data
            mime_type = get_file_mimetype(artifact_path)
            file_data = artifact_path.read_text(encoding="utf-8") if mime_type.startswith("text/") else artifact_path.read_bytes()

            # Clean up local file
            artifact_path.unlink()

            return {
                "type": "file",
                "mimeType": mime_type,
                "data": file_data
            }

    except Exception as e:
        print(f"Error processing artifact {artifact_id}: {e}")

        # Clean up local file in case of error
        if artifact_path.exists():
            artifact_path.unlink()

        return None


def parse_chat_interface_output(agent_executor_result):
    """
        Parses agent executor result into chat interface response
        return_intermediate_steps must be set as true on the AgentExecutor in order to properly parse plot and suggestions
    """
    messages = [{"role": "assistant", "content": [
                {
                    "type": "text",
                    "text": agent_executor_result["output"]
                }
            ]}]
    suggestions = []
    intermediate_steps = agent_executor_result.get('intermediate_steps', [])
    for step, output  in intermediate_steps:
        if step.tool == "send_chat_suggestions":
            suggestions = output
        
        # Check if some tool message has artifact and raw_html attribute
        artifact = None
        is_tool_msg = isinstance(output, ToolMessage)
        if is_tool_msg:
            artifact = getattr(output, "artifact", None)
            if artifact is None:
                artifact = getattr(output, "additional_kwargs", {}).get("artifact")
            if artifact:
                artifact_id = artifact.get("artifact_id")
                artifact_type = artifact.get("artifact_type", "html")  # Default to html for backward compatibility

                if artifact_id:
                    # Get environment variables
                    deployment_id = os.environ.get("DEPLOYMENT_ID")
                    execution_id = os.environ.get("EXECUTION_ID")

                    # Process artifact using the new modular function
                    content = process_artifact_file(
                        artifact_id=artifact_id,
                        file_extension=artifact_type,
                        deployment_id=deployment_id,
                        execution_id=execution_id
                    )

                    if content:
                        # Create message with file ID in data field
                        if "id" in content:
                            messages.append({
                                "role": "assistant",
                                "content": [{
                                    "type": "file",
                                    "data": content["id"],
                                    "mimeType": content["mimeType"]
                                }]
                            })
                        else:
                            # Fallback to original content structure
                            messages.append({
                                "role": "assistant",
                                "content": [content]
                            })
    return {
        "messages": messages,
        "suggestions": suggestions
    }
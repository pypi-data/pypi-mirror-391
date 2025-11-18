import os

import requests
import logging
from heaptree.enums import Language, NodeSize
from heaptree.exceptions import (
    HeaptreeException,
    InternalServerErrorException,
    MissingCredentialsException,
    raise_for_status,
    raise_for_auth_error,
)
from heaptree.response_wrappers import (
    CreateNodeResponse,
    DownloadResponse,
    ExecutionResponseWrapper,
    ReadFilesResponse,
    UploadResponse,
    WriteFilesResponse,
)

logger = logging.getLogger(__name__)


class Heaptree:
    def __init__(self, api_key: str | None = None, *, base_url: str | None = None):
        """Create a new Heaptree SDK client.

        Args:
            api_key: Your platform **X-Api-Key**.
            base_url: Override the base URL of the Heaptree API (useful for local
                testing). Defaults to the hosted production endpoint.
        """

        self.api_key: str | None = api_key
        self.token: str | None = None
        self.base_url: str = base_url or "https://api.heaptree.com"

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------


    def call_api(self, endpoint: str, data: dict):
        url = f"{self.base_url}{endpoint}"

        # ----- Auth headers -----
        headers: dict[str, str] = {"Content-Type": "application/json"}

        if self.api_key:
            headers["X-Api-Key"] = self.api_key
        else:
            raise MissingCredentialsException(
                "No api key supplied. Please set api_key"
            )

        response = requests.post(url, json=data, headers=headers)
        
        try:
            response_json = response.json()
        except ValueError as e:
            # Response is not JSON (should not happen in normal operation)
            raise HeaptreeException(
                f"Invalid JSON response for {endpoint}: {response.text}"
            ) from e
        
        # Handle HTTP error status codes
        if response.status_code == 401:
            raise_for_auth_error(response_json, "Authentication")
        elif response.status_code >= 400:
            # Generic HTTP error
            detail = response_json.get("detail", f"HTTP {response.status_code} error")
            raise HeaptreeException(f"HTTP {response.status_code}: {detail}", response_json)
            
        return response_json

    # ------------------------------------------------------------------
    # Node management
    # ------------------------------------------------------------------

    def create_node(
        self,
        num_nodes: int = 1,
        node_size: NodeSize = NodeSize.SMALL,
        lifetime_seconds: int = 330,  # 5 minutes
    ) -> CreateNodeResponse:
        """
        Create one or more nodes.

        Returns CreateNodeResponse with convenient access:
        - result.node_id (for single node)
        - result.node_ids (for multiple nodes)
        - result.status (operation status)
        - result.execution_time_seconds (time taken to create)
            
        Raises:
            UsageLimitsExceededException: When usage limits are exceeded
            InvalidRequestParametersException: When request parameters are invalid
            InternalServerErrorException: When an internal server error occurs
        """
        data = {
            "num_nodes": num_nodes,
            "node_size": node_size.value,
            "lifetime_seconds": lifetime_seconds,
        }
        raw_response = self.call_api("/create-node", data)
        
        # Use the clean mapping system to raise appropriate exceptions
        raise_for_status(raw_response, "Node creation")
        print(raw_response.get("details"))    
        return CreateNodeResponse(raw_response)

    def terminate(self, node_id: str) -> None:
        """
        Terminate a node by terminating it and removing associated resources.
        
        Args:
            node_id: The ID of the node to terminate
            
        Raises:
            NodeNotFoundException: When the specified node is not found
            AccessDeniedException: When access to the node is denied
            InvalidNodeStateException: When the node is in an invalid state
            InternalServerErrorException: When an internal server error occurs
        """
        data = {
            "node_id": node_id,
        }
        raw_response = self.call_api("/cleanup-node", data)
        
        # Use the clean mapping system to raise appropriate exceptions
        raise_for_status(raw_response, "Node termination")
        logger.info(f"Node termination status: {raw_response.get('status')}")

    def terminate_nodes(self, node_ids: list[str]) -> None:
        """
        Terminate multiple nodes at once.
        
        Args:
            node_ids: List of node IDs to terminate
            
        Raises:
            InternalServerErrorException: When an internal server error occurs
        """
        data = {"node_ids": node_ids}
        raw_response = self.call_api("/terminate-nodes", data)
        
        # Use the clean mapping system to raise appropriate exceptions
        raise_for_status(raw_response, "Bulk node termination")
        logger.info(f"Bulk node termination status: {raw_response.get('status')}")

    # ------------------------------------------------------------------
    # Remote command execution
    # ------------------------------------------------------------------

    def run_command(self, node_id: str, command: str) -> ExecutionResponseWrapper:
        """Execute a command on the remote node.
        
        Args:
            node_id: Target node.
            command: Command to execute.
            
        Returns:
            ExecutionResponseWrapper with convenient access to output, error, exit_code, etc.
        """
        data = {"node_id": node_id, "command": command}
        raw_response = self.call_api("/run-command", data)
        return ExecutionResponseWrapper(raw_response)

    def run_code(self, node_id: str, lang: "Language", code: str) -> ExecutionResponseWrapper:
        """Execute **code** on the remote *node*.

        Args:
            node_id: Target node.
            lang: :pyclass:`~heaptree.enums.Language` specifying the language
                runtime to use.
            code: Source code to execute.
            
        Returns:
            ExecutionResponseWrapper with convenient access to output, error, exit_code, etc.
        """
        data = {"node_id": node_id, "lang": lang.value, "code": code}
        raw_response = self.call_api("/run-code", data)
        return ExecutionResponseWrapper(raw_response)

    # ------------------------------------------------------------------
    # File management
    # ------------------------------------------------------------------

    def upload(self, node_id: str, file_path: str, destination_path: str = "/home/ubuntu/Desktop/MY_FILES/") -> UploadResponse:
        """
        Upload a file to a node and transfer it to the node's filesystem.

        Args:
            node_id: The ID of the node to upload to
            file_path: Local path of the file to upload
            destination_path: Optional path on the node where file should be placed
                            (defaults to /home/ubuntu/Desktop/MY_FILES/)

        Returns:
            UploadResponse(status, file_path, destination_path)
            
        Raises:
            FileNotFoundError: When the local file is not found
            InvalidRequestParametersException: When request parameters are invalid
            InstanceNotReadyException: When the instance is not ready for file transfer
            InvalidDestinationPathException: When the destination path is invalid
            TransferFailedException: When the file transfer fails
            InternalServerErrorException: When an internal server error occurs
        """

        # Validate file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Extract filename from path
        filename = os.path.basename(file_path)

        # Step 1: Get presigned upload URL
        upload_url_data = {"node_id": node_id, "filename": filename}
        upload_response = self.call_api("/get-upload-url", upload_url_data)
        
        # Use the clean mapping system to raise appropriate exceptions
        raise_for_status(upload_response, "Upload URL generation")

        # Step 2: Upload file to S3 using presigned URL
        upload_url = upload_response["upload_url"]
        fields = upload_response["fields"]

        try:
            with open(file_path, "rb") as file:
                # Prepare multipart form data
                files = {"file": (filename, file, "application/octet-stream")}

                # Upload to S3
                s3_response = requests.post(upload_url, data=fields, files=files)
                s3_response.raise_for_status()

        except requests.exceptions.RequestException as e:
            raise InternalServerErrorException(f"Failed to upload file: {str(e)}")

        # Step 3: Transfer file from S3 to node filesystem
        transfer_data = {"node_id": node_id}
        if destination_path:
            transfer_data["destination_path"] = destination_path

        transfer_response = self.call_api("/transfer-files", transfer_data)
        
        # Use the clean mapping system to raise appropriate exceptions
        raise_for_status(transfer_response, "File transfer")
        
        logger.info("File uploaded successfully to %s", transfer_response.get("destination_path", "node"))

        return UploadResponse(
            status="SUCCESS",
            file_path=file_path,
            destination_path=transfer_response.get("destination_path", ""),
            node_id=node_id
        )

    def download(self, node_id: str, remote_path: str, local_path: str) -> DownloadResponse:
        """Download a file from a node to your local filesystem.
        
        Args:
            node_id: The ID of the node to download from
            remote_path: Path to the file on the remote node
            local_path: Local path where the file should be saved
            
        Returns:
            DownloadResponse(status, remote_path, local_path)
            
        Raises:
            NodeNotFoundException: When the specified node is not found
            FileNotFoundException: When the remote file is not found
            InternalServerErrorException: When an internal server error occurs
        """
        data = {
            "node_id": node_id,
            "file_path": remote_path,  # API still expects 'file_path'
        }
        response_json = self.call_api("/download-files", data)
        raise_for_status(response_json, "File download")

        s3_url = response_json.get("download_url")

        if not s3_url:
            raise InternalServerErrorException("No download URL found in API response")

        try:
            download_response = requests.get(s3_url)
            download_response.raise_for_status()

            with open(local_path, "wb") as f:
                f.write(download_response.content)

            logger.info("File downloaded successfully to %s", local_path)
            return DownloadResponse(status="SUCCESS", remote_path=remote_path, local_path=local_path)

        except requests.exceptions.RequestException as e:
            raise InternalServerErrorException(f"Failed to download file: {e}")

    def write_files(self, node_id: str, file_path: str, content: str) -> WriteFilesResponse:
        """Write content to a file on a remote node.
        
        Args:
            node_id: The ID of the node to write to
            file_path: Path on the node where content should be written
            content: The content to write to the file
            
        Returns:
            WriteFilesResponse(status, message, file_path, node_id)
            
        Raises:
            NodeNotFoundException: When the specified node is not found
            InvalidRequestParametersException: When request parameters are invalid
            InternalServerErrorException: When an internal server error occurs
        """
        data = {"node_id": node_id, "file_path": file_path, "content": content}
        response_json = self.call_api("/write-files", data)
        raise_for_status(response_json, "File write")
        
        return WriteFilesResponse(
            status=response_json.get("status", "SUCCESS"),
            message=response_json.get("message", ""),
            file_path=file_path,
            node_id=node_id
        )

    def read_files(self, node_id: str, file_path: str) -> ReadFilesResponse:
        """Read the contents of a file from a remote node.
        
        Args:
            node_id: The ID of the node to read from
            file_path: Path to the file on the remote node
            
        Returns:
            ReadFilesResponse(status, message, file_content, file_path, node_id)
            
        Raises:
            NodeNotFoundException: When the specified node is not found
            FileNotFoundException: When the specified file is not found
            InvalidRequestParametersException: When request parameters are invalid
            InternalServerErrorException: When an internal server error occurs
        """
        data = {"node_id": node_id, "file_path": file_path}
        response_json = self.call_api("/read-files", data)
        raise_for_status(response_json, "File read")
        
        return ReadFilesResponse(
            status=response_json.get("status", "SUCCESS"),
            message=response_json.get("message", ""),
            file_content=response_json.get("file_content", ""),
            file_path=file_path,
            node_id=node_id
        )

    # ------------------------------------------------------------------
    # Firecracker microVM sandbox operations
    # ------------------------------------------------------------------

    def create_firecracker_node(
        self,
        lifetime_seconds: int = 300,
        memory_mb: int = 128,
        vcpu_count: int = 1,
    ) -> "FirecrackerNode":
        """
        Create a new Firecracker microVM sandbox (node) with sub-second startup time.
        
        Args:
            lifetime_seconds: How long the node should remain active (default: 300 seconds / 5 minutes)
            memory_mb: Memory allocation in MB (default: 128)
            vcpu_count: Number of virtual CPUs (default: 1)
            
        Returns:
            FirecrackerNode object with convenient methods for code execution
            
        Raises:
            InternalServerErrorException: When node creation fails
        """
        data = {
            "lifetime_seconds": lifetime_seconds,
            "memory_mb": memory_mb,
            "vcpu_count": vcpu_count,
        }
        response_json = self.call_api("/create-firecracker-node", data)
        raise_for_status(response_json, "Firecracker node creation")
        
        node_id = response_json.get("node_id")
        logger.info(f"Created Firecracker node {node_id} in {response_json.get('execution_time_seconds', 0):.3f}s")
        
        return FirecrackerNode(self, node_id)

    def run_firecracker_code(
        self,
        node_id: str,
        code: str,
        timeout_seconds: int = 30,
    ) -> ExecutionResponseWrapper:
        """
        Execute Python code in a Firecracker microVM sandbox.
        
        Args:
            node_id: The ID of the Firecracker node
            code: Python code to execute
            timeout_seconds: Maximum execution time (default: 30 seconds)
            
        Returns:
            ExecutionResponseWrapper with output, error, and exit code
            
        Raises:
            NodeNotFoundException: When the specified node is not found
            AccessDeniedException: When access to the node is denied
            InternalServerErrorException: When execution fails
        """
        data = {
            "node_id": node_id,
            "code": code,
            "timeout_seconds": timeout_seconds,
        }
        response_json = self.call_api("/run-firecracker-code", data)
        raise_for_status(response_json, "Firecracker code execution")
        
        return ExecutionResponseWrapper(response_json)

    def cleanup_firecracker_node(self, node_id: str) -> None:
        """
        Cleanup and destroy a Firecracker microVM node.
        
        Args:
            node_id: The ID of the Firecracker node to cleanup
            
        Raises:
            NodeNotFoundException: When the specified node is not found
            AccessDeniedException: When access to the node is denied
            InternalServerErrorException: When cleanup fails
        """
        data = {"node_id": node_id}
        response_json = self.call_api("/cleanup-firecracker-node", data)
        raise_for_status(response_json, "Firecracker node cleanup")
        logger.info(f"Cleaned up Firecracker node {node_id}")


class FirecrackerNode:
    """
    A Firecracker microVM sandbox node for isolated code execution.
    
    This class provides a convenient interface for working with Firecracker sandboxes.
    Nodes automatically terminate after their lifetime expires.
    
    Example:
        >>> from heaptree import Heaptree
        >>> client = Heaptree(api_key="your-api-key")
        >>> 
        >>> # Create a node (alive for 5 minutes by default)
        >>> node = client.create_firecracker_node()
        >>> 
        >>> # Execute Python code
        >>> result = node.run_code("print('Hello from sandbox!')")
        >>> print(result.output)
        >>> 
        >>> # Cleanup when done (optional - auto-cleans after lifetime)
        >>> node.cleanup()
    """
    
    def __init__(self, client: Heaptree, node_id: str):
        """Initialize a FirecrackerNode instance.
        
        Args:
            client: The Heaptree client instance
            node_id: The unique identifier for this node
        """
        self._client = client
        self._node_id = node_id
        self._cleaned_up = False
    
    @property
    def node_id(self) -> str:
        """Get the node ID."""
        return self._node_id
    
    @property
    def id(self) -> str:
        """Get the node ID (alias for node_id)."""
        return self._node_id
    
    def run_code(self, code: str, timeout_seconds: int = 30) -> ExecutionResponseWrapper:
        """
        Execute Python code in this sandbox.
        
        Args:
            code: Python code to execute
            timeout_seconds: Maximum execution time (default: 30 seconds)
            
        Returns:
            ExecutionResponseWrapper with convenient access to:
            - result.output: Standard output from the code
            - result.error: Error message if execution failed
            - result.exit_code: Exit code (0 for success)
            - result.logs: Combined output for convenience
            
        Raises:
            InternalServerErrorException: When execution fails
            
        Example:
            >>> result = node.run_code("print('Hello World')")
            >>> print(result.logs)
            Hello World
        """
        if self._cleaned_up:
            raise InternalServerErrorException("Cannot run code on a cleaned up node")
        
        return self._client.run_firecracker_code(
            self._node_id,
            code,
            timeout_seconds
        )
    
    def cleanup(self) -> None:
        """
        Manually cleanup and destroy this node.
        
        Note: Nodes automatically cleanup after their lifetime expires,
        so calling this method is optional. Use it when you're done with
        the node early to save resources.
        
        Raises:
            InternalServerErrorException: When cleanup fails
        """
        if self._cleaned_up:
            logger.warning(f"Node {self._node_id} already cleaned up")
            return
        
        self._client.cleanup_firecracker_node(self._node_id)
        self._cleaned_up = True
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatically cleanup."""
        if not self._cleaned_up:
            try:
                self.cleanup()
            except Exception as e:
                logger.warning(f"Failed to cleanup node {self._node_id} on exit: {e}")
        return False
    
    def __repr__(self) -> str:
        status = "cleaned_up" if self._cleaned_up else "active"
        return f"FirecrackerNode(id='{self._node_id}', status='{status}')"
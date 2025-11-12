"""Cyberdesk Python SDK Client."""
from typing import Optional, Dict, Any, Union, List, TypeVar, Generic
from uuid import UUID
from pathlib import Path
import httpx
from dataclasses import dataclass
from datetime import datetime, timezone

# Import the generated client
from openapi_client.cyberdesk_cloud_client import AuthenticatedClient
from openapi_client.cyberdesk_cloud_client.types import UNSET, Unset
from openapi_client.cyberdesk_cloud_client.api.machines import (
    list_machines_v1_machines_get,
    create_machine_v1_machines_post,
    get_machine_v1_machines_machine_id_get,
    update_machine_v1_machines_machine_id_patch,
    delete_machine_v1_machines_machine_id_delete,
    get_machine_pools_v1_machines_machine_id_pools_get,
    update_machine_pools_v1_machines_machine_id_pools_put,
)
from openapi_client.cyberdesk_cloud_client.api.pools import (
    list_pools_v1_pools_get,
    create_pool_v1_pools_post,
    get_pool_v1_pools_pool_id_get,
    update_pool_v1_pools_pool_id_patch,
    delete_pool_v1_pools_pool_id_delete,
    add_machines_to_pool_v1_pools_pool_id_machines_post,
    remove_machines_from_pool_v1_pools_pool_id_machines_delete,
)
from openapi_client.cyberdesk_cloud_client.api.workflows import (
    list_workflows_v1_workflows_get,
    create_workflow_v1_workflows_post,
    get_workflow_v1_workflows_workflow_id_get,
    update_workflow_v1_workflows_workflow_id_patch,
    delete_workflow_v1_workflows_workflow_id_delete,
)
from openapi_client.cyberdesk_cloud_client.api.runs import (
    list_runs_v1_runs_get,
    create_run_v1_runs_post,
    get_run_v1_runs_run_id_get,
    update_run_v1_runs_run_id_patch,
    delete_run_v1_runs_run_id_delete,
    bulk_create_runs_v1_runs_bulk_post,
    create_run_chain_v1_runs_chain_post,
    retry_run_v1_runs_run_id_retry_post,
)
from openapi_client.cyberdesk_cloud_client.api.connections import (
    list_connections_v1_connections_get,
    create_connection_v1_connections_post,
)
from openapi_client.cyberdesk_cloud_client.api.trajectories import (
    list_trajectories_v1_trajectories_get,
    create_trajectory_v1_trajectories_post,
    get_trajectory_v1_trajectories_trajectory_id_get,
    update_trajectory_v1_trajectories_trajectory_id_patch,
    delete_trajectory_v1_trajectories_trajectory_id_delete,
    get_latest_trajectory_for_workflow_v1_workflows_workflow_id_latest_trajectory_get,
)
from openapi_client.cyberdesk_cloud_client.api.run_attachments import (
    list_run_attachments_v1_run_attachments_get,
    create_run_attachment_v1_run_attachments_post,
    get_run_attachment_v1_run_attachments_attachment_id_get,
    download_run_attachment_v1_run_attachments_attachment_id_download_get,
    get_run_attachment_download_url_v1_run_attachments_attachment_id_download_url_get,
    update_run_attachment_v1_run_attachments_attachment_id_put,
    delete_run_attachment_v1_run_attachments_attachment_id_delete,
)

# Import models
from openapi_client.cyberdesk_cloud_client.models import (
    MachineCreate,
    MachineUpdate,
    MachineResponse,
    MachineStatus,
    MachinePoolUpdate,
    PoolCreate,
    PoolUpdate,
    PoolResponse,
    PoolWithMachines,
    MachinePoolAssignment,
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowResponse,
    RunCreate,
    RunUpdate,
    RunResponse,
    RunStatus,
    RunBulkCreate,
    RunBulkCreateResponse,
    WorkflowChainCreate,
    WorkflowChainResponse,
    FileInput,
    ConnectionCreate,
    ConnectionResponse,
    ConnectionStatus,
    TrajectoryCreate,
    TrajectoryUpdate,
    TrajectoryResponse,
    RunAttachmentCreate,
    RunAttachmentUpdate,
    RunAttachmentResponse,
    RunAttachmentDownloadUrlResponse,
    AttachmentType,
    PaginatedResponseMachineResponse,
    PaginatedResponsePoolResponse,
    PaginatedResponseWorkflowResponse,
    PaginatedResponseRunResponse,
    PaginatedResponseConnectionResponse,
    PaginatedResponseTrajectoryResponse,
    PaginatedResponseRunAttachmentResponse,
    RunRetry,
    RunField,
)

# Re-export common types
__all__ = [
    "CyberdeskClient",
    "MachineCreate",
    "MachineUpdate",
    "MachineResponse",
    "MachineStatus",
    "MachinePoolUpdate",
    "PoolCreate",
    "PoolUpdate",
    "PoolResponse",
    "PoolWithMachines",
    "MachinePoolAssignment",
    "WorkflowCreate",
    "WorkflowUpdate",
    "WorkflowResponse",
    "RunCreate",
    "RunUpdate",
    "RunResponse",
    "RunStatus",
    "RunBulkCreate",
    "RunBulkCreateResponse",
    "WorkflowChainCreate",
    "WorkflowChainResponse",
    "FileInput",
    "ConnectionCreate",
    "ConnectionResponse",
    "ConnectionStatus",
    "TrajectoryCreate",
    "TrajectoryUpdate",
    "TrajectoryResponse",
    "RunAttachmentCreate",
    "RunAttachmentUpdate",
    "RunAttachmentResponse",
    "RunAttachmentDownloadUrlResponse",
    "AttachmentType",
    "RunRetry",
    "RunField",
]

DEFAULT_API_BASE_URL = "https://api.cyberdesk.io"


T = TypeVar('T')

@dataclass
class ApiResponse(Generic[T]):
    """Wrapper for API responses."""
    data: Optional[T] = None
    error: Optional[Any] = None


def _to_uuid(value: Union[str, UUID]) -> UUID:
    """Convert string to UUID if needed."""
    if isinstance(value, str):
        return UUID(value)
    return value


def _to_unset_or_value(value: Optional[Any]) -> Union[Unset, Any]:
    """Convert None to UNSET."""
    return UNSET if value is None else value


def _to_iso_utc_str(value: Optional[Union[str, datetime]]) -> Optional[str]:
    """Convert a datetime or string to an ISO8601 UTC string.

    - If value is a string, it is returned unchanged (assumed to be ISO8601)
    - If value is a timezone-aware datetime, it is converted to UTC ISO string
    - If value is a naive datetime, it is treated as UTC and suffixed accordingly
    - If value is None, returns None
    """
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc).isoformat()
        return value.astimezone(timezone.utc).isoformat()
    return None



class MachinesAPI:
    """Machines API endpoints."""
    
    def __init__(self, client: AuthenticatedClient):
        self.client = client
    
    async def list(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        status: Optional[MachineStatus] = None,
        *,
        created_at_from: Optional[Union[str, datetime]] = None,
        created_at_to: Optional[Union[str, datetime]] = None,
    ) -> ApiResponse[PaginatedResponseMachineResponse]:
        """List machines with optional filtering.

        Args:
            skip: Pagination skip
            limit: Pagination limit
            status: Machine status filter
            created_at_from: Optional start datetime (UTC or ISO string)
            created_at_to: Optional end datetime (UTC or ISO string)
        
        Returns:
            ApiResponse with PaginatedResponseMachineResponse. Each machine includes
            desktop parameters (machine_parameters, machine_sensitive_parameters) if configured.
        """
        try:
            response = await list_machines_v1_machines_get.asyncio(
                client=self.client,
                skip=_to_unset_or_value(skip),
                limit=_to_unset_or_value(limit),
                status=status,
                created_at_from=_to_unset_or_value(_to_iso_utc_str(created_at_from)),
                created_at_to=_to_unset_or_value(_to_iso_utc_str(created_at_to)),
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def list_sync(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        status: Optional[MachineStatus] = None,
        *,
        created_at_from: Optional[Union[str, datetime]] = None,
        created_at_to: Optional[Union[str, datetime]] = None,
    ) -> ApiResponse[PaginatedResponseMachineResponse]:
        """List machines with optional filtering (synchronous).
        
        Args:
            skip: Pagination skip
            limit: Pagination limit
            status: Machine status filter
            created_at_from: Optional start datetime (UTC or ISO string)
            created_at_to: Optional end datetime (UTC or ISO string)
        
        Returns:
            ApiResponse with PaginatedResponseMachineResponse. Each machine includes
            desktop parameters (machine_parameters, machine_sensitive_parameters) if configured.
        """
        try:
            response = list_machines_v1_machines_get.sync(
                client=self.client,
                skip=_to_unset_or_value(skip),
                limit=_to_unset_or_value(limit),
                status=status,
                created_at_from=_to_unset_or_value(_to_iso_utc_str(created_at_from)),
                created_at_to=_to_unset_or_value(_to_iso_utc_str(created_at_to)),
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def create(self, data: MachineCreate) -> ApiResponse[MachineResponse]:
        """Create a new machine.
        
        Args:
            data: MachineCreate object with:
                - fingerprint: Unique machine fingerprint
                - unkey_key_id: API key ID for authentication
                - name: Optional machine name
                - machine_parameters: Optional dict of desktop parameters
                - machine_sensitive_parameters: Optional dict of sensitive desktop parameters
                  (provide actual values, they'll be stored in Basis Theory)
                - hostname, os_info, version: Optional machine metadata
        """
        try:
            response = await create_machine_v1_machines_post.asyncio(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def create_sync(self, data: MachineCreate) -> ApiResponse[MachineResponse]:
        """Create a new machine (synchronous).
        
        Args:
            data: MachineCreate object with:
                - fingerprint: Unique machine fingerprint
                - unkey_key_id: API key ID for authentication
                - name: Optional machine name
                - machine_parameters: Optional dict of desktop parameters
                - machine_sensitive_parameters: Optional dict of sensitive desktop parameters
                  (provide actual values, they'll be stored in Basis Theory)
                - hostname, os_info, version: Optional machine metadata
        """
        try:
            response = create_machine_v1_machines_post.sync(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def get(self, machine_id: str) -> ApiResponse[MachineResponse]:
        """Get a specific machine by ID.
        
        Returns:
            ApiResponse with MachineResponse including:
                - Basic info: id, name, status, fingerprint, etc.
                - machine_parameters: Dict of desktop parameters (if configured)
                - machine_sensitive_parameters: Dict of sensitive parameter aliases (if configured)
                - pools: List of pools this machine belongs to
        """
        try:
            response = await get_machine_v1_machines_machine_id_get.asyncio(
                client=self.client,
                machine_id=_to_uuid(machine_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def get_sync(self, machine_id: str) -> ApiResponse[MachineResponse]:
        """Get a specific machine by ID (synchronous).
        
        Returns:
            ApiResponse with MachineResponse including:
                - Basic info: id, name, status, fingerprint, etc.
                - machine_parameters: Dict of desktop parameters (if configured)
                - machine_sensitive_parameters: Dict of sensitive parameter aliases (if configured)
                - pools: List of pools this machine belongs to
        """
        try:
            response = get_machine_v1_machines_machine_id_get.sync(
                client=self.client,
                machine_id=_to_uuid(machine_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def update(self, machine_id: str, data: MachineUpdate) -> ApiResponse[MachineResponse]:
        """Update a machine.
        
        Args:
            machine_id: The machine ID to update
            data: MachineUpdate object with fields to update:
                - name: Optional machine name
                - machine_parameters: Optional dict of machine-specific input values that 
                  automatically populate runs on this desktop. Use {} to clear all.
                - machine_sensitive_parameters: Optional dict of sensitive parameters 
                  (provide actual values, they'll be stored in Basis Theory). Use {} to clear all.
                - status, is_available, hostname, os_info, version: Other machine fields
                - reserved_session_id: Set to null to clear reservation
        
        Desktop Parameters:
            Machine parameters automatically merge into runs assigned to this machine,
            overriding run-level input values. Use {param_name} or {$sensitive_param}
            syntax in workflow prompts.
        
        Note: 
            - linked_keepalive_machine_id is not writable; it is managed by
              Cyberdriver link events and will be set/cleared automatically by the platform.
            - For machine_sensitive_parameters, provide actual secret values. They will be
              stored securely in Basis Theory and only aliases stored in the database.
        """
        try:
            response = await update_machine_v1_machines_machine_id_patch.asyncio(
                client=self.client,
                machine_id=_to_uuid(machine_id),
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def update_sync(self, machine_id: str, data: MachineUpdate) -> ApiResponse[MachineResponse]:
        """Update a machine (synchronous).
        
        Args:
            machine_id: The machine ID to update
            data: MachineUpdate object with fields to update:
                - name: Optional machine name
                - machine_parameters: Optional dict of machine-specific input values that 
                  automatically populate runs on this desktop. Use {} to clear all.
                - machine_sensitive_parameters: Optional dict of sensitive parameters 
                  (provide actual values, they'll be stored in Basis Theory). Use {} to clear all.
                - status, is_available, hostname, os_info, version: Other machine fields
                - reserved_session_id: Set to null to clear reservation
        
        Desktop Parameters:
            Machine parameters automatically merge into runs assigned to this machine,
            overriding run-level input values. Use {param_name} or {$sensitive_param}
            syntax in workflow prompts.
        
        Note: 
            - linked_keepalive_machine_id is not writable; it is managed by
              Cyberdriver link events and will be set/cleared automatically by the platform.
            - For machine_sensitive_parameters, provide actual secret values. They will be
              stored securely in Basis Theory and only aliases stored in the database.
        """
        try:
            response = update_machine_v1_machines_machine_id_patch.sync(
                client=self.client,
                machine_id=_to_uuid(machine_id),
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def clear_session(self, machine_id: str) -> ApiResponse[MachineResponse]:
        """Clear the machine's reserved session (cancels queued/running session runs).

        This sends reserved_session_id=null per API contract.
        """
        try:
            update = MachineUpdate(reserved_session_id=None)
            response = await update_machine_v1_machines_machine_id_patch.asyncio(
                client=self.client,
                machine_id=_to_uuid(machine_id),
                body=update
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def clear_session_sync(self, machine_id: str) -> ApiResponse[MachineResponse]:
        """Clear the machine's reserved session (synchronous)."""
        try:
            update = MachineUpdate(reserved_session_id=None)
            response = update_machine_v1_machines_machine_id_patch.sync(
                client=self.client,
                machine_id=_to_uuid(machine_id),
                body=update
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def delete(self, machine_id: str) -> ApiResponse[MachineResponse]:
        """Delete a machine.
        
        Associated runs are preserved with machine_id set to NULL to maintain run history.
        Connections and request logs are cascade deleted.
        
        If the machine has desktop sensitive parameters, they will be automatically
        cleaned up from Basis Theory before deletion.
        """
        try:
            await delete_machine_v1_machines_machine_id_delete.asyncio(
                client=self.client,
                machine_id=_to_uuid(machine_id)
            )
            return ApiResponse(data={"success": True})
        except Exception as e:
            return ApiResponse(error=e)
    
    def delete_sync(self, machine_id: str) -> ApiResponse[MachineResponse]:
        """Delete a machine (synchronous).
        
        Associated runs are preserved with machine_id set to NULL to maintain run history.
        Connections and request logs are cascade deleted.
        
        If the machine has desktop sensitive parameters, they will be automatically
        cleaned up from Basis Theory before deletion.
        """
        try:
            delete_machine_v1_machines_machine_id_delete.sync(
                client=self.client,
                machine_id=_to_uuid(machine_id)
            )
            return ApiResponse(data={"success": True})
        except Exception as e:
            return ApiResponse(error=e)
    
    async def get_pools(self, machine_id: str) -> ApiResponse[List[PoolResponse]]:
        """Get all pools that a machine belongs to."""
        try:
            response = await get_machine_pools_v1_machines_machine_id_pools_get.asyncio(
                client=self.client,
                machine_id=_to_uuid(machine_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def get_pools_sync(self, machine_id: str) -> ApiResponse[List[PoolResponse]]:
        """Get all pools that a machine belongs to (synchronous)."""
        try:
            response = get_machine_pools_v1_machines_machine_id_pools_get.sync(
                client=self.client,
                machine_id=_to_uuid(machine_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def update_pools(self, machine_id: str, data: MachinePoolUpdate) -> ApiResponse[List[PoolResponse]]:
        """Update a machine's pool assignments.
        
        This replaces all existing pool assignments with the new ones.
        
        Args:
            machine_id: The machine ID
            data: MachinePoolUpdate with pool_ids list
        
        Returns:
            ApiResponse with updated MachineResponse
        """
        try:
            response = await update_machine_pools_v1_machines_machine_id_pools_put.asyncio(
                client=self.client,
                machine_id=_to_uuid(machine_id),
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def update_pools_sync(self, machine_id: str, data: MachinePoolUpdate) -> ApiResponse[List[PoolResponse]]:
        """Update a machine's pool assignments (synchronous).
        
        This replaces all existing pool assignments with the new ones.
        
        Args:
            machine_id: The machine ID
            data: MachinePoolUpdate with pool_ids list
        
        Returns:
            ApiResponse with updated MachineResponse
        """
        try:
            response = update_machine_pools_v1_machines_machine_id_pools_put.sync(
                client=self.client,
                machine_id=_to_uuid(machine_id),
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)


class PoolsAPI:
    """Pools API endpoints."""
    
    def __init__(self, client: AuthenticatedClient):
        self.client = client
    
    async def list(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None
    ) -> ApiResponse[PaginatedResponsePoolResponse]:
        """List pools for the organization."""
        try:
            response = await list_pools_v1_pools_get.asyncio(
                client=self.client,
                skip=_to_unset_or_value(skip),
                limit=_to_unset_or_value(limit)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def list_sync(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None
    ) -> ApiResponse[PaginatedResponsePoolResponse]:
        """List pools for the organization (synchronous)."""
        try:
            response = list_pools_v1_pools_get.sync(
                client=self.client,
                skip=_to_unset_or_value(skip),
                limit=_to_unset_or_value(limit)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def create(self, data: PoolCreate) -> ApiResponse[PoolResponse]:
        """Create a new pool."""
        try:
            response = await create_pool_v1_pools_post.asyncio(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def create_sync(self, data: PoolCreate) -> ApiResponse[PoolResponse]:
        """Create a new pool (synchronous)."""
        try:
            response = create_pool_v1_pools_post.sync(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def get(self, pool_id: str, include_machines: bool = False) -> ApiResponse[Union[PoolResponse, PoolWithMachines]]:
        """Get a specific pool by ID.
        
        Args:
            pool_id: The pool ID
            include_machines: Whether to include full machine details
        
        Returns:
            ApiResponse with PoolResponse or PoolWithMachines
        """
        try:
            response = await get_pool_v1_pools_pool_id_get.asyncio(
                client=self.client,
                pool_id=_to_uuid(pool_id),
                include_machines=include_machines
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def get_sync(self, pool_id: str, include_machines: bool = False) -> ApiResponse[Union[PoolResponse, PoolWithMachines]]:
        """Get a specific pool by ID (synchronous).
        
        Args:
            pool_id: The pool ID
            include_machines: Whether to include full machine details
        
        Returns:
            ApiResponse with PoolResponse or PoolWithMachines
        """
        try:
            response = get_pool_v1_pools_pool_id_get.sync(
                client=self.client,
                pool_id=_to_uuid(pool_id),
                include_machines=include_machines
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def update(self, pool_id: str, data: PoolUpdate) -> ApiResponse[PoolResponse]:
        """Update a pool's details."""
        try:
            response = await update_pool_v1_pools_pool_id_patch.asyncio(
                client=self.client,
                pool_id=_to_uuid(pool_id),
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def update_sync(self, pool_id: str, data: PoolUpdate) -> ApiResponse[PoolResponse]:
        """Update a pool's details (synchronous)."""
        try:
            response = update_pool_v1_pools_pool_id_patch.sync(
                client=self.client,
                pool_id=_to_uuid(pool_id),
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def delete(self, pool_id: str) -> ApiResponse[PoolResponse]:
        """Delete a pool. This will not delete the machines in the pool."""
        try:
            await delete_pool_v1_pools_pool_id_delete.asyncio(
                client=self.client,
                pool_id=_to_uuid(pool_id)
            )
            return ApiResponse(data={"success": True})
        except Exception as e:
            return ApiResponse(error=e)
    
    def delete_sync(self, pool_id: str) -> ApiResponse[PoolResponse]:
        """Delete a pool. This will not delete the machines in the pool (synchronous)."""
        try:
            delete_pool_v1_pools_pool_id_delete.sync(
                client=self.client,
                pool_id=_to_uuid(pool_id)
            )
            return ApiResponse(data={"success": True})
        except Exception as e:
            return ApiResponse(error=e)
    
    async def add_machines(self, pool_id: str, data: MachinePoolAssignment) -> ApiResponse[PoolWithMachines]:
        """Add machines to a pool.
        
        Args:
            pool_id: The pool ID
            data: MachinePoolAssignment with machine_ids list
        
        Returns:
            ApiResponse with PoolWithMachines
        """
        try:
            response = await add_machines_to_pool_v1_pools_pool_id_machines_post.asyncio(
                client=self.client,
                pool_id=_to_uuid(pool_id),
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def add_machines_sync(self, pool_id: str, data: MachinePoolAssignment) -> ApiResponse[PoolWithMachines]:
        """Add machines to a pool (synchronous).
        
        Args:
            pool_id: The pool ID
            data: MachinePoolAssignment with machine_ids list
        
        Returns:
            ApiResponse with PoolWithMachines
        """
        try:
            response = add_machines_to_pool_v1_pools_pool_id_machines_post.sync(
                client=self.client,
                pool_id=_to_uuid(pool_id),
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def remove_machines(self, pool_id: str, data: MachinePoolAssignment) -> ApiResponse[PoolWithMachines]:
        """Remove machines from a pool.
        
        Args:
            pool_id: The pool ID
            data: MachinePoolAssignment with machine_ids list
        
        Returns:
            ApiResponse with success status
        """
        try:
            await remove_machines_from_pool_v1_pools_pool_id_machines_delete.asyncio(
                client=self.client,
                pool_id=_to_uuid(pool_id),
                body=data
            )
            return ApiResponse(data={"success": True})
        except Exception as e:
            return ApiResponse(error=e)
    
    def remove_machines_sync(self, pool_id: str, data: MachinePoolAssignment) -> ApiResponse[PoolWithMachines]:
        """Remove machines from a pool (synchronous).
        
        Args:
            pool_id: The pool ID
            data: MachinePoolAssignment with machine_ids list
        
        Returns:
            ApiResponse with success status
        """
        try:
            remove_machines_from_pool_v1_pools_pool_id_machines_delete.sync(
                client=self.client,
                pool_id=_to_uuid(pool_id),
                body=data
            )
            return ApiResponse(data={"success": True})
        except Exception as e:
            return ApiResponse(error=e)


class WorkflowsAPI:
    """Workflows API endpoints."""
    
    def __init__(self, client: AuthenticatedClient):
        self.client = client
    
    async def list(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        *,
        created_at_from: Optional[Union[str, datetime]] = None,
        created_at_to: Optional[Union[str, datetime]] = None,
        updated_at_from: Optional[Union[str, datetime]] = None,
        updated_at_to: Optional[Union[str, datetime]] = None,
    ) -> ApiResponse[PaginatedResponseWorkflowResponse]:
        """List workflows with optional date-time filtering.

        Args:
            skip: Pagination skip
            limit: Pagination limit
            created_at_from: Start datetime for created_at filter (UTC or ISO)
            created_at_to: End datetime for created_at filter (UTC or ISO)
            updated_at_from: Start datetime for updated_at filter (UTC or ISO)
            updated_at_to: End datetime for updated_at filter (UTC or ISO)
        """
        try:
            response = await list_workflows_v1_workflows_get.asyncio(
                client=self.client,
                skip=_to_unset_or_value(skip),
                limit=_to_unset_or_value(limit),
                created_at_from=_to_unset_or_value(_to_iso_utc_str(created_at_from)),
                created_at_to=_to_unset_or_value(_to_iso_utc_str(created_at_to)),
                updated_at_from=_to_unset_or_value(_to_iso_utc_str(updated_at_from)),
                updated_at_to=_to_unset_or_value(_to_iso_utc_str(updated_at_to)),
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def list_sync(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        *,
        created_at_from: Optional[Union[str, datetime]] = None,
        created_at_to: Optional[Union[str, datetime]] = None,
        updated_at_from: Optional[Union[str, datetime]] = None,
        updated_at_to: Optional[Union[str, datetime]] = None,
    ) -> ApiResponse[PaginatedResponseWorkflowResponse]:
        """List workflows (synchronous) with optional date-time filtering."""
        try:
            response = list_workflows_v1_workflows_get.sync(
                client=self.client,
                skip=_to_unset_or_value(skip),
                limit=_to_unset_or_value(limit),
                created_at_from=_to_unset_or_value(_to_iso_utc_str(created_at_from)),
                created_at_to=_to_unset_or_value(_to_iso_utc_str(created_at_to)),
                updated_at_from=_to_unset_or_value(_to_iso_utc_str(updated_at_from)),
                updated_at_to=_to_unset_or_value(_to_iso_utc_str(updated_at_to)),
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def create(self, data: WorkflowCreate) -> ApiResponse[WorkflowResponse]:
        """Create a new workflow."""
        try:
            response = await create_workflow_v1_workflows_post.asyncio(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def create_sync(self, data: WorkflowCreate) -> ApiResponse[WorkflowResponse]:
        """Create a new workflow (synchronous)."""
        try:
            response = create_workflow_v1_workflows_post.sync(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def get(self, workflow_id: str) -> ApiResponse[WorkflowResponse]:
        """Get a specific workflow by ID."""
        try:
            response = await get_workflow_v1_workflows_workflow_id_get.asyncio(
                client=self.client,
                workflow_id=_to_uuid(workflow_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def get_sync(self, workflow_id: str) -> ApiResponse[WorkflowResponse]:
        """Get a specific workflow by ID (synchronous)."""
        try:
            response = get_workflow_v1_workflows_workflow_id_get.sync(
                client=self.client,
                workflow_id=_to_uuid(workflow_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def update(self, workflow_id: str, data: WorkflowUpdate) -> ApiResponse[WorkflowResponse]:
        """Update a workflow."""
        try:
            response = await update_workflow_v1_workflows_workflow_id_patch.asyncio(
                client=self.client,
                workflow_id=_to_uuid(workflow_id),
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def update_sync(self, workflow_id: str, data: WorkflowUpdate) -> ApiResponse[WorkflowResponse]:
        """Update a workflow (synchronous)."""
        try:
            response = update_workflow_v1_workflows_workflow_id_patch.sync(
                client=self.client,
                workflow_id=_to_uuid(workflow_id),
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def delete(self, workflow_id: str) -> ApiResponse[WorkflowResponse]:
        """Delete a workflow."""
        try:
            await delete_workflow_v1_workflows_workflow_id_delete.asyncio(
                client=self.client,
                workflow_id=_to_uuid(workflow_id)
            )
            return ApiResponse(data={"success": True})
        except Exception as e:
            return ApiResponse(error=e)
    
    def delete_sync(self, workflow_id: str) -> ApiResponse[WorkflowResponse]:
        """Delete a workflow (synchronous)."""
        try:
            delete_workflow_v1_workflows_workflow_id_delete.sync(
                client=self.client,
                workflow_id=_to_uuid(workflow_id)
            )
            return ApiResponse(data={"success": True})
        except Exception as e:
            return ApiResponse(error=e)


class RunsAPI:
    """Runs API endpoints."""
    
    def __init__(self, client: AuthenticatedClient):
        self.client = client
    
    async def list(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        status: Optional[RunStatus] = None,
        workflow_id: Optional[str] = None,
        machine_id: Optional[str] = None,
        session_id: Optional[str] = None,
        *,
        created_at_from: Optional[Union[str, datetime]] = None,
        created_at_to: Optional[Union[str, datetime]] = None,
        fields: Optional[List[RunField]] = None,
    ) -> ApiResponse[PaginatedResponseRunResponse]:
        """List runs with optional filtering.
        
        Runs are ordered by: RUNNING (by started_at DESC) first, then all others (by ended_at DESC).
        This surfaces active work and recent completions.

        Args:
            skip: Pagination skip
            limit: Pagination limit
            status: Run status filter
            workflow_id: Filter by workflow ID
            machine_id: Filter by machine ID
            session_id: Filter by session ID
            created_at_from: Optional start datetime (UTC or ISO string)
            created_at_to: Optional end datetime (UTC or ISO string)
            fields: Optional list of fields to include per run (projection). When set,
                the response includes only these plus base fields (id, workflow_id,
                machine_id, status, created_at). Available fields include: started_at,
                ended_at, error, output_data, input_values, and more.
        
        Returns:
            ApiResponse with RunResponse objects including timing fields:
                - created_at: When run was created
                - started_at: When run execution started (null for SCHEDULING runs)
                - ended_at: When run completed (null for RUNNING/SCHEDULING runs)
        """
        try:
            response = await list_runs_v1_runs_get.asyncio(
                client=self.client,
                skip=_to_unset_or_value(skip),
                limit=_to_unset_or_value(limit),
                status=status,
                workflow_id=_to_uuid(workflow_id) if workflow_id else UNSET,
                machine_id=_to_uuid(machine_id) if machine_id else UNSET,
                session_id=_to_uuid(session_id) if session_id else UNSET,
                created_at_from=_to_unset_or_value(_to_iso_utc_str(created_at_from)),
                created_at_to=_to_unset_or_value(_to_iso_utc_str(created_at_to)),
                fields=_to_unset_or_value(fields),
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def list_sync(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        status: Optional[RunStatus] = None,
        workflow_id: Optional[str] = None,
        machine_id: Optional[str] = None,
        session_id: Optional[str] = None,
        *,
        created_at_from: Optional[Union[str, datetime]] = None,
        created_at_to: Optional[Union[str, datetime]] = None,
        fields: Optional[List[RunField]] = None,
    ) -> ApiResponse[PaginatedResponseRunResponse]:
        """List runs with optional filtering (synchronous).

        See async variant for parameter docs. Supports `fields` projection.
        """
        try:
            response = list_runs_v1_runs_get.sync(
                client=self.client,
                skip=_to_unset_or_value(skip),
                limit=_to_unset_or_value(limit),
                status=status,
                workflow_id=_to_uuid(workflow_id) if workflow_id else UNSET,
                machine_id=_to_uuid(machine_id) if machine_id else UNSET,
                session_id=_to_uuid(session_id) if session_id else UNSET,
                created_at_from=_to_unset_or_value(_to_iso_utc_str(created_at_from)),
                created_at_to=_to_unset_or_value(_to_iso_utc_str(created_at_to)),
                fields=_to_unset_or_value(fields),
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)

    async def retry(self, run_id: str, retry: RunRetry) -> ApiResponse[RunResponse]:
        """Retry an existing run in-place (same run_id).

        Clears previous outputs/history/output attachments, optionally replaces inputs/files,
        and attempts immediate assignment unless the session is busy.
        """
        try:
            response = await retry_run_v1_runs_run_id_retry_post.asyncio(
                client=self.client,
                run_id=_to_uuid(run_id),
                body=retry,
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)

    def retry_sync(self, run_id: str, retry: RunRetry) -> ApiResponse[RunResponse]:
        """Retry an existing run in-place (synchronous)."""
        try:
            response = retry_run_v1_runs_run_id_retry_post.sync(
                client=self.client,
                run_id=_to_uuid(run_id),
                body=retry,
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def create(self, data: RunCreate) -> ApiResponse[RunResponse]:
        """Create a new run.
        
        Args:
            data: RunCreate object with:
                - workflow_id: The workflow to run
                - machine_id: Optional specific machine ID
                - pool_ids: Optional list of pool IDs (machine must be in ALL specified pools)
                - input_values: Optional input values for workflow variables
                - file_inputs: Optional files to upload to the machine
                - sensitive_input_values: Optional sensitive inputs (stored securely, not in DB)
                - session_id: Optional UUID to join an existing session
                - start_session: Optional bool to start a new machine session
                - session_alias: Optional alias to persist outputs for refs in this session
                - release_session_after: Optional bool to release the session when this run completes (success, error, or cancel)
        
        Returns:
            ApiResponse with RunResponse
        """
        try:
            response = await create_run_v1_runs_post.asyncio(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def create_sync(self, data: RunCreate) -> ApiResponse[RunResponse]:
        """Create a new run (synchronous).
        
        Args:
            data: RunCreate object with:
                - workflow_id: The workflow to run
                - machine_id: Optional specific machine ID
                - pool_ids: Optional list of pool IDs (machine must be in ALL specified pools)
                - input_values: Optional input values for workflow variables
                - file_inputs: Optional files to upload to the machine
                - sensitive_input_values: Optional sensitive inputs (stored securely, not in DB)
                - session_id: Optional UUID to join an existing session
                - start_session: Optional bool to start a new machine session
                - session_alias: Optional alias to persist outputs for refs in this session
                - release_session_after: Optional bool to release the session when this run completes (success, error, or cancel)
        
        Returns:
            ApiResponse with RunResponse
        """
        try:
            response = create_run_v1_runs_post.sync(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def get(self, run_id: str) -> ApiResponse[RunResponse]:
        """Get a specific run by ID.
        
        Returns:
            ApiResponse with RunResponse including timing information:
                - created_at: When run was created
                - started_at: When run execution started (null if not started)
                - ended_at: When run completed (null if not finished)
        """
        try:
            response = await get_run_v1_runs_run_id_get.asyncio(
                client=self.client,
                run_id=_to_uuid(run_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def get_sync(self, run_id: str) -> ApiResponse[RunResponse]:
        """Get a specific run by ID (synchronous).
        
        Returns:
            ApiResponse with RunResponse including timing information:
                - created_at: When run was created
                - started_at: When run execution started (null if not started)
                - ended_at: When run completed (null if not finished)
        """
        try:
            response = get_run_v1_runs_run_id_get.sync(
                client=self.client,
                run_id=_to_uuid(run_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def update(self, run_id: str, data: RunUpdate) -> ApiResponse[RunResponse]:
        """Update a run."""
        try:
            response = await update_run_v1_runs_run_id_patch.asyncio(
                client=self.client,
                run_id=_to_uuid(run_id),
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def update_sync(self, run_id: str, data: RunUpdate) -> ApiResponse[RunResponse]:
        """Update a run (synchronous)."""
        try:
            response = update_run_v1_runs_run_id_patch.sync(
                client=self.client,
                run_id=_to_uuid(run_id),
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def delete(self, run_id: str) -> ApiResponse[RunResponse]:
        """Delete a run."""
        try:
            await delete_run_v1_runs_run_id_delete.asyncio(
                client=self.client,
                run_id=_to_uuid(run_id)
            )
            return ApiResponse(data={"success": True})
        except Exception as e:
            return ApiResponse(error=e)
    
    def delete_sync(self, run_id: str) -> ApiResponse[RunResponse]:
        """Delete a run (synchronous)."""
        try:
            delete_run_v1_runs_run_id_delete.sync(
                client=self.client,
                run_id=_to_uuid(run_id)
            )
            return ApiResponse(data={"success": True})
        except Exception as e:
            return ApiResponse(error=e)
    
    async def bulk_create(self, data: RunBulkCreate) -> ApiResponse[RunBulkCreateResponse]:
        """Create multiple runs with the same configuration.
        
        This method efficiently creates multiple runs:
        - All runs are created in a single database transaction
        - Temporal workflows are started asynchronously 
        - Returns immediately with created run details
        
        Args:
            data: RunBulkCreate object containing:
                - workflow_id: The workflow to run
                - machine_id: Optional specific machine ID 
                - pool_ids: Optional list of pool IDs (machine must be in ALL specified pools)
                - input_values: Optional input values for workflow variables
                - file_inputs: Optional files to upload to the machine
                - sensitive_input_values: Optional sensitive inputs (stored securely, not in DB)
                - count: Number of runs to create (max 1000)
                - session_id: Optional UUID to join an existing session for all runs
                - start_session: Optional bool to start a new machine session for all runs
        
        Returns:
            ApiResponse with RunBulkCreateResponse containing:
                - created_runs: List of created RunResponse objects
                - failed_count: Number of runs that failed to create
                - errors: List of error messages for failed runs
        """
        try:
            response = await bulk_create_runs_v1_runs_bulk_post.asyncio(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def bulk_create_sync(self, data: RunBulkCreate) -> ApiResponse[RunBulkCreateResponse]:
        """Create multiple runs with the same configuration (synchronous).
        
        This method efficiently creates multiple runs:
        - All runs are created in a single database transaction
        - Temporal workflows are started asynchronously 
        - Returns immediately with created run details
        
        Args:
            data: RunBulkCreate object containing:
                - workflow_id: The workflow to run
                - machine_id: Optional specific machine ID 
                - pool_ids: Optional list of pool IDs (machine must be in ALL specified pools)
                - input_values: Optional input values for workflow variables
                - file_inputs: Optional files to upload to the machine
                - sensitive_input_values: Optional sensitive inputs (stored securely, not in DB)
                - count: Number of runs to create (max 1000)
                - session_id: Optional UUID to join an existing session for all runs
                - start_session: Optional bool to start a new machine session for all runs
        
        Returns:
            ApiResponse with RunBulkCreateResponse containing:
                - created_runs: List of created RunResponse objects
                - failed_count: Number of runs that failed to create
                - errors: List of error messages for failed runs
        """
        try:
            response = bulk_create_runs_v1_runs_bulk_post.sync(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)

    async def chain(self, data: WorkflowChainCreate) -> ApiResponse[WorkflowChainResponse]:
        """Create a multi-step chain that runs on a single reserved session/machine.

        Args:
            data: WorkflowChainCreate with steps (session_alias, inputs, sensitive_inputs),
                  optional shared_inputs/sensitive/file_inputs, and optional
                  session_id or machine_id/pool_ids for session start.

        Returns:
            ApiResponse with WorkflowChainResponse
        """
        try:
            response = await create_run_chain_v1_runs_chain_post.asyncio(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)

    def chain_sync(self, data: WorkflowChainCreate) -> ApiResponse[WorkflowChainResponse]:
        """Create a multi-step chain (synchronous).

        Args:
            data: WorkflowChainCreate with steps (session_alias, inputs, sensitive_inputs),
                  optional shared_inputs/sensitive/file_inputs, and optional
                  session_id or machine_id/pool_ids for session start.

        Returns:
            ApiResponse with WorkflowChainResponse
        """
        try:
            response = create_run_chain_v1_runs_chain_post.sync(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)


class ConnectionsAPI:
    """Connections API endpoints."""
    
    def __init__(self, client: AuthenticatedClient):
        self.client = client
    
    async def list(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        machine_id: Optional[str] = None,
        status: Optional[Union[str, ConnectionStatus]] = None
    ) -> ApiResponse[PaginatedResponseConnectionResponse]:
        """List connections with optional filtering."""
        try:
            # Handle status conversion
            if isinstance(status, str):
                status = Unset if status is None else ConnectionStatus(status)
            
            response = await list_connections_v1_connections_get.asyncio(
                client=self.client,
                skip=_to_unset_or_value(skip),
                limit=_to_unset_or_value(limit),
                machine_id=_to_uuid(machine_id) if machine_id else UNSET,
                status=status
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def list_sync(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        machine_id: Optional[str] = None,
        status: Optional[Union[str, ConnectionStatus]] = None
    ) -> ApiResponse[PaginatedResponseConnectionResponse]:
        """List connections with optional filtering (synchronous)."""
        try:
            # Handle status conversion
            if isinstance(status, str):
                status = Unset if status is None else ConnectionStatus(status)
            
            response = list_connections_v1_connections_get.sync(
                client=self.client,
                skip=_to_unset_or_value(skip),
                limit=_to_unset_or_value(limit),
                machine_id=_to_uuid(machine_id) if machine_id else UNSET,
                status=status
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def create(self, data: ConnectionCreate) -> ApiResponse[ConnectionResponse]:
        """Create a new connection."""
        try:
            response = await create_connection_v1_connections_post.asyncio(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def create_sync(self, data: ConnectionCreate) -> ApiResponse[ConnectionResponse]:
        """Create a new connection (synchronous)."""
        try:
            response = create_connection_v1_connections_post.sync(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)


class TrajectoriesAPI:
    """Trajectories API endpoints."""
    
    def __init__(self, client: AuthenticatedClient):
        self.client = client
    
    async def list(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        workflow_id: Optional[str] = None,
        is_approved: Optional[bool] = None,
        *,
        created_at_from: Optional[Union[str, datetime]] = None,
        created_at_to: Optional[Union[str, datetime]] = None,
        updated_at_from: Optional[Union[str, datetime]] = None,
        updated_at_to: Optional[Union[str, datetime]] = None,
    ) -> ApiResponse[PaginatedResponseTrajectoryResponse]:
        """List trajectories with optional filtering.
        
        Args:
            skip: Number of records to skip
            limit: Number of records to return
            workflow_id: Filter by workflow ID
            is_approved: Filter by approval status (True=approved, False=not approved, None=all)
            created_at_from: Filter created at or after (UTC or ISO string)
            created_at_to: Filter created at or before (UTC or ISO string)
            updated_at_from: Filter updated at or after (UTC or ISO string)
            updated_at_to: Filter updated at or before (UTC or ISO string)
        
        Note: By default returns both approved and unapproved trajectories.
        Only approved trajectories are used during workflow execution.
        """
        try:
            response = await list_trajectories_v1_trajectories_get.asyncio(
                client=self.client,
                skip=_to_unset_or_value(skip),
                limit=_to_unset_or_value(limit),
                workflow_id=_to_uuid(workflow_id) if workflow_id else UNSET,
                is_approved=_to_unset_or_value(is_approved),
                created_at_from=_to_unset_or_value(_to_iso_utc_str(created_at_from)),
                created_at_to=_to_unset_or_value(_to_iso_utc_str(created_at_to)),
                updated_at_from=_to_unset_or_value(_to_iso_utc_str(updated_at_from)),
                updated_at_to=_to_unset_or_value(_to_iso_utc_str(updated_at_to)),
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def list_sync(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        workflow_id: Optional[str] = None,
        is_approved: Optional[bool] = None,
        *,
        created_at_from: Optional[Union[str, datetime]] = None,
        created_at_to: Optional[Union[str, datetime]] = None,
        updated_at_from: Optional[Union[str, datetime]] = None,
        updated_at_to: Optional[Union[str, datetime]] = None,
    ) -> ApiResponse[PaginatedResponseTrajectoryResponse]:
        """List trajectories with optional filtering (synchronous).
        
        Args:
            skip: Number of records to skip
            limit: Number of records to return
            workflow_id: Filter by workflow ID
            is_approved: Filter by approval status (True=approved, False=not approved, None=all)
            created_at_from: Filter created at or after (UTC or ISO string)
            created_at_to: Filter created at or before (UTC or ISO string)
            updated_at_from: Filter updated at or after (UTC or ISO string)
            updated_at_to: Filter updated at or before (UTC or ISO string)
        
        Note: By default returns both approved and unapproved trajectories.
        Only approved trajectories are used during workflow execution.
        """
        try:
            response = list_trajectories_v1_trajectories_get.sync(
                client=self.client,
                skip=_to_unset_or_value(skip),
                limit=_to_unset_or_value(limit),
                workflow_id=_to_uuid(workflow_id) if workflow_id else UNSET,
                is_approved=_to_unset_or_value(is_approved),
                created_at_from=_to_unset_or_value(_to_iso_utc_str(created_at_from)),
                created_at_to=_to_unset_or_value(_to_iso_utc_str(created_at_to)),
                updated_at_from=_to_unset_or_value(_to_iso_utc_str(updated_at_from)),
                updated_at_to=_to_unset_or_value(_to_iso_utc_str(updated_at_to)),
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def create(self, data: TrajectoryCreate) -> ApiResponse[TrajectoryResponse]:
        """Create a new trajectory.
        
        Note: Trajectories are created with is_approved=False by default.
        You must explicitly approve them before they can be used during workflow execution.
        """
        try:
            response = await create_trajectory_v1_trajectories_post.asyncio(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def create_sync(self, data: TrajectoryCreate) -> ApiResponse[TrajectoryResponse]:
        """Create a new trajectory (synchronous).
        
        Note: Trajectories are created with is_approved=False by default.
        You must explicitly approve them before they can be used during workflow execution.
        """
        try:
            response = create_trajectory_v1_trajectories_post.sync(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def get(self, trajectory_id: str) -> ApiResponse[TrajectoryResponse]:
        """Get a specific trajectory by ID."""
        try:
            response = await get_trajectory_v1_trajectories_trajectory_id_get.asyncio(
                client=self.client,
                trajectory_id=_to_uuid(trajectory_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def get_sync(self, trajectory_id: str) -> ApiResponse[TrajectoryResponse]:
        """Get a specific trajectory by ID (synchronous)."""
        try:
            response = get_trajectory_v1_trajectories_trajectory_id_get.sync(
                client=self.client,
                trajectory_id=_to_uuid(trajectory_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def update(self, trajectory_id: str, data: TrajectoryUpdate) -> ApiResponse[TrajectoryResponse]:
        """Update a trajectory.
        
        You can update trajectory metadata (name, description), trajectory data (steps),
        and approval status (is_approved). Only approved trajectories are used during
        workflow execution.
        """
        try:
            response = await update_trajectory_v1_trajectories_trajectory_id_patch.asyncio(
                client=self.client,
                trajectory_id=_to_uuid(trajectory_id),
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def update_sync(self, trajectory_id: str, data: TrajectoryUpdate) -> ApiResponse[TrajectoryResponse]:
        """Update a trajectory (synchronous).
        
        You can update trajectory metadata (name, description), trajectory data (steps),
        and approval status (is_approved). Only approved trajectories are used during
        workflow execution.
        """
        try:
            response = update_trajectory_v1_trajectories_trajectory_id_patch.sync(
                client=self.client,
                trajectory_id=_to_uuid(trajectory_id),
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def delete(self, trajectory_id: str) -> ApiResponse[TrajectoryResponse]:
        """Delete a trajectory."""
        try:
            await delete_trajectory_v1_trajectories_trajectory_id_delete.asyncio(
                client=self.client,
                trajectory_id=_to_uuid(trajectory_id)
            )
            return ApiResponse(data={"success": True})
        except Exception as e:
            return ApiResponse(error=e)
    
    def delete_sync(self, trajectory_id: str) -> ApiResponse[TrajectoryResponse]:
        """Delete a trajectory (synchronous)."""
        try:
            delete_trajectory_v1_trajectories_trajectory_id_delete.sync(
                client=self.client,
                trajectory_id=_to_uuid(trajectory_id)
            )
            return ApiResponse(data={"success": True})
        except Exception as e:
            return ApiResponse(error=e)
    
    async def get_latest_for_workflow(self, workflow_id: str) -> ApiResponse[TrajectoryResponse]:
        """Get the latest trajectory for a workflow."""
        try:
            response = await get_latest_trajectory_for_workflow_v1_workflows_workflow_id_latest_trajectory_get.asyncio(
                client=self.client,
                workflow_id=_to_uuid(workflow_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def get_latest_for_workflow_sync(self, workflow_id: str) -> ApiResponse[TrajectoryResponse]:
        """Get the latest trajectory for a workflow (synchronous)."""
        try:
            response = get_latest_trajectory_for_workflow_v1_workflows_workflow_id_latest_trajectory_get.sync(
                client=self.client,
                workflow_id=_to_uuid(workflow_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)


class RunAttachmentsAPI:
    """Run Attachments API endpoints."""
    
    def __init__(self, client: AuthenticatedClient):
        self.client = client
    
    async def list(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        run_id: Optional[str] = None,
        attachment_type: Optional[AttachmentType] = None
    ) -> ApiResponse[PaginatedResponseRunAttachmentResponse]:
        """List run attachments with optional filtering."""
        try:
            response = await list_run_attachments_v1_run_attachments_get.asyncio(
                client=self.client,
                skip=_to_unset_or_value(skip),
                limit=_to_unset_or_value(limit),
                run_id=_to_uuid(run_id) if run_id else UNSET,
                attachment_type=attachment_type
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def list_sync(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        run_id: Optional[str] = None,
        attachment_type: Optional[AttachmentType] = None
    ) -> ApiResponse[PaginatedResponseRunAttachmentResponse]:
        """List run attachments with optional filtering (synchronous)."""
        try:
            response = list_run_attachments_v1_run_attachments_get.sync(
                client=self.client,
                skip=_to_unset_or_value(skip),
                limit=_to_unset_or_value(limit),
                run_id=_to_uuid(run_id) if run_id else UNSET,
                attachment_type=attachment_type
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def create(self, data: RunAttachmentCreate) -> ApiResponse[RunAttachmentResponse]:
        """Create a new run attachment."""
        try:
            response = await create_run_attachment_v1_run_attachments_post.asyncio(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def create_sync(self, data: RunAttachmentCreate) -> ApiResponse[RunAttachmentResponse]:
        """Create a new run attachment (synchronous)."""
        try:
            response = create_run_attachment_v1_run_attachments_post.sync(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def get(self, attachment_id: str) -> ApiResponse[RunAttachmentResponse]:
        """Get a specific run attachment by ID."""
        try:
            response = await get_run_attachment_v1_run_attachments_attachment_id_get.asyncio(
                client=self.client,
                attachment_id=_to_uuid(attachment_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def get_sync(self, attachment_id: str) -> ApiResponse[RunAttachmentResponse]:
        """Get a specific run attachment by ID (synchronous)."""
        try:
            response = get_run_attachment_v1_run_attachments_attachment_id_get.sync(
                client=self.client,
                attachment_id=_to_uuid(attachment_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def get_download_url(
        self, 
        attachment_id: str,
        expires_in: Optional[int] = None
    ) -> ApiResponse[RunAttachmentDownloadUrlResponse]:
        """Get a signed download URL for a run attachment.
        
        The returned URL will trigger an automatic download when accessed in a browser.
        
        Args:
            attachment_id: The ID of the attachment
            expires_in: URL expiration time in seconds (10-3600). Default: 300 (5 minutes)
        
        Returns:
            ApiResponse with RunAttachmentDownloadUrlResponse containing:
                - url: The signed download URL
                - expires_in: The expiration time in seconds
        """
        try:
            response = await get_run_attachment_download_url_v1_run_attachments_attachment_id_download_url_get.asyncio(
                client=self.client,
                attachment_id=_to_uuid(attachment_id),
                expires_in=_to_unset_or_value(expires_in)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def get_download_url_sync(
        self, 
        attachment_id: str,
        expires_in: Optional[int] = None
    ) -> ApiResponse[RunAttachmentDownloadUrlResponse]:
        """Get a signed download URL for a run attachment (synchronous).
        
        The returned URL will trigger an automatic download when accessed in a browser.
        
        Args:
            attachment_id: The ID of the attachment
            expires_in: URL expiration time in seconds (10-3600). Default: 300 (5 minutes)
        
        Returns:
            ApiResponse with RunAttachmentDownloadUrlResponse containing:
                - url: The signed download URL
                - expires_in: The expiration time in seconds
        """
        try:
            response = get_run_attachment_download_url_v1_run_attachments_attachment_id_download_url_get.sync(
                client=self.client,
                attachment_id=_to_uuid(attachment_id),
                expires_in=_to_unset_or_value(expires_in)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def download(self, attachment_id: str) -> ApiResponse[bytes]:
        """Download a run attachment file directly.
        
        This method returns the raw file content as bytes. For a download URL instead,
        use get_download_url().
        
        Args:
            attachment_id: The ID of the attachment to download
        
        Returns:
            ApiResponse with data containing the raw file bytes
        """
        try:
            response = await download_run_attachment_v1_run_attachments_attachment_id_download_get.asyncio(
                client=self.client,
                attachment_id=_to_uuid(attachment_id)
            )
            # Extract bytes from File object returned by generator
            if response and hasattr(response, 'payload'):
                file_bytes = response.payload.read()
                return ApiResponse(data=file_bytes)
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def download_sync(self, attachment_id: str) -> ApiResponse[bytes]:
        """Download a run attachment file directly (synchronous).
        
        This method returns the raw file content as bytes. For a download URL instead,
        use get_download_url_sync().
        
        Args:
            attachment_id: The ID of the attachment to download
        
        Returns:
            ApiResponse with data containing the raw file bytes
        """
        try:
            response = download_run_attachment_v1_run_attachments_attachment_id_download_get.sync(
                client=self.client,
                attachment_id=_to_uuid(attachment_id)
            )
            # Extract bytes from File object returned by generator
            if response and hasattr(response, 'payload'):
                file_bytes = response.payload.read()
                return ApiResponse(data=file_bytes)
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def update(self, attachment_id: str, data: RunAttachmentUpdate) -> ApiResponse[RunAttachmentResponse]:
        """Update a run attachment (e.g., set expiration)."""
        try:
            response = await update_run_attachment_v1_run_attachments_attachment_id_put.asyncio(
                client=self.client,
                attachment_id=_to_uuid(attachment_id),
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def update_sync(self, attachment_id: str, data: RunAttachmentUpdate) -> ApiResponse[RunAttachmentResponse]:
        """Update a run attachment (e.g., set expiration) (synchronous)."""
        try:
            response = update_run_attachment_v1_run_attachments_attachment_id_put.sync(
                client=self.client,
                attachment_id=_to_uuid(attachment_id),
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def delete(self, attachment_id: str) -> ApiResponse[RunAttachmentResponse]:
        """Delete a run attachment."""
        try:
            await delete_run_attachment_v1_run_attachments_attachment_id_delete.asyncio(
                client=self.client,
                attachment_id=_to_uuid(attachment_id)
            )
            return ApiResponse(data={"success": True})
        except Exception as e:
            return ApiResponse(error=e)
    
    def delete_sync(self, attachment_id: str) -> ApiResponse[RunAttachmentResponse]:
        """Delete a run attachment (synchronous)."""
        try:
            delete_run_attachment_v1_run_attachments_attachment_id_delete.sync(
                client=self.client,
                attachment_id=_to_uuid(attachment_id)
            )
            return ApiResponse(data={"success": True})
        except Exception as e:
            return ApiResponse(error=e)
    
    async def save_to_file(
        self,
        attachment_id: str,
        output_path: Optional[Union[str, Path]] = None,
        use_original_filename: bool = True
    ) -> ApiResponse[Dict[str, Any]]:
        """Download and save a run attachment to a file.
        
        This is a convenience method that combines getting attachment info
        and downloading the file content.
        
        Args:
            attachment_id: The ID of the attachment to download
            output_path: Path where to save the file. If None and use_original_filename
                        is True, saves to current directory with original filename.
            use_original_filename: If True and output_path is a directory, uses the
                                 attachment's original filename.
        
        Returns:
            ApiResponse with data containing the saved file path
        """
        try:
            # Get attachment info for filename
            info_response = await self.get(attachment_id)
            if info_response.error:
                return info_response
            
            attachment_info = info_response.data
            
            # Download the file content
            download_response = await self.download(attachment_id)
            if download_response.error:
                return download_response
            
            # Determine output path
            if output_path is None:
                output_path = Path(attachment_info.filename)
            else:
                output_path = Path(output_path)
                if output_path.is_dir() and use_original_filename:
                    output_path = output_path / attachment_info.filename
            
            # Save to file
            output_path.write_bytes(download_response.data)
            
            return ApiResponse(data={"path": str(output_path), "size": len(download_response.data)})
        except Exception as e:
            return ApiResponse(error=e)
    
    def save_to_file_sync(
        self,
        attachment_id: str,
        output_path: Optional[Union[str, Path]] = None,
        use_original_filename: bool = True
    ) -> ApiResponse[Dict[str, Any]]:
        """Download and save a run attachment to a file (synchronous).
        
        This is a convenience method that combines getting attachment info
        and downloading the file content.
        
        Args:
            attachment_id: The ID of the attachment to download
            output_path: Path where to save the file. If None and use_original_filename
                        is True, saves to current directory with original filename.
            use_original_filename: If True and output_path is a directory, uses the
                                 attachment's original filename.
        
        Returns:
            ApiResponse with data containing the saved file path
        """
        try:
            # Get attachment info for filename
            info_response = self.get_sync(attachment_id)
            if info_response.error:
                return info_response
            
            attachment_info = info_response.data
            
            # Download the file content
            download_response = self.download_sync(attachment_id)
            if download_response.error:
                return download_response
            
            # Determine output path
            if output_path is None:
                output_path = Path(attachment_info.filename)
            else:
                output_path = Path(output_path)
                if output_path.is_dir() and use_original_filename:
                    output_path = output_path / attachment_info.filename
            
            # Save to file
            output_path.write_bytes(download_response.data)
            
            return ApiResponse(data={"path": str(output_path), "size": len(download_response.data)})
        except Exception as e:
            return ApiResponse(error=e)


class CyberdeskClient:
    """Main Cyberdesk SDK client."""
    
    def __init__(self, api_key: str, base_url: str = DEFAULT_API_BASE_URL):
        """Initialize the Cyberdesk client.
        
        Args:
            api_key: Your Cyberdesk API key
            base_url: API base URL (defaults to https://api.cyberdesk.io)
        """
        # Create the underlying client with authentication
        self._client = AuthenticatedClient(
            base_url=base_url,
            token=api_key,
            prefix="Bearer",
            auth_header_name="Authorization",
            raise_on_unexpected_status=True  # Raise exceptions for non-200/422 responses
        )
        
        # Initialize API endpoints
        self.machines = MachinesAPI(self._client)
        self.pools = PoolsAPI(self._client)
        self.workflows = WorkflowsAPI(self._client)
        self.runs = RunsAPI(self._client)
        self.connections = ConnectionsAPI(self._client)
        self.trajectories = TrajectoriesAPI(self._client)
        self.run_attachments = RunAttachmentsAPI(self._client)
        
        # TODO: Add computer API for screenshot functionality
        # The openapi-python-client doesn't generate code for binary responses like PNG images
        # To add screenshot support, implement a ComputerAPI class that:
        # - Makes raw HTTP GET request to /v1/computer/{machine_id}/display/screenshot
        # - Returns the PNG image bytes
        # Example: self.computer = ComputerAPI(self._client)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def close(self):
        """Close the client connection."""
        if hasattr(self._client, '__exit__'):
            self._client.__exit__(None, None, None) 
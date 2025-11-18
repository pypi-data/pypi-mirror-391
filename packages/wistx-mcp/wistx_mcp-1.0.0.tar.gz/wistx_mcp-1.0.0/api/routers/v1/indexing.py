"""Indexing endpoints for user-provided resources."""

import json
import logging
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status

from api.dependencies import get_current_user
from api.models.indexing import ResourceStatus, ResourceType
from api.models.indexing_requests import (
    IndexDocumentRequest,
    IndexDocumentationRequest,
    IndexRepositoryRequest,
)
from api.models.indexing_responses import (
    IndexResourceResponse,
    ResourceDetailResponse,
    ResourceListResponse,
)
from api.models.v1_responses import ErrorResponse
from api.services.indexing_service import indexing_service
from api.services.quota_service import QuotaExceededError, quota_service
from api.services.usage_tracker import usage_tracker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/indexing", tags=["indexing"])


@router.post(
    "/repositories",
    response_model=IndexResourceResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Index GitHub repository",
    description="Index a GitHub repository for user-specific search. Supports both public and private repositories.",
)
async def index_repository(
    request: IndexRepositoryRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> IndexResourceResponse:
    """Index a GitHub repository.

    Args:
        request: Index repository request
        current_user: Current authenticated user

    Returns:
        Index resource response with resource_id and status

    Raises:
        HTTPException: If quota exceeded or validation fails
    """
    user_id = current_user.get("user_id")
    plan = current_user.get("plan", "free")
    organization_id = current_user.get("organization_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found",
        )

    try:
        await quota_service.check_indexing_quota(
            user_id=user_id,
            plan=plan,
            estimated_storage_mb=0.0,
        )
    except QuotaExceededError as e:
        logger.warning("Indexing quota exceeded for user %s: %s", user_id, e)
        error_response = ErrorResponse(
            error={
                "code": "QUOTA_EXCEEDED",
                "message": str(e),
                "details": {
                    "limit_type": e.limit_type,
                    "current": e.current,
                    "limit": e.limit,
                },
            },
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=error_response.model_dump(),
        ) from e

    try:
        from api.services.github_service import github_service

        repo_url_str = str(request.repo_url)

        has_access = await github_service.validate_repository_access(
            repo_url=repo_url_str,
            github_token=request.github_token,
        )

        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Repository access denied. Check repository URL and GitHub token.",
            )

        name = request.name or repo_url_str.split("/")[-1].replace(".git", "")

        resource = await indexing_service.create_resource(
            user_id=user_id,
            organization_id=organization_id,
            resource_type=ResourceType.REPOSITORY,
            name=name,
            description=request.description,
            tags=request.tags,
            repo_url=repo_url_str,
            branch=request.branch,
            github_token=request.github_token,
        )

        await indexing_service.start_indexing_job(
            resource_id=resource.resource_id,
            user_id=user_id,
            plan=plan,
        )

        await usage_tracker.track_indexing_operation(
            user_id=user_id,
            api_key_id=current_user.get("api_key_id", ""),
            index_type="repository",
            resource_id=resource.resource_id,
            documents_count=0,
            storage_mb=0.0,
            organization_id=organization_id,
            plan=plan,
        )

        return IndexResourceResponse(
            resource_id=resource.resource_id,
            status=resource.status,
            progress=resource.progress,
            message="Repository indexing started",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error indexing repository: %s", e, exc_info=True)
        error_response = ErrorResponse(
            error={
                "code": "INDEXING_ERROR",
                "message": "Failed to start repository indexing",
                "details": str(e) if logger.isEnabledFor(logging.DEBUG) else None,
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.model_dump(),
        ) from e


@router.post(
    "/documentation",
    response_model=IndexResourceResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Index documentation website",
    description="Index a documentation website for user-specific search.",
)
async def index_documentation(
    request: IndexDocumentationRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> IndexResourceResponse:
    """Index a documentation website.

    Args:
        request: Index documentation request
        current_user: Current authenticated user

    Returns:
        Index resource response with resource_id and status

    Raises:
        HTTPException: If quota exceeded or validation fails
    """
    user_id = current_user.get("user_id")
    plan = current_user.get("plan", "free")
    organization_id = current_user.get("organization_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found",
        )

    try:
        await quota_service.check_indexing_quota(
            user_id=user_id,
            plan=plan,
            estimated_storage_mb=0.0,
        )
    except QuotaExceededError as e:
        logger.warning("Indexing quota exceeded for user %s: %s", user_id, e)
        error_response = ErrorResponse(
            error={
                "code": "QUOTA_EXCEEDED",
                "message": str(e),
                "details": {
                    "limit_type": e.limit_type,
                    "current": e.current,
                    "limit": e.limit,
                },
            },
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=error_response.model_dump(),
        ) from e

    try:
        doc_url_str = str(request.documentation_url)
        name = request.name or doc_url_str

        resource = await indexing_service.create_resource(
            user_id=user_id,
            organization_id=organization_id,
            resource_type=ResourceType.DOCUMENTATION,
            name=name,
            description=request.description,
            tags=request.tags,
            documentation_url=doc_url_str,
            include_patterns=request.include_patterns,
            exclude_patterns=request.exclude_patterns,
        )

        await indexing_service.start_indexing_job(
            resource_id=resource.resource_id,
            user_id=user_id,
            plan=plan,
        )

        await usage_tracker.track_indexing_operation(
            user_id=user_id,
            api_key_id=current_user.get("api_key_id", ""),
            index_type="documentation",
            resource_id=resource.resource_id,
            documents_count=0,
            storage_mb=0.0,
            organization_id=organization_id,
            plan=plan,
        )

        return IndexResourceResponse(
            resource_id=resource.resource_id,
            status=resource.status,
            progress=resource.progress,
            message="Documentation indexing started",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error indexing documentation: %s", e, exc_info=True)
        error_response = ErrorResponse(
            error={
                "code": "INDEXING_ERROR",
                "message": "Failed to start documentation indexing",
                "details": str(e) if logger.isEnabledFor(logging.DEBUG) else None,
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.model_dump(),
        ) from e


@router.post(
    "/documents",
    response_model=IndexResourceResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Index document",
    description="Upload and index a document (PDF, DOCX, Markdown, etc.) for user-specific search. "
                "Supports both file upload (multipart/form-data) and URL download (multipart/form-data).",
)
async def index_document(
    file: Optional[UploadFile] = File(default=None, description="Uploaded file (PDF, DOCX, Markdown, TXT)"),
    document_url: Optional[str] = Form(default=None, description="Document URL (http/https) or local file path"),
    document_type: Optional[str] = Form(default=None, description="Document type (auto-detected if not provided)"),
    name: Optional[str] = Form(default=None, description="Custom name for the resource"),
    description: Optional[str] = Form(default=None, description="Resource description"),
    tags: Optional[str] = Form(default=None, description="JSON array string of tags"),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> IndexResourceResponse:
    """Index a document.

    Supports two modes:
    1. File upload (multipart/form-data): Provide 'file' parameter
    2. URL download (multipart/form-data): Provide 'document_url' parameter

    Args:
        file: Uploaded file (optional)
        document_url: Document URL or local path (optional)
        document_type: Document type (auto-detected if not provided)
        name: Custom name for the resource
        description: Resource description
        tags: JSON array string of tags
        current_user: Current authenticated user

    Returns:
        Index resource response with resource_id and status

    Raises:
        HTTPException: If validation fails, quota exceeded, or processing fails
    """
    user_id = current_user.get("user_id")
    plan = current_user.get("plan", "free")
    organization_id = current_user.get("organization_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found",
        )

    if not file and not document_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'file' or 'document_url' must be provided",
        )

    if file and document_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot provide both 'file' and 'document_url'. Choose one.",
        )

    tag_list = []
    if tags:
        try:
            tag_list = json.loads(tags) if isinstance(tags, str) else tags
            if not isinstance(tag_list, list):
                tag_list = []
        except Exception:
            tag_list = []

    tmp_file_path: Optional[Path] = None
    detected_document_type: Optional[str] = None
    file_name: Optional[str] = None

    try:
        from api.utils.file_handler import file_handler

        if file:
            tmp_file_path, detected_document_type = await file_handler.save_uploaded_file(
                file=file,
                plan=plan,
            )
            file_name = file.filename or "uploaded_file"

        elif document_url:
            if document_url.startswith(("http://", "https://")):
                tmp_file_path, detected_document_type = await file_handler.download_file_from_url(
                    url=document_url,
                    plan=plan,
                )
                file_name = Path(document_url).name or "downloaded_file"
            else:
                tmp_file_path = Path(document_url)
                
                try:
                    validated_path = file_handler.validate_file_path(tmp_file_path)
                    tmp_file_path = validated_path
                except ValueError as e:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid file path: {str(e)}",
                    ) from e
                
                if not tmp_file_path.exists():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"File not found: {document_url}",
                    )
                
                if not file_handler.is_temporary_file(tmp_file_path):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="File must be in temporary directory",
                    )
                
                file_name = tmp_file_path.name
                detected_document_type = document_type or file_handler.validate_file_type(
                    file_name,
                    None,
                )

        final_document_type = document_type or detected_document_type

        if not final_document_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not determine document type. Please provide 'document_type' parameter.",
            )

        valid_document_types = {"pdf", "docx", "markdown", "md", "txt"}
        if final_document_type.lower() not in valid_document_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid document type: {final_document_type}. "
                       f"Supported types: {', '.join(valid_document_types)}",
            )

        file_size_mb = 0.0
        if tmp_file_path and tmp_file_path.exists():
            file_size_mb = tmp_file_path.stat().st_size / (1024 * 1024)

        try:
            await quota_service.check_indexing_quota(
                user_id=user_id,
                plan=plan,
                estimated_storage_mb=file_size_mb,
            )
        except QuotaExceededError as e:
            if tmp_file_path and tmp_file_path.exists():
                if document_url and document_url.startswith(("http://", "https://")) or file:
                    file_handler.cleanup_file(tmp_file_path)

            logger.warning("Indexing quota exceeded for user %s: %s", user_id, e)
            error_response = ErrorResponse(
                error={
                    "code": "QUOTA_EXCEEDED",
                    "message": str(e),
                    "details": {
                        "limit_type": e.limit_type,
                        "current": e.current,
                        "limit": e.limit,
                    },
                },
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=error_response.model_dump(),
            ) from e

        document_path_str = str(tmp_file_path) if tmp_file_path else document_url

        resource = await indexing_service.create_resource(
            user_id=user_id,
            organization_id=organization_id,
            resource_type=ResourceType.DOCUMENT,
            name=name or file_name or "Document",
            description=description,
            tags=tag_list,
            document_url=document_path_str,
            document_type=final_document_type.lower(),
        )

        await indexing_service.start_indexing_job(
            resource_id=resource.resource_id,
            user_id=user_id,
            plan=plan,
        )

        await usage_tracker.track_indexing_operation(
            user_id=user_id,
            api_key_id=current_user.get("api_key_id", ""),
            index_type="document",
            resource_id=resource.resource_id,
            documents_count=1,
            storage_mb=file_size_mb,
            organization_id=organization_id,
            plan=plan,
        )

        return IndexResourceResponse(
            resource_id=resource.resource_id,
            status=resource.status,
            progress=resource.progress,
            message="Document indexing started",
        )

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning("Validation error indexing document: %s", e)
        if tmp_file_path and tmp_file_path.exists():
            if document_url and document_url.startswith(("http://", "https://")) or file:
                file_handler.cleanup_file(tmp_file_path)
        error_response = ErrorResponse(
            error={
                "code": "VALIDATION_ERROR",
                "message": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response.model_dump(),
        ) from e
    except Exception as e:
        logger.error("Error indexing document: %s", e, exc_info=True)

        if tmp_file_path and tmp_file_path.exists():
            if document_url and document_url.startswith(("http://", "https://")) or file:
                from api.utils.file_handler import file_handler
                file_handler.cleanup_file(tmp_file_path)

        error_response = ErrorResponse(
            error={
                "code": "INDEXING_ERROR",
                "message": "Failed to start document indexing",
                "details": str(e) if logger.isEnabledFor(logging.DEBUG) else None,
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.model_dump(),
        ) from e


@router.get(
    "/resources",
    response_model=ResourceListResponse,
    summary="List indexed resources",
    description="List all indexed resources for the current user.",
)
async def list_resources(
    resource_type: ResourceType | None = Query(default=None, description="Filter by resource type"),
    status: ResourceStatus | None = Query(default=None, description="Filter by status"),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> ResourceListResponse:
    """List indexed resources for user.

    Args:
        resource_type: Filter by resource type
        status: Filter by status
        current_user: Current authenticated user

    Returns:
        Resource list response
    """
    user_id = current_user.get("user_id")
    organization_id = current_user.get("organization_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found",
        )

    try:
        resources = await indexing_service.list_resources(
            user_id=user_id,
            organization_id=organization_id,
            resource_type=resource_type,
            status=status,
        )

        resource_responses = [
            ResourceDetailResponse(
                resource_id=r.resource_id,
                user_id=r.user_id,
                organization_id=r.organization_id,
                resource_type=r.resource_type,
                status=r.status,
                progress=r.progress,
                name=r.name,
                description=r.description,
                tags=r.tags,
                repo_url=r.repo_url,
                branch=r.branch,
                documentation_url=r.documentation_url,
                document_url=r.document_url,
                articles_indexed=r.articles_indexed,
                files_processed=r.files_processed,
                total_files=r.total_files,
                storage_mb=r.storage_mb,
                error_message=r.error_message,
                error_details=r.error_details,
                created_at=r.created_at,
                updated_at=r.updated_at,
                indexed_at=r.indexed_at,
            )
            for r in resources
        ]

        return ResourceListResponse(resources=resource_responses, total=len(resource_responses))

    except Exception as e:
        logger.error("Error listing resources: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list resources",
        ) from e


@router.get(
    "/resources/{resource_id}",
    response_model=ResourceDetailResponse,
    summary="Get resource details",
    description="Get detailed information about a specific indexed resource.",
)
async def get_resource(
    resource_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> ResourceDetailResponse:
    """Get resource details.

    Args:
        resource_id: Resource ID
        current_user: Current authenticated user

    Returns:
        Resource detail response

    Raises:
        HTTPException: If resource not found or access denied
    """
    user_id = current_user.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found",
        )

    try:
        resource = await indexing_service.get_resource(resource_id, user_id)

        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found or access denied",
            )

        return ResourceDetailResponse(
            resource_id=resource.resource_id,
            user_id=resource.user_id,
            organization_id=resource.organization_id,
            resource_type=resource.resource_type,
            status=resource.status,
            progress=resource.progress,
            name=resource.name,
            description=resource.description,
            tags=resource.tags,
            repo_url=resource.repo_url,
            branch=resource.branch,
            documentation_url=resource.documentation_url,
            document_url=resource.document_url,
            articles_indexed=resource.articles_indexed,
            files_processed=resource.files_processed,
            total_files=resource.total_files,
            storage_mb=resource.storage_mb,
            error_message=resource.error_message,
            error_details=resource.error_details,
            created_at=resource.created_at,
            updated_at=resource.updated_at,
            indexed_at=resource.indexed_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting resource: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get resource",
        ) from e


@router.delete(
    "/resources/{resource_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete indexed resource",
    description="Delete an indexed resource and all associated knowledge articles.",
)
async def delete_resource(
    resource_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> None:
    """Delete indexed resource.

    Args:
        resource_id: Resource ID
        current_user: Current authenticated user

    Raises:
        HTTPException: If resource not found or access denied
    """
    user_id = current_user.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found",
        )

    try:
        success = await indexing_service.delete_resource(resource_id, user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found or access denied",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting resource: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete resource",
        ) from e


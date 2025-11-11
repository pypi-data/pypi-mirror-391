"""
MCP Tools for Odoo integration

This module contains all the MCP tool functions for interacting with Odoo.
"""

from typing import Any, cast

from biszx_odoo_mcp.exceptions import OdooMCPError, ToolError
from biszx_odoo_mcp.server.context import AppContext
from biszx_odoo_mcp.server.response import Response


async def search_models(mcp: Any, query: str) -> dict[str, Any]:
    """
    Get a list of all available models in the Odoo system.
    Args:
        query: Search term to find models (searches in model name and display name)
    Returns:
        JSON string with matching models
    """
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        data = app_context.odoo.search_models(query)
        return Response(data=data).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()
    except Exception as e:
        tool_error = ToolError(
            f"Unexpected error getting models: {str(e)}",
            tool_name="search_models",
            original_error=e,
        )
        return Response(error=tool_error.to_dict()).to_dict()


async def get_model_info(mcp: Any, model_name: str) -> dict[str, Any]:
    """
    Get information about a specific Odoo model.
    Args:
        model_name: Name of the model (e.g., 'res.partner')
    Returns:
        Dictionary with model information
    """
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        data = app_context.odoo.get_model_info(model_name)
        return Response(data=data).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()
    except Exception as e:
        tool_error = ToolError(
            f"Unexpected error getting model info: {str(e)}",
            tool_name="get_model_info",
            details={"model_name": model_name},
            original_error=e,
        )
        return Response(error=tool_error.to_dict()).to_dict()


async def get_model_fields(
    mcp: Any, model_name: str, query_field: str
) -> dict[str, Any]:
    """
    Get field definitions for a specific Odoo model.
    Args:
        model_name: Name of the model (e.g., 'res.partner')
        query_field: Search term to find fields (searches in field name and string)
    Returns:
        Dictionary with field definitions
    """
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        data = app_context.odoo.get_model_fields(model_name, query_field)
        return Response(data=data).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()
    except Exception as e:
        tool_error = ToolError(
            f"Unexpected error getting model fields: {str(e)}",
            tool_name="get_model_fields",
            details={"model_name": model_name},
            original_error=e,
        )
        return Response(error=tool_error.to_dict()).to_dict()


async def search_records(
    mcp: Any,
    model_name: str,
    domain: list[Any],
    fields: list[str] | None = None,
    limit: int | None = None,
    offset: int | None = None,
    order: str | None = None,
) -> dict[str, Any]:
    """
    Search for records in an Odoo model.
    Args:
        model_name: Name of the model e.g., 'res.partner'
        domain: Search domain as list of tuples e.g., [['is_company', '=', true]]
        fields: List of field names to return, None for all fields (default: null)
        limit: Maximum number of records to return (default: null)
        offset: Number of records to skip (default: null)
        order: Sorting criteria e.g., 'name ASC, id DESC' (default: null)
    Returns:
        Dictionary with search results
    """
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        data = app_context.odoo.search_read(
            model_name, domain, fields=fields, limit=limit, offset=offset, order=order
        )
        return Response(data=data).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()


async def search_count(
    mcp: Any,
    model_name: str,
    domain: list[Any],
) -> dict[str, Any]:
    """
    Count records that match a search domain.
    Args:
        model_name: Name of the model e.g., 'res.partner'
        domain: Search domain as list of tuples e.g., [['is_company', '=', True]]
    Returns:
        Dictionary with the count of matching records
    """
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        count = app_context.odoo.search_count(model_name, domain)
        return Response(data={"count": count}).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()


async def search_ids(
    mcp: Any,
    model_name: str,
    domain: list[Any],
    offset: int | None = None,
    limit: int | None = None,
    order: str | None = None,
) -> dict[str, Any]:
    """
    Search for record IDs that match a domain.
    Args:
        model_name: Name of the model e.g., 'res.partner'
        domain: Search domain as list of tuples e.g., [['is_company', '=', True]]
        offset: Number of records to skip (default: null)
        limit: Maximum number of records to return (default: null)
        order: Sorting criteria e.g., 'name ASC, id DESC' (default: null)
    Returns:
        Dictionary with list of matching record IDs
    """
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        ids = app_context.odoo.search_ids(
            model_name, domain, offset=offset, limit=limit, order=order
        )
        return Response(data={"ids": ids}).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()


async def read_records(
    mcp: Any,
    model_name: str,
    ids: list[int],
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """
    Read specific records by their IDs.
    Args:
        model_name: Name of the model e.g., 'res.partner'
        ids: List of record IDs to read
        fields: List of field names to return, None for all fields (default: null)
    Returns:
        Dictionary with record data
    """
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        data = app_context.odoo.read_records(model_name, ids, fields=fields)
        return Response(data=data).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()


async def create_records(
    mcp: Any,
    model_name: str,
    values_list: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Create multiple records in an Odoo model.
    Args:
        model_name: Name of the model e.g., 'res.partner'
        values_list: List of dictionaries with field values for the new records
    Returns:
        Dictionary with the created record IDs
    """
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        record_ids = app_context.odoo.create_records(model_name, values_list)
        return Response(data={"ids": record_ids}).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()


async def write_records(
    mcp: Any,
    model_name: str,
    record_ids: list[int],
    values: dict[str, Any],
) -> dict[str, Any]:
    """
    Update multiple records in an Odoo model.
    Args:
        model_name: Name of the model e.g., 'res.partner'
        record_ids: List of record IDs to update
        values: Dictionary with field values to update
    Returns:
        Dictionary with operation result
    """
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        result = app_context.odoo.write_records(model_name, record_ids, values)
        return Response(data={"success": result}).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()


async def search_and_write(
    mcp: Any,
    model_name: str,
    domain: list[Any],
    values: dict[str, Any],
) -> dict[str, Any]:
    """
    Search for records and update them in one operation.
    Args:
        model_name: Name of the model e.g., 'res.partner'
        domain: Search domain to find records to update
        values: Dictionary with field values to update
    Returns:
        Dictionary with operation results including affected record count
    """
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        # First search for IDs
        record_ids = app_context.odoo.search_ids(model_name, domain)
        if not record_ids:
            return Response(
                data={"affected_records": 0, "message": "No records found"}
            ).to_dict()

        # Then update the found records
        app_context.odoo.write_records(model_name, record_ids, values)
        return Response(
            data={
                "affected_records": len(record_ids),
                "record_ids": record_ids,
            }
        ).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()


async def unlink_records(
    mcp: Any,
    model_name: str,
    record_ids: list[int],
) -> dict[str, Any]:
    """
    Delete multiple records from an Odoo model.
    Args:
        model_name: Name of the model e.g., 'res.partner'
        record_ids: List of record IDs to delete
    Returns:
        Dictionary with operation result
    """
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        app_context.odoo.unlink_records(model_name, record_ids)
        return Response().to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()


async def search_and_unlink(
    mcp: Any,
    model_name: str,
    domain: list[Any],
) -> dict[str, Any]:
    """
    Search for records and delete them in one operation.
    Args:
        model_name: Name of the model e.g., 'res.partner'
        domain: Search domain to find records to delete
    Returns:
        Dictionary with operation results including affected record count
    """
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        # First search for IDs
        record_ids = app_context.odoo.search_ids(model_name, domain)
        if not record_ids:
            return Response(error={"error": "No records found"}).to_dict()

        # Then delete the found records
        app_context.odoo.unlink_records(model_name, record_ids)
        return Response(
            data={"affected_records": len(record_ids), "record_ids": record_ids}
        ).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()


async def call_method(
    mcp: Any,
    model_name: str,
    method_name: str,
    args: list[Any] | None = None,
    kwargs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Call a custom method on an Odoo model.
    Args:
        model_name: Name of the model e.g., 'res.partner'
        method_name: Name of the method to call
        args: Positional arguments to pass to the method (default: null)
        kwargs: Keyword arguments to pass to the method (default: null)
    Returns:
        Dictionary with method result
    """
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}

    try:
        result = app_context.odoo.call_method(model_name, method_name, args, kwargs)
        return Response(data=result).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()


async def read_group(
    mcp: Any,
    model_name: str,
    domain: list[Any],
    fields: list[str],
    groupby: list[str],
    offset: int | None = None,
    limit: int | None = None,
    order: str | None = None,
) -> dict[str, Any]:
    """
    Group records and perform aggregations on an Odoo model.
    Args:
        model_name: Name of the model e.g., 'res.partner'
        domain: Search domain as list of tuples e.g., [['is_company', '=', True]]
        fields: List of field names to include in results, can include
            aggregation functions e.g., ['name', 'total_amount:sum']
        groupby: List of field names to group by e.g., ['name']
        offset: Number of groups to skip (default: null)
        limit: Maximum number of groups to return (default: null)
        order: Sorting criteria for groups e.g., 'field_name ASC' (default: null)
    Returns:
        Dictionary with grouped and aggregated data
    """
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        data = app_context.odoo.read_group(
            model_name,
            domain,
            fields=fields,
            groupby=groupby,
            offset=offset,
            limit=limit,
            order=order,
        )
        return Response(data=data).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()

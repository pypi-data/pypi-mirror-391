"""CLI commands for mxcpctl.

This module provides the main command-line interface for managing
MXCP instances through the mxcpd API.
"""

import sys

import click
import httpx
from rich.console import Console

console = Console()


def get_headers(token: str | None) -> dict[str, str]:
    """Get HTTP headers with optional authentication token.

    Args:
        token: Optional API token for Bearer authentication

    Returns:
        Dictionary of HTTP headers
    """
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


@click.group()
@click.option("--host", default="localhost", envvar="MXCPCTL_HOST", help="mxcpd host")
@click.option("--port", default=8000, envvar="MXCPCTL_PORT", help="mxcpd port")
@click.option("--tls/--no-tls", default=False, help="Use HTTPS")
@click.option("--token", envvar="MXCPCTL_TOKEN", help="API token for authentication")
@click.version_option(version="0.1.0")
@click.pass_context
def main(ctx: click.Context, host: str, port: int, tls: bool, token: str | None) -> None:
    """mxcpctl - MXCP instance management CLI.

    Communicates with mxcpd to monitor and control MXCP instances.
    """
    # Store connection info in context
    ctx.ensure_object(dict)
    ctx.obj["host"] = host
    ctx.obj["port"] = port
    ctx.obj["base_url"] = f"{'https' if tls else 'http'}://{host}:{port}"
    ctx.obj["token"] = token


@main.command()
@click.pass_context
def health(ctx: click.Context) -> None:
    """Check mxcpd health."""
    base_url = ctx.obj["base_url"]
    token = ctx.obj.get("token")

    try:
        response = httpx.get(f"{base_url}/health", headers=get_headers(token), timeout=5.0)
        response.raise_for_status()
        data = response.json()

        console.print("[green]✓[/green] mxcpd is healthy")
        console.print(f"  Version: {data['version']}")
        console.print(f"  Instance: {data['instance']}")
        console.print(f"  Environment: {data['environment']}")
        console.print(f"  Status: {data['status']}")

    except httpx.ConnectError:
        console.print(f"[red]✗[/red] Failed to connect to {base_url}")
        console.print("  Is mxcpd running?")
        sys.exit(1)
    except httpx.TimeoutException:
        console.print("[red]✗[/red] Connection timeout")
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        console.print(f"[red]✗[/red] HTTP error: {e.response.status_code}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]✗[/red] Unexpected error: {e}")
        sys.exit(1)


@main.command()
@click.option("--instance", "-i", help="Filter by instance ID")
@click.pass_context
def status(ctx: click.Context, instance: str | None) -> None:
    """Get instance status."""
    base_url = ctx.obj["base_url"]
    token = ctx.obj.get("token")
    params = {"instance": instance} if instance else {}

    try:
        response = httpx.get(
            f"{base_url}/api/v1/status", params=params, headers=get_headers(token), timeout=10.0
        )
        response.raise_for_status()
        data = response.json()

        # Multi-instance response is a list
        for instance_data in data:
            console.print(
                f"\n[cyan]Instance: {instance_data['instance_name']}[/cyan] ({instance_data['instance_id']})"  # noqa: E501
            )
            console.print(f"  Status: [green]{instance_data.get('status', 'unknown')}[/green]")
            console.print(f"  Version: {instance_data.get('version', 'unknown')}")
            console.print(f"  Uptime: {instance_data.get('uptime', 'unknown')}")
            console.print(f"  Profile: {instance_data.get('profile', 'unknown')}")
            console.print(f"  Mode: {instance_data.get('mode', 'unknown')}")

            if instance_data.get("error"):
                console.print(f"  [red]Error: {instance_data['error']}[/red]")

    except httpx.RequestError as e:
        console.print(f"[red]✗[/red] Request failed: {e}")
        sys.exit(1)


@main.command()
@click.option("--instance", "-i", help="Filter by instance ID")
@click.pass_context
def config(ctx: click.Context, instance: str | None) -> None:
    """Get instance configuration."""
    base_url = ctx.obj["base_url"]
    token = ctx.obj.get("token")
    params = {"instance": instance} if instance else {}

    try:
        response = httpx.get(
            f"{base_url}/api/v1/config", params=params, headers=get_headers(token), timeout=10.0
        )
        response.raise_for_status()
        data = response.json()

        for config_data in data:
            console.print(
                f"\n[cyan]Instance: {config_data['instance_name']}[/cyan] ({config_data['instance_id']})"  # noqa: E501
            )
            console.print(f"  Profile: {config_data.get('profile', 'N/A')}")
            console.print(f"  Environment: {config_data.get('environment', 'N/A')}")
            console.print(f"  Read-only: {config_data.get('readonly', False)}")
            console.print(f"  Debug: {config_data.get('debug', False)}")

            if config_data.get("features"):
                features = config_data["features"]
                console.print("  Features:")
                console.print(f"    SQL Tools: {features.get('sql_tools', False)}")
                console.print(f"    Audit Logging: {features.get('audit_logging', False)}")
                console.print(f"    Telemetry: {features.get('telemetry', False)}")

    except httpx.RequestError as e:
        console.print(f"[red]✗[/red] Request failed: {e}")
        sys.exit(1)


@main.command()
@click.option("--instance", "-i", help="Filter by instance ID")
@click.pass_context
def reload(ctx: click.Context, instance: str | None) -> None:
    """Trigger configuration reload."""
    base_url = ctx.obj["base_url"]
    token = ctx.obj.get("token")
    params = {"instance": instance} if instance else {}

    try:
        response = httpx.post(
            f"{base_url}/api/v1/reload", params=params, headers=get_headers(token), timeout=30.0
        )
        response.raise_for_status()
        data = response.json()

        for reload_data in data:
            instance_name = reload_data.get("instance_name", "unknown")
            status = reload_data.get("status", "unknown")

            if status == "success":
                console.print(f"[green]✓[/green] Reload triggered for {instance_name}")
                if reload_data.get("request_id"):
                    console.print(f"  Request ID: {reload_data['request_id']}")
            else:
                console.print(f"[red]✗[/red] Reload failed for {instance_name}")
                if reload_data.get("error"):
                    console.print(f"  Error: {reload_data['error']}")

    except httpx.RequestError as e:
        console.print(f"[red]✗[/red] Request failed: {e}")
        sys.exit(1)


@main.group()
def endpoints() -> None:
    """Manage endpoints."""
    pass


@endpoints.command("list")
@click.option("--instance", "-i", help="Filter by instance ID")
@click.option(
    "--type",
    "-t",
    type=click.Choice(["tool", "resource", "prompt"]),
    help="Filter by endpoint type",
)
@click.pass_context
def list_endpoints(ctx: click.Context, instance: str | None, type: str | None) -> None:
    """List all endpoints."""
    base_url = ctx.obj["base_url"]
    token = ctx.obj.get("token")
    params = {}
    if instance:
        params["instance"] = instance

    try:
        response = httpx.get(
            f"{base_url}/api/v1/endpoints", params=params, headers=get_headers(token), timeout=10.0
        )
        response.raise_for_status()
        data = response.json()

        for instance_data in data:
            console.print(
                f"\n[cyan]Instance: {instance_data['instance_name']}[/cyan] ({instance_data['instance_id']})"  # noqa: E501
            )

            endpoints_list = instance_data.get("endpoints", [])

            # Filter by type if specified
            if type:
                endpoints_list = [ep for ep in endpoints_list if ep.get("type") == type]

            if not endpoints_list:
                console.print("  No endpoints found")
                continue

            # Group by type
            by_type: dict[str, list] = {}
            for ep in endpoints_list:
                ep_type = ep.get("type", "unknown")
                if ep_type not in by_type:
                    by_type[ep_type] = []
                by_type[ep_type].append(ep)

            for ep_type, eps in by_type.items():
                console.print(f"\n  [yellow]{ep_type.upper()}S[/yellow] ({len(eps)})")
                for ep in eps:
                    name = ep.get("name", "unknown")
                    enabled = ep.get("enabled", False)
                    status = ep.get("status", "unknown")

                    status_icon = "✓" if status == "ok" else "✗"
                    status_color = "green" if status == "ok" else "red"

                    console.print(f"    [{status_color}]{status_icon}[/{status_color}] {name}")
                    if ep.get("description"):
                        console.print(f"      {ep['description']}")
                    if not enabled:
                        console.print("      [dim](disabled)[/dim]")
                    if ep.get("error"):
                        console.print(f"      [red]Error: {ep['error']}[/red]")

    except httpx.RequestError as e:
        console.print(f"[red]✗[/red] Request failed: {e}")
        sys.exit(1)


@main.group()
def audit() -> None:
    """Query audit logs."""
    pass


@audit.command("query")
@click.option("--instance", "-i", help="Filter by instance ID")
@click.option("--operation-type", help="Filter by operation type (tool, resource, prompt)")
@click.option("--operation-name", help="Filter by operation name")
@click.option("--status", type=click.Choice(["success", "error"]), help="Filter by status")
@click.option("--user-id", help="Filter by user ID")
@click.option("--limit", default=10, help="Maximum number of records (default: 10)")
@click.option("--offset", default=0, help="Number of records to skip")
@click.pass_context
def query_audit(
    ctx: click.Context,
    instance: str | None,
    operation_type: str | None,
    operation_name: str | None,
    status: str | None,
    user_id: str | None,
    limit: int,
    offset: int,
) -> None:
    """Query audit logs with filters."""
    base_url = ctx.obj["base_url"]
    token = ctx.obj.get("token")
    params: dict[str, str | int] = {"limit": limit, "offset": offset}

    if instance:
        params["instance"] = instance
    if operation_type:
        params["operation_type"] = operation_type
    if operation_name:
        params["operation_name"] = operation_name
    if status:
        params["operation_status"] = status
    if user_id:
        params["user_id"] = user_id

    try:
        response = httpx.get(
            f"{base_url}/api/v1/audit/query",
            params=params,
            headers=get_headers(token),
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()

        for instance_data in data:
            console.print(
                f"\n[cyan]Instance: {instance_data['instance_name']}[/cyan] ({instance_data['instance_id']})"  # noqa: E501
            )

            records = instance_data.get("records", [])
            count = instance_data.get("count", 0)

            console.print(f"  Found {count} record(s)")

            if not records:
                continue

            for record in records:
                timestamp = record.get("timestamp", "N/A")
                op_type = record.get("operation_type", "N/A")
                op_name = record.get("operation_name", "N/A")
                op_status = record.get("operation_status", "N/A")
                duration = record.get("duration_ms")

                status_icon = "✓" if op_status == "success" else "✗"
                status_color = "green" if op_status == "success" else "red"

                console.print(
                    f"\n  [{status_color}]{status_icon}[/{status_color}] {op_type}/{op_name}"
                )
                console.print(f"    Time: {timestamp}")
                console.print(f"    Status: {op_status}")
                if duration is not None:
                    console.print(f"    Duration: {duration}ms")
                if record.get("user_id"):
                    console.print(f"    User: {record['user_id']}")
                if record.get("error_message"):
                    console.print(f"    [red]Error: {record['error_message']}[/red]")

    except httpx.RequestError as e:
        console.print(f"[red]✗[/red] Request failed: {e}")
        sys.exit(1)


@audit.command("stats")
@click.option("--instance", "-i", help="Filter by instance ID")
@click.pass_context
def audit_stats(ctx: click.Context, instance: str | None) -> None:
    """Get audit log statistics."""
    base_url = ctx.obj["base_url"]
    token = ctx.obj.get("token")
    params = {"instance": instance} if instance else {}

    try:
        response = httpx.get(
            f"{base_url}/api/v1/audit/stats",
            params=params,
            headers=get_headers(token),
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()

        for instance_data in data:
            console.print(
                f"\n[cyan]Instance: {instance_data['instance_name']}[/cyan] ({instance_data['instance_id']})"  # noqa: E501
            )

            total = instance_data.get("total_records", 0)
            console.print(f"  Total Records: {total}")

            if instance_data.get("by_type"):
                console.print("\n  By Type:")
                for op_type, count in instance_data["by_type"].items():
                    console.print(f"    {op_type}: {count}")

            if instance_data.get("by_status"):
                console.print("\n  By Status:")
                for status, count in instance_data["by_status"].items():
                    status_color = "green" if status == "success" else "red"
                    console.print(f"    [{status_color}]{status}[/{status_color}]: {count}")

            if instance_data.get("earliest_timestamp"):
                console.print("\n  Time Range:")
                console.print(f"    Earliest: {instance_data['earliest_timestamp']}")
                console.print(f"    Latest: {instance_data.get('latest_timestamp', 'N/A')}")

    except httpx.RequestError as e:
        console.print(f"[red]✗[/red] Request failed: {e}")
        sys.exit(1)


@main.group()
def telemetry() -> None:
    """Query telemetry data (traces and metrics)."""
    pass


@telemetry.command("status")
@click.pass_context
def telemetry_status(ctx: click.Context) -> None:
    """Get telemetry receiver status."""
    base_url = ctx.obj["base_url"]
    token = ctx.obj.get("token")

    try:
        response = httpx.get(
            f"{base_url}/api/v1/telemetry/status", headers=get_headers(token), timeout=10.0
        )
        response.raise_for_status()
        result = response.json()
        data = result.get("data", {})

        console.print("\n[cyan]Telemetry Receiver Status[/cyan]")
        console.print(f"  Enabled: {'Yes' if data.get('enabled') else 'No'}")
        console.print(f"  Traces Received: {data.get('traces_received', 0)}")
        console.print(f"  Traces Stored: {data.get('traces_stored', 0)}")
        console.print(f"  Metrics Received: {data.get('metrics_received', 0)}")
        console.print(f"  Storage Usage: {data.get('storage_usage_mb', 0):.2f} MB")

        if data.get("last_trace_time"):
            console.print(f"  Last Trace: {data['last_trace_time']}")

    except httpx.RequestError as e:
        console.print(f"[red]✗[/red] Request failed: {e}")
        sys.exit(1)


@telemetry.command("traces")
@click.option("--limit", default=20, help="Maximum number of traces to show")
@click.option("--endpoint", help="Filter by endpoint name")
@click.pass_context
def list_traces(ctx: click.Context, limit: int, endpoint: str | None) -> None:
    """List recent traces."""
    base_url = ctx.obj["base_url"]
    token = ctx.obj.get("token")
    params: dict[str, str | int] = {"limit": limit}

    if endpoint:
        params["endpoint_name"] = endpoint

    try:
        response = httpx.get(
            f"{base_url}/api/v1/telemetry/traces",
            params=params,
            headers=get_headers(token),
            timeout=10.0,
        )
        response.raise_for_status()
        result = response.json()
        data = result.get("data", {})
        traces = data.get("items", [])

        if not traces:
            console.print("No traces found")
            return

        console.print(f"\n[cyan]Recent Traces[/cyan] (showing {len(traces)})")

        for trace in traces:
            trace_id = trace.get("trace_id", "N/A")
            endpoint_name = trace.get("endpoint_name", "N/A")
            duration = trace.get("duration_ms", 0)
            status = trace.get("status", "unknown")
            span_count = trace.get("span_count", 0)

            status_icon = "✓" if status == "ok" else "✗"
            status_color = "green" if status == "ok" else "red"

            console.print(f"\n  [{status_color}]{status_icon}[/{status_color}] {endpoint_name}")
            console.print(f"    Trace ID: {trace_id}")
            console.print(f"    Duration: {duration:.2f}ms")
            console.print(f"    Spans: {span_count}")
            console.print(f"    Time: {trace.get('start_time', 'N/A')}")

    except httpx.RequestError as e:
        console.print(f"[red]✗[/red] Request failed: {e}")
        sys.exit(1)


@telemetry.command("trace")
@click.argument("trace_id")
@click.pass_context
def get_trace(ctx: click.Context, trace_id: str) -> None:
    """Get detailed trace information."""
    base_url = ctx.obj["base_url"]
    token = ctx.obj.get("token")

    try:
        response = httpx.get(
            f"{base_url}/api/v1/telemetry/traces/{trace_id}",
            headers=get_headers(token),
            timeout=10.0,
        )
        response.raise_for_status()
        result = response.json()
        trace = result.get("data", {})

        console.print("\n[cyan]Trace Details[/cyan]")
        console.print(f"  Trace ID: {trace.get('trace_id', 'N/A')}")
        console.print(f"  Endpoint: {trace.get('endpoint_name', 'N/A')}")
        console.print(f"  Service: {trace.get('service_name', 'N/A')}")
        console.print(f"  Duration: {trace.get('duration_ms', 0):.2f}ms")
        console.print(f"  Status: {trace.get('status', 'unknown')}")
        console.print(f"  Span Count: {trace.get('span_count', 0)}")

        spans = trace.get("spans", [])
        if spans:
            console.print("\n  [yellow]Spans[/yellow]:")
            for span in spans:
                indent = "    " if span.get("parent_span_id") else "  "
                name = span.get("name", "N/A")
                duration = span.get("duration_ms", 0)
                console.print(f"{indent}• {name} ({duration:.2f}ms)")

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            console.print(f"[red]✗[/red] Trace not found: {trace_id}")
        else:
            console.print(f"[red]✗[/red] HTTP error: {e.response.status_code}")
        sys.exit(1)
    except httpx.RequestError as e:
        console.print(f"[red]✗[/red] Request failed: {e}")
        sys.exit(1)


@telemetry.command("metrics")
@click.option("--endpoint", help="Filter by endpoint name")
@click.option("--window", type=int, help="Time window in hours (1-24)")
@click.pass_context
def get_metrics(ctx: click.Context, endpoint: str | None, window: int | None) -> None:
    """Get aggregated performance metrics."""
    base_url = ctx.obj["base_url"]
    token = ctx.obj.get("token")
    params: dict[str, str | int] = {}

    if endpoint:
        params["endpoint_name"] = endpoint
    if window:
        params["window_hours"] = window

    try:
        response = httpx.get(
            f"{base_url}/api/v1/telemetry/metrics",
            params=params,
            headers=get_headers(token),
            timeout=10.0,
        )
        response.raise_for_status()
        result = response.json()
        data = result.get("data", {})
        metrics = data.get("metrics", [])

        if not metrics:
            console.print("No metrics found")
            return

        window_str = f"{window}h" if window else "all time"
        console.print(f"\n[cyan]Performance Metrics[/cyan] ({window_str})")

        for metric in metrics:
            endpoint_name = metric.get("endpoint_name", "N/A")
            requests = metric.get("request_count", 0)
            errors = metric.get("error_count", 0)
            error_rate = metric.get("error_rate", 0) * 100

            console.print(f"\n  [yellow]{endpoint_name}[/yellow]")
            console.print(f"    Requests: {requests}")
            console.print(f"    Errors: {errors} ({error_rate:.1f}%)")

            if metric.get("p50_ms") is not None:
                console.print("    Latency:")
                console.print(f"      P50: {metric['p50_ms']:.2f}ms")
                console.print(f"      P95: {metric.get('p95_ms', 0):.2f}ms")
                console.print(f"      P99: {metric.get('p99_ms', 0):.2f}ms")
                console.print(f"      Avg: {metric.get('avg_ms', 0):.2f}ms")

    except httpx.RequestError as e:
        console.print(f"[red]✗[/red] Request failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

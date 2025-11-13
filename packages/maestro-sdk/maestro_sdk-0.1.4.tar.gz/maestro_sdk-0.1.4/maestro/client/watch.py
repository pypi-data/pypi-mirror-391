"""Monitor a workflow instance execution and report all the changes from the workflow and its step instances."""

from __future__ import annotations

import sys
import time
from datetime import datetime
from typing import Any

from .client import MaestroClient

WF_TERMINAL_STATES = {"TIMED_OUT", "STOPPED", "FAILED", "SUCCEEDED", "NOT_FOUND"}


def _get_workflow_data(client: MaestroClient, workflow_id: str, instance_id: int) -> tuple[str, dict[str, Any]]:
    """
    Get workflow instance data and extract aggregated info.
    :param client: Maestro API client
    :param workflow_id: workflow id to get the data
    :param instance_id: instance id to get the data
    :return: tuple of workflow status nad step views
    """
    wf_instance = client.get_instance(workflow_id, instance_id)
    if wf_instance.get("status", None) == "NOT_FOUND":
        return "NOT_FOUND", {}

    agg_info = wf_instance.get("aggregated_info", {})
    wf_status = agg_info.get("workflow_instance_status", "UNKNOWN")
    step_views = agg_info.get("step_aggregated_views", {})
    return wf_status, step_views


def _show_step_changes(step_views: dict[str, Any], cur_steps: dict[str, str], dot_printed: bool) -> bool:
    """
    Show step changes.
    :param step_views: newly fetched step_aggregated_views
    :param cur_steps: the currently tracked step statuses
    :return: True if there is any step status change, otherwise, false.
    """
    status_changed = False

    for step_id, step_info in step_views.items():
        status = step_info.get("status", "UNKNOWN")

        if status == "NOT_CREATED":
            continue

        if step_id not in cur_steps or cur_steps[step_id] != status:
            if dot_printed:
                print()
                dot_printed = False
            print(f"[{datetime.now().strftime("%H:%M:%S")}]: {step_id} -> {status}")
            cur_steps[step_id] = status
            status_changed = True

    return status_changed


def watch_workflow(client: MaestroClient, workflow_id: str, instance_id: int, poll_interval: int = 3) -> None:
    """
    Watch a workflow instance execution and also show the step status changes.

    :param client: Maestro API client
    :param workflow_id: workflow id to watch
    :param instance_id: instance id to watch
    :param poll_interval: polling interval in seconds
    """
    print(f"Watching workflow instance [{workflow_id}][{instance_id}]...")

    cur_steps: dict[str, str] = {}
    dot_printed = False

    try:
        wf_status, step_views = _get_workflow_data(client, workflow_id, instance_id)

        print(f"-> Current workflow status: [{wf_status}]")
        print("-"*50)
        status_changed = _show_step_changes(step_views, cur_steps, dot_printed)

        while wf_status not in WF_TERMINAL_STATES:
            if not status_changed:
                print(".", end="", flush=True)
                dot_printed = True

            time.sleep(poll_interval)

            wf_status, step_views = _get_workflow_data(client, workflow_id, instance_id)
            status_changed = _show_step_changes(step_views, cur_steps, dot_printed)
            if status_changed:
                dot_printed = False

        if dot_printed:
            print()
        print("-"*50)
        if wf_status == "NOT_FOUND":
            print(f"x Workflow instance [{workflow_id}][{instance_id}] not found")
        else:
            print(f"* Workflow instance [{workflow_id}][{instance_id}] is completed with status [{wf_status}]")

    except KeyboardInterrupt:
        print("\nWatch interrupted by user")
    except Exception as e:
        print(f"\nWatch failed due to exception: {e}")
        sys.exit(1)

import shutil
import subprocess
from pathlib import Path
from typing import Any

from .base import AzureMCPError, get_context


def list_resource_groups() -> list[dict[str, Any]]:
    try:
        ctx = get_context()
        client = ctx.resource_client
        rgs = list(client.resource_groups.list())

        result = []
        for rg in rgs:
            rg_dict = rg.as_dict()
            tags = rg_dict.get("tags", {}) or {}
            rg_dict["application"] = tags.get("application", "None")
            result.append(rg_dict)

        return result

    except AzureMCPError:
        raise
    except Exception as e:
        msg = f"Failed to list resource groups: {e}"
        raise AzureMCPError(msg) from e


def list_resources_in_group(resource_group: str) -> list[dict[str, Any]]:
    try:
        ctx = get_context()
        client = ctx.resource_client
        resources = list(client.resources.list_by_resource_group(resource_group))
        return [r.as_dict() for r in resources]

    except AzureMCPError:
        raise
    except Exception as e:
        msg = f"Failed to list resources in group '{resource_group}': {e}"
        raise AzureMCPError(msg) from e


def export_resource_group_template(resource_group: str) -> dict[str, Any]:
    try:
        ctx = get_context()
        client = ctx.resource_client

        export_result = client.resource_groups.begin_export_template(
            resource_group_name=resource_group,
            parameters={"options": "IncludeParameterDefaultValue", "resources": ["*"]},
        ).result()

        if hasattr(export_result, "as_dict"):
            d = export_result.as_dict()
            if "template" in d:
                return d["template"]
            return d

        if hasattr(export_result, "template"):
            return export_result.template

        return {"export_result": str(export_result)}

    except AzureMCPError:
        raise
    except Exception as e:
        msg = f"Failed to export resource group template for '{resource_group}': {e}"
        raise AzureMCPError(msg) from e


def decompile_arm_to_bicep(arm_template_path: str, output_path: str | None = None) -> str:
    if shutil.which("az") is None:
        msg = (
            "Azure CLI is not available. Install Azure CLI to use Bicep decompilation. "
            "See: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli"
        )
        raise AzureMCPError(msg)

    arm_template_file = Path(arm_template_path)
    if not arm_template_file.is_file():
        error_msg = f"ARM template not found: {arm_template_file}"
        raise AzureMCPError(error_msg)

    arm_template_file = arm_template_file.resolve()
    if not arm_template_file.is_relative_to(Path.cwd()):
        error_msg = "ARM template path must be located within the repository"
        raise AzureMCPError(error_msg)

    output_file = Path(output_path) if output_path else arm_template_file.with_suffix(".bicep")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file = output_file.resolve()
    if not output_file.is_relative_to(Path.cwd()):
        error_msg = "Output path must be located within the repository"
        raise AzureMCPError(error_msg)

    command = [
        "az",
        "bicep",
        "decompile",
        "--file",
        str(arm_template_file),
        "--outfile",
        str(output_file),
    ]

    try:
        subprocess.run(command, capture_output=True, text=True, check=True)  # noqa: S603
        return str(output_file)

    except AzureMCPError:
        raise
    except subprocess.CalledProcessError as e:
        msg = f"Bicep decompilation failed: {e.stderr or e.stdout or str(e)}"
        raise AzureMCPError(msg) from e
    except Exception as e:
        msg = f"Failed to decompile ARM template: {e}"
        raise AzureMCPError(msg) from e

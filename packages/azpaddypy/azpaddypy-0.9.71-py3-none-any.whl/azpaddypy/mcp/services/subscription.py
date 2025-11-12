from typing import Any

from .base import AzureMCPError, get_context


def list_subscriptions() -> list[dict[str, Any]]:
    try:
        from azure.identity import DefaultAzureCredential
        from azure.mgmt.resource import SubscriptionClient

        credential = DefaultAzureCredential()
        client = SubscriptionClient(credential)

        subs = list(client.subscriptions.list())
        return [
            s.as_dict()
            if hasattr(s, "as_dict")
            else {
                "subscriptionId": getattr(s, "subscription_id", None),
                "displayName": getattr(s, "display_name", None),
                "state": getattr(s, "state", None),
                "tenantId": getattr(s, "tenant_id", None),
            }
            for s in subs
        ]

    except AzureMCPError:
        raise
    except Exception as e:
        msg = f"Failed to list subscriptions: {e}"
        raise AzureMCPError(msg) from e


def get_subscription_info() -> dict[str, Any]:
    try:
        ctx = get_context()
        subscription_id = ctx.subscription_id
        client = ctx.subscription_client

        sub = client.subscriptions.get(subscription_id)

        if hasattr(sub, "as_dict"):
            return sub.as_dict()

        return {
            "subscriptionId": getattr(sub, "subscription_id", subscription_id),
            "displayName": getattr(sub, "display_name", None),
            "state": getattr(sub, "state", None),
            "tenantId": getattr(sub, "tenant_id", None),
        }

    except AzureMCPError:
        raise
    except Exception as e:
        msg = f"Failed to get subscription info: {e}"
        raise AzureMCPError(msg) from e


def list_locations() -> list[dict[str, Any]]:
    try:
        ctx = get_context()
        subscription_id = ctx.subscription_id
        client = ctx.subscription_client

        locs = list(client.subscriptions.list_locations(subscription_id))
        return [
            l.as_dict()
            if hasattr(l, "as_dict")
            else {"name": getattr(l, "name", None), "displayName": getattr(l, "display_name", None)}
            for l in locs
        ]

    except AzureMCPError:
        raise
    except Exception as e:
        msg = f"Failed to list locations: {e}"
        raise AzureMCPError(msg) from e

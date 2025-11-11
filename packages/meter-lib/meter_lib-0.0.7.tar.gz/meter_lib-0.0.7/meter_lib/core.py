from datetime import datetime
from typing import Optional
import requests

def fetch_customer_id(tenant_id: str, portal_url: str, api_key: str = None):
    """
    Fetch the customer account for a given tenant_id.
    Returns a dict with customer info, or None if not found/error.
    """
    url = f" http://metering.metering.svc.cluster.local:8000/v1alpha1/customer-accounts/tenant/{tenant_id}"
    headers = {}
    
    if portal_url and api_key:
        headers["x-api-key"] = api_key
        url = f"{portal_url}/metering/v1alpha1/customer-accounts/tenant/{tenant_id}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Handle list response
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        elif isinstance(data, dict):
            return data
        else:
            print(f"No customer account found for tenant {tenant_id}")
            return None

    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def post_meter_usage(tenant_id: str, device_id: str, meter_id: str, kafka_url: str, total_usage: int,  portal_url: str = None, api_key: str = None ) :
    """
    Posts meter usage to the events API.
    Uses tenant_id + device_id in headers and includes customer_id in payload.
    """
    customer_account = fetch_customer_id(tenant_id, portal_url, api_key)

    if not customer_account:
        print("No customer account available, skipping meter usage post")
        return None

    url = f"{kafka_url}/topics/usage-events"
    headers = {
        "Content-Type": "application/vnd.kafka.json.v2+json",
    }
    payload = {
        "records": [
            {
                "value": {
                    "meter_id": meter_id,
                    "customer_id": customer_account["id"],
                    "total_usage": total_usage
                }
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f" Error posting to {url}: {e}")
        return None
    
def post_ai_meter_usage(tenant_id: str, device_id: str, meter_id: str, kafka_url: str, portal_url: str = None, api_key: str = None, start_time:Optional[datetime]= None, end_time:Optional[datetime]=None) :
    """
    Posts meter usage to the ai events API.
    Uses tenant_id + device_id in headers and includes customer_id in payload.
    """
    customer_account = fetch_customer_id(tenant_id, portal_url, api_key)

    if not customer_account:
        print("No customer account available, skipping meter usage post")
        return None

    url = f"{kafka_url}/topics/usage-events"
    headers = {
        "Content-Type": "application/vnd.kafka.json.v2+json",
    }
    
    event_value = {
        "ai_event": True,
        "meter_id": meter_id,
        "customer_id": customer_account["id"],
    }
    if start_time:
        event_value["start_time"] = start_time.isoformat()
    if end_time:
        event_value["end_time"] = end_time.isoformat()

    payload = {
        "records": [
            {
                "value": event_value
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f" Error posting to {url}: {e}")
        return None


"""Client for the railops-stats AWS Lambda function.

Primary path: HTTP POST to the API served by `sam local start-api` (AWS SAM CLI
running the Lambda in a Docker Lambda runtime), configurable with RAILOPS_STATS_URL.
Fallback: import the very same handler module and run it in-process, clearly
labelled, so deployments without SAM (e.g. Vercel) keep working.
"""
import importlib.util
import json
import os
import urllib.error
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HANDLER_PATH = os.path.join(BASE_DIR, "aws", "functions", "stats", "app.py")
DEFAULT_URL = "http://127.0.0.1:3000/stats"


def stats_url():
    return os.getenv("RAILOPS_STATS_URL", DEFAULT_URL)


def _load_handler():
    spec = importlib.util.spec_from_file_location("railops_stats_lambda", HANDLER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.handler


def get_stats(snapshot, timeout=20):
    """Returns (stats_dict, source, error). source is 'sam-local' or 'in-process'."""
    payload = json.dumps(snapshot).encode()
    request = urllib.request.Request(stats_url(), data=payload, method="POST", headers={"Content-Type": "application/json"})
    error = None
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode()), "sam-local", None
    except urllib.error.HTTPError as exc:
        error = f"Lambda returned HTTP {exc.code}"
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        error = f"SAM local API not reachable at {stats_url()} ({getattr(exc, 'reason', exc)})"
    result = _load_handler()({"body": json.dumps(snapshot)}, None)
    return json.loads(result["body"]), "in-process", error

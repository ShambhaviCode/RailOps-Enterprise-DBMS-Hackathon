"""railops-stats: AWS Lambda function that turns a RailOps data snapshot into
operational statistics and an attention list for administrators.

Pure Python, no external dependencies, so it runs identically through
`sam local invoke`, `sam local start-api`, a real Lambda, or in-process.
Input: API Gateway proxy event whose JSON body is the RailOps snapshot
(trains, stations, routes, schedules, employees) - see aws/events/stats-event.json.
"""
import json
from collections import Counter


def compute_stats(snapshot):
    trains = snapshot.get("trains") or []
    stations = snapshot.get("stations") or []
    routes = snapshot.get("routes") or []
    schedules = snapshot.get("schedules") or []
    employees = snapshot.get("employees") or []

    station_names = {str(s.get("name", "")).strip().lower() for s in stations}
    station_cities = {str(s.get("city", "")).strip().lower() for s in stations}
    known_places = station_names | station_cities

    capacities = [int(t.get("capacity") or 0) for t in trains]
    distances = [int(r.get("distance_km") or 0) for r in routes]
    platforms = [int(s.get("platforms") or 0) for s in stations]

    scheduled_routes = Counter(str(s.get("route", "")) for s in schedules)
    scheduled_trains = Counter(str(s.get("train", "")) for s in schedules)
    platform_load = Counter(str(s.get("platform", "")) for s in schedules)
    train_numbers = Counter(str(t.get("number", "")) for t in trains)

    attention = []
    for t in trains:
        for end in ("source", "destination"):
            place = str(t.get(end, "")).strip()
            if place and place.lower() not in known_places:
                attention.append({"severity": "high", "module": "Trains", "item": f"{t.get('number')} {t.get('name')}", "issue": f"{end} '{place}' has no matching station record"})
    for number, count in train_numbers.items():
        if count > 1:
            attention.append({"severity": "high", "module": "Trains", "item": number, "issue": f"train number appears {count} times"})
    for r in routes:
        if r.get("name") and str(r.get("name")) not in scheduled_routes:
            attention.append({"severity": "medium", "module": "Routes", "item": f"{r.get('code')} {r.get('name')}", "issue": "route has no schedule assigned"})
    for t in trains:
        label = f"{t.get('number')} {t.get('name')}"
        if label not in scheduled_trains:
            attention.append({"severity": "medium", "module": "Trains", "item": label, "issue": "train is not scheduled on any route"})
    for s in stations:
        if int(s.get("platforms") or 0) < 5:
            attention.append({"severity": "low", "module": "Stations", "item": f"{s.get('code')} {s.get('name')}", "issue": f"only {s.get('platforms')} platforms - capacity risk"})
    for e in employees:
        if str(e.get("status", "")).lower() != "active":
            attention.append({"severity": "low", "module": "Employees", "item": f"{e.get('code')} {e.get('name')}", "issue": f"status is {e.get('status')}"})
    for s in schedules:
        if s.get("arrival") and s.get("departure") and str(s["departure"]) < str(s["arrival"]):
            attention.append({"severity": "medium", "module": "Schedules", "item": f"{s.get('train')} on {s.get('route')}", "issue": "departure is before arrival"})

    order = {"high": 0, "medium": 1, "low": 2}
    attention.sort(key=lambda a: order[a["severity"]])

    return {
        "summary": {
            "trains": len(trains),
            "stations": len(stations),
            "routes": len(routes),
            "schedules": len(schedules),
            "employees": len(employees),
            "active_employees": sum(1 for e in employees if str(e.get("status", "")).lower() == "active"),
        },
        "fleet": {
            "total_seat_capacity": sum(capacities),
            "average_capacity": round(sum(capacities) / len(capacities)) if capacities else 0,
            "largest_train": max(trains, key=lambda t: int(t.get("capacity") or 0), default={}).get("name"),
        },
        "network": {
            "total_route_km": sum(distances),
            "longest_route": max(routes, key=lambda r: int(r.get("distance_km") or 0), default={}).get("name"),
            "total_platforms": sum(platforms),
            "states_covered": len({str(s.get("state", "")).lower() for s in stations if s.get("state")}),
        },
        "scheduling": {
            "routes_with_schedules": len(scheduled_routes),
            "routes_without_schedules": max(len(routes) - len(scheduled_routes), 0),
            "trains_scheduled": len(scheduled_trains),
            "busiest_platform": platform_load.most_common(1)[0][0] if platform_load else None,
        },
        "attention": attention,
        "attention_count": {"high": sum(a["severity"] == "high" for a in attention), "medium": sum(a["severity"] == "medium" for a in attention), "low": sum(a["severity"] == "low" for a in attention)},
        "health_score": max(0, 100 - 15 * sum(a["severity"] == "high" for a in attention) - 7 * sum(a["severity"] == "medium" for a in attention) - 2 * sum(a["severity"] == "low" for a in attention)),
        "generated_by": "railops-stats Lambda (AWS SAM)",
    }


def handler(event, context):
    body = event.get("body") if isinstance(event, dict) else None
    if body is None:
        snapshot = event if isinstance(event, dict) else {}
    else:
        try:
            snapshot = json.loads(body) if isinstance(body, str) else body
        except json.JSONDecodeError:
            return {"statusCode": 400, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": "body must be JSON"})}
    result = compute_stats(snapshot or {})
    result["invoked_via"] = "aws-lambda" if context is not None and getattr(context, "function_name", None) else "in-process"
    return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps(result)}

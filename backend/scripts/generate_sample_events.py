import sys
import argparse
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import db_manager, init_indexes
from app.services.sample_generator import SampleEventGenerator
from app.services.event_service import EventService
from app.core.logging_config import setup_logging, logger


def generate_and_ingest(scenario: str, count: int):
    setup_logging()
    logger.info(f"Connecting to MongoDB Atlas to ingest sample '{scenario}' events...")

    if not db_manager.connect():
        logger.error(f"Cannot connect to MongoDB Atlas: {db_manager.last_error}")
        return []

    db = db_manager.get_db()
    init_indexes(db)
    svc = EventService(db)

    events = SampleEventGenerator.generate_events(scenario_key=scenario, count=count)
    ingested = []

    for ev in events:
        saved = svc.ingest_event(ev, run_detection=True, actor="sample_generator")
        ingested.append(saved)
        logger.info(
            f"Ingested event: {saved.id} | Category: {saved.category} | Severity: {saved.severity} | Risk: {saved.risk_score}"
        )

    # Check resulting alerts
    alerts = list(db.alerts.find({"related_event_id": {"$in": [e.id for e in ingested]}}))
    logger.info(f"Sample generation completed. Ingested {len(ingested)} events; created {len(alerts)} alerts in Atlas.")

    return ingested


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate safe RFC 5737 simulated network events and trigger SentinelAI detection")
    parser.add_argument(
        "--scenario",
        choices=["port_scan", "dos_syn_flood", "brute_force", "anomalous_beacon", "benign_web"],
        default="port_scan",
        help="Attack scenario to simulate",
    )
    parser.add_argument("--count", type=int, default=3, help="Number of events to generate")
    parser.add_argument("--list", action="store_true", help="List available scenarios")

    args = parser.parse_args()

    if args.list:
        print("\nAvailable Simulated Scenarios:")
        for s in SampleEventGenerator.list_scenarios():
            print(f"  • {s['key']:18} : {s['name']} (Severity: {s['severity']}, Expected Risk: {s['riskScore']})")
            print(f"    {s['description']}")
            print(f"    Source IP: {s['sourceIp']} -> Dest IP: {s['destIp']}\n")
    else:
        generate_and_ingest(args.scenario, args.count)

import asyncio

from orchepy_client import OrchepyClient


async def main() -> None:
    """Demonstrate workflow automation features."""
    client = OrchepyClient(base_url="http://localhost:3296")

    # Create a workflow with automations
    print("Creating workflow with automations...")
    workflow = await client.create_workflow(
        name="Invoice Processing",
        phases=["Upload", "OCR", "Validation", "Manual Review", "Approved"],
        initial_phase="Upload",
        automations={
            "automations": [
                {
                    "trigger": "on_enter",
                    "phase": "OCR",
                    "actions": [
                        {
                            "type": "webhook",
                            "id": "ocr_process",
                            "name": "Start OCR Processing",
                            "url": "https://ocr-service.com/process",
                            "method": "POST",
                            "headers": {
                                "Authorization": "Bearer YOUR_TOKEN",
                                "Content-Type": "application/json",
                            },
                            "fields": ["case_id", "data"],
                            "retry": {
                                "enabled": True,
                                "max_attempts": 3,
                                "delay_ms": 1000,
                            },
                            "on_error": "stop",
                        },
                        {
                            "type": "delay",
                            "name": "Wait for OCR",
                            "duration_ms": 5000,
                        },
                    ],
                },
                {
                    "trigger": "on_enter",
                    "phase": "Validation",
                    "actions": [
                        {
                            "type": "conditional",
                            "operator": "AND",
                            "conditions": [
                                {"field": "data.amount", "op": ">", "value": 10000},
                                {"field": "status", "op": "==", "value": "active"},
                            ],
                            "then": [
                                {
                                    "type": "webhook",
                                    "url": "https://manager-approval.com/request",
                                },
                                {
                                    "type": "move_to_phase",
                                    "phase": "Manual Review",
                                },
                            ],
                            "else": [
                                {
                                    "type": "set_field",
                                    "field": "data.auto_approved",
                                    "value": True,
                                },
                                {
                                    "type": "move_to_phase",
                                    "phase": "Approved",
                                },
                            ],
                        }
                    ],
                },
            ]
        },
    )
    print(f"✓ Created workflow with automations: {workflow['id']}")

    # Create a case (automations will run automatically)
    print("\nCreating case (automations will trigger)...")
    case = await client.create_case(
        workflow_id=workflow["id"],
        data={
            "invoice_number": "INV-001",
            "amount": 15000,
            "vendor": "Acme Supplies",
        },
    )
    print(f"✓ Case created: {case['id']}")
    print("  Automations will execute in the background")

    print("\n✅ Automation example completed!")


if __name__ == "__main__":
    asyncio.run(main())

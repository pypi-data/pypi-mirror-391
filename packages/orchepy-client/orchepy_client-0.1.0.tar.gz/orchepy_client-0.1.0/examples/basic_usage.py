import asyncio

from orchepy_client import OrchepyClient


async def main() -> None:
    """Demonstrate basic orchepy-client usage."""
    # Initialize client
    client = OrchepyClient(base_url="http://localhost:3296")

    # Create a workflow
    print("Creating workflow...")
    workflow = await client.create_workflow(
        name="Sales Pipeline",
        phases=["Lead", "Qualified", "Proposal", "Negotiation", "Closed"],
        initial_phase="Lead",
        active=True,
        sla_config={
            "Lead": {"hours": 24},
            "Qualified": {"hours": 48},
            "Proposal": {"hours": 72},
        },
    )
    print(f"✓ Created workflow: {workflow['id']}")

    # Create a case
    print("\nCreating case...")
    case = await client.create_case(
        workflow_id=workflow["id"],
        data={
            "customer": "Acme Corp",
            "value": 50000,
            "contact": "john@acme.com",
            "product": "Enterprise Plan",
        },
        metadata={
            "source": "website",
            "campaign": "Q4-2024",
        },
    )
    print(f"✓ Created case: {case['id']}")
    print(f"  Current phase: {case['current_phase']}")

    # Move case to next phase
    print("\nMoving case to 'Qualified'...")
    await client.move_case(
        case_id=case["id"],
        to_phase="Qualified",
        reason="Customer showed interest in enterprise plan",
        triggered_by="sales-agent-123",
    )
    print("✓ Case moved successfully")

    # Update case data
    print("\nUpdating case data...")
    await client.update_case_data(
        case_id=case["id"],
        data={
            "value": 75000,
            "notes": "Upgraded to premium package",
        },
    )
    print("✓ Case data updated")

    # Send notification
    print("\nSending notification...")
    await client.send_notification(
        case_id=case["id"],
        subject="Follow-up Required",
        body="Please schedule a demo call with the customer.",
    )
    print("✓ Notification sent")

    # Get updated case info
    print("\nFetching updated case info...")
    updated_case = await client.get_case(case["id"])
    print(f"✓ Case info retrieved")
    print(f"  Current phase: {updated_case['current_phase']}")
    print(f"  Value: {updated_case['data']['value']}")

    # Get case history
    print("\nFetching case history...")
    history = await client.get_case_history(case["id"])
    print(f"✓ Retrieved {len(history)} history entries")
    for entry in history:
        from_phase = entry.get("from_phase") or "START"
        to_phase = entry["to_phase"]
        print(f"  {from_phase} → {to_phase}")

    # List all cases in workflow
    print("\nListing cases in workflow...")
    cases = await client.list_cases(workflow_id=workflow["id"])
    print(f"✓ Found {len(cases)} case(s) in workflow")

    print("\n✅ Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())

# mewo_ovhcloud

## Testing

**WARNING: This creates real instances on ovhcloud**

You need these env vars for testing:

    export OVH_APPLICATION_KEY="your_key"
    export OVH_APPLICATION_SECRET="your_secret"
    export OVH_CONSUMER_KEY="your_consumer_key"
    export OVH_PROJECT_ID="your_project_id"
    
You can also run:

    mkunlock ovhcloud --source'


Run quick validation (no resources created):

    poetry run python tests/test_e2e.py quick

Run full end-to-end test (creates and deletes resources):

    poetry run python tests/test_e2e.py

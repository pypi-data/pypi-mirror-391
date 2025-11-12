"""Example: Working with organization resources."""

from dataspace_sdk import DataSpaceClient

# Initialize and login
client = DataSpaceClient(base_url="https://api.dataspace.example.com")
keycloak_token = "your_keycloak_token_here"

try:
    user_info = client.login(keycloak_token=keycloak_token)
    print(f"Logged in as: {user_info['user']['username']}\n")
    
    # Iterate through user's organizations
    for org in user_info['user']['organizations']:
        print(f"Organization: {org['name']}")
        print(f"Role: {org['role']}")
        print("-" * 50)
        
        # Get datasets for this organization
        datasets = client.datasets.get_organization_datasets(
            organization_id=org['id'],
            limit=10
        )
        print(f"Datasets: {len(datasets)}")
        for dataset in datasets[:5]:
            print(f"  - {dataset['title']}")
        
        # Get AI models for this organization
        models = client.aimodels.get_organization_models(
            organization_id=org['id'],
            limit=10
        )
        print(f"\nAI Models: {len(models)}")
        for model in models[:5]:
            print(f"  - {model.get('displayName', model.get('name'))}")
        
        # Get use cases for this organization
        usecases = client.usecases.get_organization_usecases(
            organization_id=org['id'],
            limit=10
        )
        print(f"\nUse Cases: {len(usecases)}")
        for usecase in usecases[:5]:
            print(f"  - {usecase['title']}")
        
        print("\n")

except Exception as e:
    print(f"Error: {e}")

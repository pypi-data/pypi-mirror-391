"""
Onehouse CLI Tool
Execute SQL commands against Onehouse API using stored credentials.
"""

import os
import json
import sys
import argparse
import requests
import time
from pathlib import Path


def load_credentials():
    """Load credentials from ~/.onehouse/credentials file."""
    credentials_file = Path.home() / ".onehouse" / "credentials"
    if not credentials_file.exists():
        print("Error: No credentials found. Run 'onehouse-cli-configure' first to set up credentials.")
        return None

    try:
        with open(credentials_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading credentials file: {e}")
        return None


def get_profile_credentials(credentials, profile_name):
    """Get credentials for a specific profile."""
    if profile_name not in credentials:
        available_profiles = list(credentials.keys())
        print(f"Error: Profile '{profile_name}' not found.")
        if available_profiles:
            print(f"Available profiles: {', '.join(available_profiles)}")
        else:
            print("No profiles found. Run 'onehouse-cli-configure' to create one.")
        return None

    return credentials[profile_name]


def check_request_status(profile_creds, request_id):
    """Check the status of a request using the status endpoint."""
    api_endpoint = profile_creds.get('api_endpoint', 'https://api.onehouse.ai')
    url = f"{api_endpoint}/v1/status/{request_id}"

    headers = {
        'x-onehouse-account-uid': profile_creds['account_uid'],
        'x-onehouse-project-uid': profile_creds['project_uid'],
        'x-onehouse-api-key': profile_creds['api_key'],
        'x-onehouse-api-secret': profile_creds['api_secret'],
        'x-onehouse-region': profile_creds['project_region'],
        'x-onehouse-uuid': profile_creds['user_id']
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"Status check failed with status {response.status_code}")
            try:
                error_data = response.json()
                print("Error response:", json.dumps(error_data, indent=2))
            except json.JSONDecodeError:
                print("Error response:", response.text)
            return None

    except requests.exceptions.RequestException as e:
        print(f"Status check request failed: {e}")
        return None


def check_status_async(profile_creds, request_id):
    """Check the status of a request asynchronously without timeout."""
    print(f"Checking status for request ID: {request_id}")

    status_result = check_request_status(profile_creds, request_id)

    if status_result is None:
        print("Failed to check status.")
        return False

    # Try different possible status field names
    status = (status_result.get('status') or
             status_result.get('state') or
             status_result.get('jobStatus') or
             status_result.get('requestStatus') or
             status_result.get('apiStatus') or '').lower()

    print(f"Current Status: {status}")

    if status in ['completed', 'success', 'finished', 'done', 'succeed', 'api_operation_status_success']:
        print("✅ Request completed successfully!")

        # Only show result if it's not empty
        result_to_show = status_result.get('apiResponse', status_result)
        if result_to_show and result_to_show != {}:
            print("Result:")
            print(json.dumps(result_to_show, indent=2))
        return True
    elif status in ['failed', 'error', 'failure', 'api_operation_status_failed', 'api_operation_status_error']:
        print("❌ Request failed!")
        print("Error details:")
        print(json.dumps(status_result, indent=2))
        return False
    elif status in ['running', 'processing', 'in_progress', 'pending', 'submitted', 'queued', 'api_operation_status_pending']:
        print("⏳ Request is still in progress...")
        print("Full status details:")
        print(json.dumps(status_result, indent=2))
        return True
    else:
        print(f"⚠️ Request has status: {status}")
        print("Full status details:")
        print(json.dumps(status_result, indent=2))
        return True


def wait_for_completion(profile_creds, request_id, timeout_minutes=10):
    """Poll the status endpoint until completion or timeout."""
    timeout_seconds = timeout_minutes * 60
    start_time = time.time()
    last_status = None
    progress_shown = False

    while time.time() - start_time < timeout_seconds:
        status_result = check_request_status(profile_creds, request_id)

        if status_result is None:
            print("Failed to check status, retrying in 1 second...")
            time.sleep(1)
            continue

        # Try different possible status field names
        status = (status_result.get('status') or
                 status_result.get('state') or
                 status_result.get('jobStatus') or
                 status_result.get('requestStatus') or
                 status_result.get('apiStatus') or '').lower()

        # Only print status if it changed or it's the first time
        if status != last_status:
            print(f"Status: {status}")
            last_status = status

        if status in ['completed', 'success', 'finished', 'done', 'succeed', 'api_operation_status_success']:
            print("✅ Command completed successfully!")

            # Only show result if it's not empty
            result_to_show = status_result.get('apiResponse', status_result)
            if result_to_show and result_to_show != {}:
                print("Final Result:")
                print(json.dumps(result_to_show, indent=2))
            return True
        elif status in ['failed', 'error', 'failure', 'api_operation_status_failed', 'api_operation_status_error']:
            print("❌ Command failed!")
            print("Error details:")
            print(json.dumps(status_result, indent=2))
            return False
        elif status in ['running', 'processing', 'in_progress', 'pending', 'submitted', 'queued', 'api_operation_status_pending']:
            if not progress_shown:
                print("⏳ Request is in progress...")
                progress_shown = True
            time.sleep(1)
        else:
            if not progress_shown:
                print(f"⏳ Request status is '{status}', monitoring progress...")
                progress_shown = True
            time.sleep(1)

    print(f"⏰ Timeout reached after {timeout_minutes} minutes")
    print(f"You can check the status later using: onehouse-cli --check-status {request_id} --profile {profile_creds.get('name', 'your-profile')}")
    return False


def execute_command(profile_creds, command, timeout_minutes=10):
    """Execute a command against the Onehouse API and wait for completion."""
    api_endpoint = profile_creds.get('api_endpoint', 'https://api.onehouse.ai')
    url = f"{api_endpoint}/v1/resource/"

    headers = {
        'x-onehouse-account-uid': profile_creds['account_uid'],
        'x-onehouse-project-uid': profile_creds['project_uid'],
        'x-onehouse-api-key': profile_creds['api_key'],
        'x-onehouse-api-secret': profile_creds['api_secret'],
        'Content-Type': 'application/json',
        'x-onehouse-region': profile_creds['project_region'],
        'x-onehouse-uuid': profile_creds['user_id']
    }

    # Add required request_id header
    headers['x-onehouse-link-uid'] = profile_creds['request_id']

    payload = {
        "statement": command
    }

    try:
        print(f"Executing command: {command}")
        print("Making API request...")

        response = requests.post(url, headers=headers, json=payload)

        print(f"Response Status: {response.status_code}")

        if response.status_code == 200:
            try:
                result = response.json()
                print("Initial Response:")
                print(json.dumps(result, indent=2))

                # Extract request ID from response if available
                async_request_id = result.get('requestId') or result.get('request_id') or result.get('id')

                if async_request_id:
                    print(f"Request ID: {async_request_id}")
                    return wait_for_completion(profile_creds, async_request_id, timeout_minutes)
                else:
                    print("No request ID found in response - command may have completed immediately")
                    return True

            except json.JSONDecodeError:
                print("Response (raw text):")
                print(response.text)
                return True
        else:
            print("Error Response:")
            print(f"Status Code: {response.status_code}")
            print("Headers:")
            for header, value in response.headers.items():
                print(f"  {header}: {value}")
            print("Body:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except json.JSONDecodeError:
                print(response.text if response.text else "(empty)")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False


def list_profiles(credentials):
    """List all available profiles."""
    if not credentials:
        print("No profiles found.")
        return

    default_profile = credentials.get('_default', None)

    print("Available profiles:")
    for profile_name, profile_data in credentials.items():
        # Skip the _default entry
        if profile_name == '_default':
            continue

        account_uid = profile_data.get('account_uid', 'N/A')
        project_uid = profile_data.get('project_uid', 'N/A')
        region = profile_data.get('project_region', 'N/A')
        environment = profile_data.get('environment', 'production')

        default_indicator = " (default)" if profile_name == default_profile else ""
        print(f"  - {profile_name}{default_indicator}")
        print(f"    Account: {account_uid}")
        print(f"    Project: {project_uid}")
        print(f"    Region: {region}")
        print(f"    Environment: {environment}")
        print()


def main():
    """Main function to run the CLI tool."""
    parser = argparse.ArgumentParser(
        description='Execute SQL commands against Onehouse API',
        epilog='Examples:\n'
               '  Execute command: onehouse-cli --command "ALTER OCU SET LIMIT = \'3\'" --profile myprofile\n'
               '  Check status: onehouse-cli --check-status REQUEST_ID --profile myprofile',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--command', '-c',
        type=str,
        help='SQL command to execute (backticks around job IDs will be preserved automatically)'
    )

    parser.add_argument(
        '--profile', '-p',
        type=str,
        help='Profile name to use for authentication (uses default if not specified)'
    )

    parser.add_argument(
        '--list-profiles', '-l',
        action='store_true',
        help='List all available profiles'
    )

    parser.add_argument(
        '--timeout', '-t',
        type=int,
        default=10,
        help='Timeout in minutes for command completion (default: 10)'
    )

    parser.add_argument(
        '--check-status',
        type=str,
        help='Check the status of an existing request by providing its request ID'
    )

    args = parser.parse_args()

    # Load credentials
    credentials = load_credentials()
    if not credentials:
        return 1

    # List profiles if requested
    if args.list_profiles:
        list_profiles(credentials)
        return 0

    # Handle check-status if requested
    if args.check_status:
        # Handle profile selection for status check
        profile_name = args.profile
        if not profile_name:
            # Check if there's a default profile set
            if '_default' in credentials:
                profile_name = credentials['_default']
                print(f"Using default profile: {profile_name}")
            else:
                print("Error: --profile is required for status check")
                print("\nUse --list-profiles to see available profiles")
                print("Or run 'onehouse-cli-configure' to set up a default profile")
                return 1

        # Get profile credentials
        profile_creds = get_profile_credentials(credentials, profile_name)
        if not profile_creds:
            return 1

        # Store profile name for better error messages
        profile_creds['name'] = profile_name

        # Check status asynchronously
        success = check_status_async(profile_creds, args.check_status)
        return 0 if success else 1

    # Validate required arguments for command execution
    if not args.command:
        print("Error: --command is required (unless using --check-status)")
        parser.print_help()
        return 1

    # Handle profile selection
    profile_name = args.profile
    if not profile_name:
        # Check if there's a default profile set
        if '_default' in credentials:
            profile_name = credentials['_default']
            print(f"Using default profile: {profile_name}")
        else:
            print("Error: --profile is required")
            print("\nUse --list-profiles to see available profiles")
            print("Or run 'onehouse-cli-configure' to set up a default profile")
            return 1

    # Get profile credentials
    profile_creds = get_profile_credentials(credentials, profile_name)
    if not profile_creds:
        return 1

    # Store profile name for better error messages
    profile_creds['name'] = profile_name

    # Execute the command
    success = execute_command(profile_creds, args.command, args.timeout)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

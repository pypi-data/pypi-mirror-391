"""
Onehouse CLI Configuration Tool
Collects and stores Onehouse API credentials for future use.
"""

import os
import json
import getpass
from pathlib import Path


def get_user_input(prompt, secure=False):
    """Get input from user with optional secure input for secrets."""
    if secure:
        return getpass.getpass(prompt)
    return input(prompt).strip()


def create_config_directory():
    """Create the ~/.onehouse directory if it doesn't exist."""
    config_dir = Path.home() / ".onehouse"
    config_dir.mkdir(exist_ok=True)
    return config_dir


def load_existing_credentials():
    """Load existing credentials file or return empty dict."""
    credentials_file = Path.home() / ".onehouse" / "credentials"
    if credentials_file.exists():
        try:
            with open(credentials_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_credentials(credentials):
    """Save credentials to ~/.onehouse/credentials file."""
    config_dir = create_config_directory()
    credentials_file = config_dir / "credentials"

    with open(credentials_file, 'w') as f:
        json.dump(credentials, f, indent=2)

    # Set restrictive permissions (readable only by owner)
    os.chmod(credentials_file, 0o600)


def collect_credentials():
    """Collect all required credentials from user."""
    print("Onehouse CLI Configuration")
    print("=" * 30)
    print("Please provide your Onehouse API credentials:")
    print()

    credentials = {}

    # Profile name
    profile_name = get_user_input("Profile name: ")
    if not profile_name:
        print("Error: Profile name is required")
        return None

    # Load existing credentials to check if profile exists
    existing_credentials = load_existing_credentials()
    existing_profile = existing_credentials.get(profile_name, {})

    if profile_name in existing_credentials:
        print(f"\n⚠️  Profile '{profile_name}' already exists:")
        print(f"    Account: {existing_profile.get('account_uid', 'N/A')}")
        print(f"    Project: {existing_profile.get('project_uid', 'N/A')}")
        print(f"    Region: {existing_profile.get('project_region', 'N/A')}")
        print(f"    Environment: {existing_profile.get('environment', 'production')}")

        # Show API Key/Secret previews in the summary
        existing_key = existing_profile.get('api_key', '')
        existing_secret = existing_profile.get('api_secret', '')
        key_preview = existing_key[:4] + '...' if len(existing_key) > 4 else existing_key
        secret_preview = existing_secret[:4] + '...' if len(existing_secret) > 4 else existing_secret
        if existing_key:
            print(f"    API Key: {key_preview}")
        if existing_secret:
            print(f"    API Secret: {secret_preview}")

        print("\nPress Enter to keep existing values or enter new values:")

    # Account UID
    existing_account = existing_profile.get('account_uid', '')
    prompt = f"Account UID ({existing_account}): " if existing_account else "Account UID: "
    account_uid = get_user_input(prompt).strip()
    if not account_uid:
        if existing_account:
            account_uid = existing_account
        else:
            print("Error: Account UID is required")
            return None

    # Project UID
    existing_project = existing_profile.get('project_uid', '')
    prompt = f"Project UID ({existing_project}): " if existing_project else "Project UID: "
    project_uid = get_user_input(prompt).strip()
    if not project_uid:
        if existing_project:
            project_uid = existing_project
        else:
            print("Error: Project UID is required")
            return None

    # API Key
    existing_key = existing_profile.get('api_key', '')
    key_preview = existing_key[:4] + '...' if len(existing_key) > 4 else existing_key
    prompt = f"API Key ({key_preview}) (input masked): " if existing_key else "API Key (input masked): "
    api_key = get_user_input(prompt, secure=True)
    if not api_key:
        if existing_key:
            api_key = existing_key
        else:
            print("Error: API Key is required")
            return None

    # API Secret
    existing_secret = existing_profile.get('api_secret', '')
    secret_preview = existing_secret[:4] + '...' if len(existing_secret) > 4 else existing_secret
    prompt = f"API Secret ({secret_preview}) (input masked): " if existing_secret else "API Secret (input masked): "
    api_secret = get_user_input(prompt, secure=True)
    if not api_secret:
        if existing_secret:
            api_secret = existing_secret
        else:
            print("Error: API Secret is required")
            return None

    # Project Region
    existing_region = existing_profile.get('project_region', '')
    prompt = f"Project Region ({existing_region}): " if existing_region else "Project Region: "
    project_region = get_user_input(prompt).strip()
    if not project_region:
        if existing_region:
            project_region = existing_region
        else:
            print("Error: Project Region is required")
            return None

    # User ID
    existing_user = existing_profile.get('user_id', '')
    prompt = f"User ID ({existing_user}): " if existing_user else "User ID: "
    user_id = get_user_input(prompt).strip()
    if not user_id:
        if existing_user:
            user_id = existing_user
        else:
            print("Error: User ID is required")
            return None

    # Request ID
    existing_request = existing_profile.get('request_id', '')
    prompt = f"Request ID ({existing_request}): " if existing_request else "Request ID: "
    request_id = get_user_input(prompt).strip()
    if not request_id:
        if existing_request:
            request_id = existing_request
        else:
            print("Error: Request ID is required")
            return None

    # Environment selection
    existing_env = existing_profile.get('environment', 'production')
    print()
    print("Environment Selection:")
    print("1. Production (api.onehouse.ai)")
    print("2. Staging (staging-api.onehouse.ai)")
    prompt = f"Choose environment (1 or 2) ({existing_env}): " if existing_env else "Choose environment (1 or 2): "
    env_choice = get_user_input(prompt).strip()

    if not env_choice and existing_env:
        environment = existing_env
        api_endpoint = existing_profile.get('api_endpoint',
                                          'https://staging-api.onehouse.ai' if existing_env == 'staging'
                                          else 'https://api.onehouse.ai')
    elif env_choice == "2":
        environment = "staging"
        api_endpoint = "https://staging-api.onehouse.ai"
    else:
        environment = "production"
        api_endpoint = "https://api.onehouse.ai"

    print(f"Selected: {environment} environment")

    credentials[profile_name] = {
        "account_uid": account_uid,
        "project_uid": project_uid,
        "api_key": api_key,
        "api_secret": api_secret,
        "project_region": project_region,
        "user_id": user_id,
        "request_id": request_id,
        "environment": environment,
        "api_endpoint": api_endpoint
    }

    # Ask if this should be the default profile
    print()
    set_as_default = get_user_input("Set this as the default profile? (y/n): ").strip().lower()
    if set_as_default in ['y', 'yes']:
        credentials['_default'] = profile_name

    return credentials, profile_name


def is_already_in_shell_profile():
    """Check if onehouse-cli is already added to shell profile."""
    cli_dir = Path(__file__).parent.absolute()

    # Detect shell and profile file
    shell_profiles = [
        Path.home() / ".zshrc",
        Path.home() / ".bashrc",
        Path.home() / ".bash_profile"
    ]

    for profile_file in shell_profiles:
        if profile_file.exists():
            try:
                with open(profile_file, 'r') as f:
                    content = f.read()
                    if str(cli_dir) in content and "onehouse-cli" in content:
                        return True
            except IOError:
                pass

    return False


def add_to_shell_profile():
    """Add onehouse-cli tools to the user's shell profile."""
    import subprocess

    # Get the directory where the CLI tools are located
    cli_dir = Path(__file__).parent.absolute()
    path_export = f'export PATH="{cli_dir}:$PATH"'

    # Detect shell and profile file
    shell_profiles = [
        Path.home() / ".zshrc",
        Path.home() / ".bashrc",
        Path.home() / ".bash_profile"
    ]

    profile_file = None
    for profile in shell_profiles:
        if profile.exists():
            profile_file = profile
            break

    if not profile_file:
        print("Could not find shell profile file (.zshrc, .bashrc, .bash_profile)")
        print(f"Manually add this to your shell profile: {path_export}")
        return

    # Check if already added
    try:
        with open(profile_file, 'r') as f:
            content = f.read()
            if str(cli_dir) in content and "onehouse-cli" in content:
                print(f"✓ Already added to {profile_file}")
                return
    except IOError:
        pass

    # Add to profile
    try:
        with open(profile_file, 'a') as f:
            f.write(f"\n# Add onehouse-cli tools to PATH\n{path_export}\n")
        print(f"✓ Added to {profile_file}")
        print("Please run 'source ~/.zshrc' (or your shell profile) to apply changes")
    except IOError as e:
        print(f"Failed to write to {profile_file}: {e}")
        print(f"Manually add this to your shell profile: {path_export}")


def main():
    """Main function to run the configuration tool."""
    try:
        # Load existing credentials
        existing_credentials = load_existing_credentials()

        # Collect new credentials
        result = collect_credentials()
        if not result:
            return 1

        new_credentials, profile_name = result

        # Merge with existing credentials
        existing_credentials.update(new_credentials)

        # Save credentials
        save_credentials(existing_credentials)

        print()
        print(f"✓ Profile '{profile_name}' configured successfully!")
        print(f"Credentials saved to: {Path.home() / '.onehouse' / 'credentials'}")
        print()

        # Check if already in shell profile, only ask if not already added
        if is_already_in_shell_profile():
            print("✓ onehouse-cli tools already in shell PATH")
        else:
            add_to_profile = input("Add onehouse-cli tools to your shell PATH? (y/n): ").strip().lower()
            if add_to_profile in ['y', 'yes']:
                add_to_shell_profile()

        print("You can now use this profile with future Onehouse CLI commands.")

        return 0

    except KeyboardInterrupt:
        print("\n\nConfiguration cancelled.")
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

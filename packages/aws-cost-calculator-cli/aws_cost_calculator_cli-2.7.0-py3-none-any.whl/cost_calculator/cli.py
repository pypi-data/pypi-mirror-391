#!/usr/bin/env python3
"""
AWS Cost Calculator CLI

Usage:
    cc --profile myprofile
    cc --profile myprofile --start-date 2025-11-04
    cc --profile myprofile --offset 2 --window 30
"""

import click
import boto3
import json
import os
import platform
from datetime import datetime, timedelta
from pathlib import Path
from cost_calculator.trends import format_trends_markdown
from cost_calculator.monthly import format_monthly_markdown
from cost_calculator.drill import format_drill_down_markdown

# API Configuration - can be overridden via environment variable
API_BASE_URL = os.environ.get(
    'COST_CALCULATOR_API_URL',
    'https://api.costcop.cloudfix.dev'
)
# Legacy profiles URL for backward compatibility
PROFILES_API_URL = os.environ.get(
    'COST_CALCULATOR_PROFILES_URL',
    f'{API_BASE_URL}/profiles'
)
from cost_calculator.executor import execute_trends, execute_monthly, execute_drill


def apply_auth_options(config, sso=None, access_key_id=None, secret_access_key=None, session_token=None):
    """Apply authentication options to profile config
    
    Args:
        config: Profile configuration dict
        sso: AWS SSO profile name
        access_key_id: AWS Access Key ID
        secret_access_key: AWS Secret Access Key
        session_token: AWS Session Token
    
    Returns:
        Updated config dict
    """
    import subprocess
    
    if sso:
        # SSO authentication - trigger login if needed
        try:
            # Test if SSO session is valid
            result = subprocess.run(
                ['aws', 'sts', 'get-caller-identity', '--profile', sso],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                if 'expired' in result.stderr.lower() or 'token' in result.stderr.lower():
                    click.echo(f"SSO session expired or not initialized. Logging in...")
                    subprocess.run(['aws', 'sso', 'login', '--profile', sso], check=True)
        except Exception as e:
            click.echo(f"Warning: Could not verify SSO session: {e}")
        
        config['aws_profile'] = sso
    elif access_key_id and secret_access_key:
        # Static credentials provided via CLI
        config['credentials'] = {
            'aws_access_key_id': access_key_id,
            'aws_secret_access_key': secret_access_key,
            'region': 'us-east-1'
        }
        if session_token:
            config['credentials']['aws_session_token'] = session_token
    
    return config


def get_api_secret():
    """Get API secret from config file or environment variable"""
    import os
    
    # Check environment variable first
    api_secret = os.environ.get('COST_API_SECRET')
    if api_secret:
        return api_secret
    
    # Check config file
    config_dir = Path.home() / '.config' / 'cost-calculator'
    config_file = config_dir / 'config.json'
    
    if config_file.exists():
        with open(config_file) as f:
            config = json.load(f)
            return config.get('api_secret')
    
    return None


def get_exclusions(profile_name=None):
    """Get exclusions configuration from DynamoDB API"""
    import requests
    
    api_secret = get_api_secret()
    if not api_secret:
        raise click.ClickException(
            "No API secret configured.\n"
            "Run: cc configure --api-secret YOUR_SECRET"
        )
    
    try:
        response = requests.post(
            PROFILES_API_URL,
            headers={'X-API-Secret': api_secret, 'Content-Type': 'application/json'},
            json={'operation': 'get_exclusions', 'profile_name': profile_name},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json().get('exclusions', {})
        else:
            # Return defaults if API fails
            return {
                'record_types': ['Tax', 'Support'],
                'services': [],
                'usage_types': [],
                'line_item_types': []
            }
    except:
        # Return defaults if request fails
        return {
            'record_types': ['Tax', 'Support'],
            'services': [],
            'usage_types': [],
            'line_item_types': []
        }


def build_exclusion_filter(exclusions):
    """Build AWS Cost Explorer filter from exclusions config"""
    filter_parts = []
    
    # Exclude record types (Tax, Support, etc.)
    if exclusions.get('record_types'):
        filter_parts.append({
            "Not": {
                "Dimensions": {
                    "Key": "RECORD_TYPE",
                    "Values": exclusions['record_types']
                }
            }
        })
    
    # Exclude specific services (OCBLateFee, etc.)
    if exclusions.get('services'):
        filter_parts.append({
            "Not": {
                "Dimensions": {
                    "Key": "SERVICE",
                    "Values": exclusions['services']
                }
            }
        })
    
    # Exclude usage types
    if exclusions.get('usage_types'):
        filter_parts.append({
            "Not": {
                "Dimensions": {
                    "Key": "USAGE_TYPE",
                    "Values": exclusions['usage_types']
                }
            }
        })
    
    # Exclude line item types (Refund, Credit, etc.)
    if exclusions.get('line_item_types'):
        filter_parts.append({
            "Not": {
                "Dimensions": {
                    "Key": "LINE_ITEM_TYPE",
                    "Values": exclusions['line_item_types']
                }
            }
        })
    
    return filter_parts


def load_profile(profile_name):
    """Load profile configuration from DynamoDB API (API-only, no local files)"""
    import requests
    
    # Get API secret
    api_secret = get_api_secret()
    
    if not api_secret:
        raise click.ClickException(
            "No API secret configured.\n"
            "Run: cc configure --api-secret YOUR_SECRET\n"
            "Or set environment variable: export COST_API_SECRET=YOUR_SECRET"
        )
    
    try:
        response = requests.post(
            PROFILES_API_URL,
            headers={'X-API-Secret': api_secret, 'Content-Type': 'application/json'},
            json={'operation': 'get', 'profile_name': profile_name},
            timeout=10
        )
        
        if response.status_code == 200:
            response_data = response.json()
            # API returns {"profile": {...}} wrapper
            profile_data = response_data.get('profile', response_data)
            profile = {
                'accounts': profile_data['accounts'],
                'profile_name': profile_name  # Store profile name for API calls
            }
            
            # If profile has aws_profile field, use it
            if 'aws_profile' in profile_data:
                profile['aws_profile'] = profile_data['aws_profile']
            # Check for AWS_PROFILE environment variable (SSO support)
            elif os.environ.get('AWS_PROFILE'):
                profile['aws_profile'] = os.environ['AWS_PROFILE']
            # Use environment credentials
            elif os.environ.get('AWS_ACCESS_KEY_ID'):
                profile['credentials'] = {
                    'aws_access_key_id': os.environ['AWS_ACCESS_KEY_ID'],
                    'aws_secret_access_key': os.environ['AWS_SECRET_ACCESS_KEY'],
                    'aws_session_token': os.environ.get('AWS_SESSION_TOKEN')
                }
            else:
                # Try to find a matching AWS profile by name
                # This allows "khoros" profile to work with "khoros_umbrella" AWS profile
                import subprocess
                try:
                    result = subprocess.run(
                        ['aws', 'configure', 'list-profiles'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        available_profiles = result.stdout.strip().split('\n')
                        # Try exact match first
                        if profile_name in available_profiles:
                            profile['aws_profile'] = profile_name
                        # Try with common suffixes
                        elif f"{profile_name}_umbrella" in available_profiles:
                            profile['aws_profile'] = f"{profile_name}_umbrella"
                        elif f"{profile_name}-umbrella" in available_profiles:
                            profile['aws_profile'] = f"{profile_name}-umbrella"
                        elif f"{profile_name}_prod" in available_profiles:
                            profile['aws_profile'] = f"{profile_name}_prod"
                        # If no match found, leave it unset - user must provide --sso
                except:
                    # If we can't list profiles, leave it unset - user must provide --sso
                    pass
            
            return profile
        else:
            raise click.ClickException(
                f"Profile '{profile_name}' not found in DynamoDB.\n"
                f"Run: cc profile create --name {profile_name} --accounts \"...\""
            )
    except requests.exceptions.RequestException as e:
        raise click.ClickException(
            f"Failed to fetch profile from API: {e}\n"
            "Check your API secret and network connection."
        )


def calculate_costs(profile_config, accounts, start_date, offset, window):
    """
    Calculate AWS costs for the specified period.
    
    Args:
        profile_config: Profile configuration (with aws_profile or credentials)
        accounts: List of AWS account IDs
        start_date: Start date (defaults to today)
        offset: Days to go back from start_date (default: 2)
        window: Number of days to analyze (default: 30)
    
    Returns:
        dict with cost breakdown
    """
    # Calculate date range
    if start_date:
        end_date = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        end_date = datetime.now()
    
    # Go back by offset days
    end_date = end_date - timedelta(days=offset)
    
    # Start date is window days before end_date
    start_date_calc = end_date - timedelta(days=window)
    
    # Format for API (end date is exclusive, so add 1 day)
    api_start = start_date_calc.strftime('%Y-%m-%d')
    api_end = (end_date + timedelta(days=1)).strftime('%Y-%m-%d')
    
    click.echo(f"Analyzing: {api_start} to {end_date.strftime('%Y-%m-%d')} ({window} days)")
    
    # Initialize boto3 client
    try:
        if 'aws_profile' in profile_config:
            # SSO-based authentication
            aws_profile = profile_config['aws_profile']
            click.echo(f"AWS Profile: {aws_profile} (SSO)")
            click.echo(f"Accounts: {len(accounts)}")
            click.echo("")
            session = boto3.Session(profile_name=aws_profile)
            ce_client = session.client('ce', region_name='us-east-1')
        else:
            # Static credentials
            creds = profile_config['credentials']
            click.echo(f"AWS Credentials: Static")
            click.echo(f"Accounts: {len(accounts)}")
            click.echo("")
            
            session_kwargs = {
                'aws_access_key_id': creds['aws_access_key_id'],
                'aws_secret_access_key': creds['aws_secret_access_key'],
                'region_name': creds.get('region', 'us-east-1')
            }
            
            if 'aws_session_token' in creds:
                session_kwargs['aws_session_token'] = creds['aws_session_token']
            
            session = boto3.Session(**session_kwargs)
            ce_client = session.client('ce')
            
    except Exception as e:
        if 'Token has expired' in str(e) or 'sso' in str(e).lower():
            if 'aws_profile' in profile_config:
                raise click.ClickException(
                    f"AWS SSO session expired or not initialized.\n"
                    f"Run: aws sso login --profile {profile_config['aws_profile']}"
                )
            else:
                raise click.ClickException(
                    f"AWS credentials expired.\n"
                    f"Run: cc configure --profile <profile_name>"
                )
        raise
    
    # Build filter with dynamic exclusions
    exclusions = get_exclusions()  # Get from DynamoDB
    exclusion_filters = build_exclusion_filter(exclusions)
    
    cost_filter = {
        "And": [
            {
                "Dimensions": {
                    "Key": "LINKED_ACCOUNT",
                    "Values": accounts
                }
            },
            {
                "Dimensions": {
                    "Key": "BILLING_ENTITY",
                    "Values": ["AWS"]
                }
            }
        ]
    }
    
    # Add dynamic exclusion filters
    cost_filter["And"].extend(exclusion_filters)
    
    # Get daily costs
    click.echo("Fetching cost data...")
    try:
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': api_start,
                'End': api_end
            },
            Granularity='DAILY',
            Metrics=['NetAmortizedCost'],
            Filter=cost_filter
        )
    except Exception as e:
        if 'Token has expired' in str(e) or 'expired' in str(e).lower():
            raise click.ClickException(
                f"AWS SSO session expired.\n"
                f"Run: aws sso login --profile {aws_profile}"
            )
        raise
    
    # Calculate total
    total_cost = sum(
        float(day['Total']['NetAmortizedCost']['Amount'])
        for day in response['ResultsByTime']
    )
    
    # Get support cost from the 1st of the month containing the end date
    # Support is charged on the 1st of each month for the previous month's usage
    # For Oct 3-Nov 2 analysis, we get support from Nov 1 (which is October's support)
    support_month_date = end_date.replace(day=1)
    support_date_str = support_month_date.strftime('%Y-%m-%d')
    support_date_end = (support_month_date + timedelta(days=1)).strftime('%Y-%m-%d')
    
    click.echo("Fetching support costs...")
    support_response = ce_client.get_cost_and_usage(
        TimePeriod={
            'Start': support_date_str,
            'End': support_date_end
        },
        Granularity='DAILY',
        Metrics=['NetAmortizedCost'],
        Filter={
            "And": [
                {
                    "Dimensions": {
                        "Key": "LINKED_ACCOUNT",
                        "Values": accounts
                    }
                },
                {
                    "Dimensions": {
                        "Key": "RECORD_TYPE",
                        "Values": ["Support"]
                    }
                }
            ]
        }
    )
    
    support_cost = float(support_response['ResultsByTime'][0]['Total']['NetAmortizedCost']['Amount'])
    
    # Calculate days in the month that the support covers
    # Support on Nov 1 covers October (31 days)
    support_month = support_month_date - timedelta(days=1)  # Go back to previous month
    import calendar
    days_in_support_month = calendar.monthrange(support_month.year, support_month.month)[1]
    
    # Support allocation: divide by 2 (50% allocation), then by days in month
    support_per_day = (support_cost / 2) / days_in_support_month
    
    # Calculate daily rate
    # NOTE: We divide operational by window, but support by days_in_support_month
    # This matches the console's calculation method
    daily_operational = total_cost / days_in_support_month  # Use 31 for October, not 30
    daily_total = daily_operational + support_per_day
    
    # Annual projection
    annual = daily_total * 365
    
    return {
        'period': {
            'start': api_start,
            'end': end_date.strftime('%Y-%m-%d'),
            'days': window
        },
        'costs': {
            'total_operational': total_cost,
            'daily_operational': daily_operational,
            'support_month': support_cost,
            'support_per_day': support_per_day,
            'daily_total': daily_total,
            'annual_projection': annual
        }
    }


@click.group()
def cli():
    """
    AWS Cost Calculator - Calculate daily and annual AWS costs
    
    \b
    Two authentication methods:
    1. AWS SSO (recommended for interactive use)
    2. Static credentials (for automation/CI)
    
    \b
    Quick Start:
      # SSO Method
      aws sso login --profile my_aws_profile
      cc init --profile myprofile --aws-profile my_aws_profile --accounts "123,456,789"
      cc calculate --profile myprofile
    
      # Static Credentials Method
      cc init --profile myprofile --aws-profile dummy --accounts "123,456,789"
      cc configure --profile myprofile
      cc calculate --profile myprofile
    
    \b
    For detailed documentation, see:
      - COST_CALCULATION_METHODOLOGY.md
      - README.md
    """
    pass


@cli.command('setup-cur')
@click.option('--database', required=True, prompt='CUR Athena Database', help='Athena database name for CUR')
@click.option('--table', required=True, prompt='CUR Table Name', help='CUR table name')
@click.option('--s3-output', required=True, prompt='S3 Output Location', help='S3 bucket for Athena query results')
def setup_cur(database, table, s3_output):
    """
    Configure CUR (Cost and Usage Report) settings for resource-level queries
    
    Saves CUR configuration to ~/.config/cost-calculator/cur_config.json
    
    Example:
      cc setup-cur --database my_cur_db --table cur_table --s3-output s3://my-bucket/
    """
    import json
    
    config_dir = Path.home() / '.config' / 'cost-calculator'
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config_file = config_dir / 'cur_config.json'
    
    config = {
        'database': database,
        'table': table,
        's3_output': s3_output
    }
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    click.echo(f"✓ CUR configuration saved to {config_file}")
    click.echo(f"  Database: {database}")
    click.echo(f"  Table: {table}")
    click.echo(f"  S3 Output: {s3_output}")
    click.echo("")
    click.echo("You can now use: cc drill --service 'EC2 - Other' --resources")


@cli.command('setup-api')
@click.option('--api-secret', required=True, prompt=True, hide_input=True, help='COST_API_SECRET value')
def setup_api(api_secret):
    """
    Configure COST_API_SECRET for backend API access
    
    Saves the API secret to the appropriate location based on your OS:
    - Mac/Linux: ~/.zshrc or ~/.bashrc
    - Windows: User environment variables
    
    Example:
      cc setup-api --api-secret your-secret-here
      
    Or let it prompt you (input will be hidden):
      cc setup-api
    """
    system = platform.system()
    
    if system == "Windows":
        # Windows: Set user environment variable
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, 'COST_API_SECRET', 0, winreg.REG_SZ, api_secret)
            winreg.CloseKey(key)
            click.echo("✓ COST_API_SECRET saved to Windows user environment variables")
            click.echo("  Please restart your terminal for changes to take effect")
        except Exception as e:
            click.echo(f"✗ Error setting Windows environment variable: {e}", err=True)
            click.echo("\nManual setup:")
            click.echo("1. Open System Properties > Environment Variables")
            click.echo("2. Add new User variable:")
            click.echo("   Name: COST_API_SECRET")
            click.echo(f"   Value: {api_secret}")
            return
    else:
        # Mac/Linux: Add to shell profile
        shell = os.environ.get('SHELL', '/bin/bash')
        
        if 'zsh' in shell:
            profile_file = Path.home() / '.zshrc'
        else:
            profile_file = Path.home() / '.bashrc'
        
        # Check if already exists
        export_line = f'export COST_API_SECRET="{api_secret}"'
        
        try:
            if profile_file.exists():
                content = profile_file.read_text()
                if 'COST_API_SECRET' in content:
                    # Replace existing
                    lines = content.split('\n')
                    new_lines = []
                    for line in lines:
                        if 'COST_API_SECRET' in line and line.strip().startswith('export'):
                            new_lines.append(export_line)
                        else:
                            new_lines.append(line)
                    profile_file.write_text('\n'.join(new_lines))
                    click.echo(f"✓ Updated COST_API_SECRET in {profile_file}")
                else:
                    # Append
                    with profile_file.open('a') as f:
                        f.write(f'\n# AWS Cost Calculator API Secret\n{export_line}\n')
                    click.echo(f"✓ Added COST_API_SECRET to {profile_file}")
            else:
                # Create new file
                profile_file.write_text(f'# AWS Cost Calculator API Secret\n{export_line}\n')
                click.echo(f"✓ Created {profile_file} with COST_API_SECRET")
            
            # Also set for current session
            os.environ['COST_API_SECRET'] = api_secret
            click.echo(f"✓ Set COST_API_SECRET for current session")
            click.echo(f"\nTo use in new terminals, run: source {profile_file}")
            
        except Exception as e:
            click.echo(f"✗ Error writing to {profile_file}: {e}", err=True)
            click.echo(f"\nManual setup: Add this line to {profile_file}:")
            click.echo(f"  {export_line}")
            return


@cli.command()
@click.option('--profile', required=True, help='Profile name (e.g., myprofile)')
@click.option('--start-date', help='Start date (YYYY-MM-DD, default: today)')
@click.option('--offset', default=2, help='Days to go back from start date (default: 2)')
@click.option('--window', default=30, help='Number of days to analyze (default: 30)')
@click.option('--json-output', is_flag=True, help='Output as JSON')
@click.option('--sso', help='AWS SSO profile name (e.g., my_sso_profile)')
@click.option('--access-key-id', help='AWS Access Key ID (for static credentials)')
@click.option('--secret-access-key', help='AWS Secret Access Key (for static credentials)')
@click.option('--session-token', help='AWS Session Token (for static credentials)')
def calculate(profile, start_date, offset, window, json_output, sso, access_key_id, secret_access_key, session_token):
    """
    Calculate AWS costs with daily rate and annual projection.
    
    This is the core cost calculation command that analyzes operational costs
    over a specified period and projects annual spending. It queries AWS Cost
    Explorer for all accounts in the profile, applies exclusions, and calculates
    both daily operational costs and allocated support costs.
    
    \b
    KEY FEATURES:
    • Operational cost analysis over configurable window
    • Support cost allocation (50% of monthly support ÷ days)
    • Daily rate calculation (operational + support per day)
    • Annual projection (daily rate × 365)
    • Automatic exclusions (Tax, Support calculated separately)
    • JSON output for programmatic use
    
    \b
    HOW IT WORKS:
    1. Loads profile from backend (accounts, exclusions, config)
    2. Queries Cost Explorer for operational costs in date range
    3. Queries Cost Explorer for support costs in the analysis month
    4. Calculates daily operational cost (total ÷ window days)
    5. Calculates support per day (monthly support ÷ 2 ÷ days in month)
    6. Computes daily rate (operational + support)
    7. Projects annual cost (daily rate × 365)
    
    \b
    DATE RANGE:
    • start-date: Starting point (default: today)
    • offset: Days back from start-date (default: 2 = T-2)
    • window: Number of days to analyze (default: 30)
    • Actual range: (start-date - offset - window) to (start-date - offset)
    
    Example: If today is Nov 12, 2025:
      - Default (offset=2, window=30): Oct 11 to Nov 10 (30 days)
      - Custom (offset=0, window=60): Sep 13 to Nov 12 (60 days)
    
    \b
    WHEN TO USE:
    • Daily cost monitoring and budgeting
    • Quick cost check for specific period
    • Annual cost projections
    • Baseline cost calculations
    • Automated cost reporting (with --json-output)
    
    \b
    AUTHENTICATION:
    Three methods supported (in order of preference):
    
    1. SSO (Recommended):
        cc calculate --profile myprofile --sso my_sso_profile
    
    2. Static Credentials:
        cc calculate --profile myprofile \\
            --access-key-id ASIA... \\
            --secret-access-key ... \\
            --session-token ...
    
    3. Environment Variables:
        export AWS_PROFILE=my_sso_profile
        cc calculate --profile myprofile
    
    \b
    EXAMPLES:
    
    Basic usage - last 30 days:
        cc calculate --profile khoros --sso khoros_umbrella
    
    Specific date range:
        cc calculate --profile khoros --sso khoros_umbrella \\
            --start-date 2025-10-01 --window 30
    
    Last 60 days:
        cc calculate --profile khoros --sso khoros_umbrella --window 60
    
    JSON output for automation:
        cc calculate --profile khoros --sso khoros_umbrella --json-output
    
    No offset (include today):
        cc calculate --profile khoros --sso khoros_umbrella --offset 0
    
    \b
    OUTPUT:
    Human-readable format shows:
    • Period analyzed (start/end dates, days)
    • Total operational cost
    • Daily operational cost
    • Support cost (monthly and per day)
    • Daily rate (operational + support)
    • Annual projection
    
    JSON format includes:
    • period: {start, end, days}
    • costs: {total_operational, daily_operational, support_month, 
             support_per_day, daily_total, annual_projection}
    • accounts: [list of account IDs]
    • exclusions: [list of excluded services]
    
    \b
    NOTES:
    • Requires AWS credentials with Cost Explorer read access
    • Profile must exist in backend DynamoDB
    • Support cost is allocated at 50% (÷2) per AWS best practices
    • Uses Net Amortized Cost metric
    • Excludes marketplace charges (AWS billing entity only)
    • T-2 offset recommended to avoid incomplete recent data
    
    \b
    SEE ALSO:
    • cc trends - For week-over-week cost analysis
    • cc monthly - For month-over-month comparisons
    • cc daily-report - For detailed daily breakdowns
    • cc info calculate - For more detailed help
    """
    
    # Load profile configuration
    config = load_profile(profile)
    
    # Apply authentication options
    config = apply_auth_options(config, sso, access_key_id, secret_access_key, session_token)
    
    # Calculate costs
    result = calculate_costs(
        profile_config=config,
        accounts=config['accounts'],
        start_date=start_date,
        offset=offset,
        window=window
    )
    
    if json_output:
        click.echo(json.dumps(result, indent=2))
    else:
        # Pretty print results
        click.echo("=" * 60)
        click.echo(f"Period: {result['period']['start']} to {result['period']['end']}")
        click.echo(f"Days analyzed: {result['period']['days']}")
        click.echo("=" * 60)
        click.echo(f"Total operational cost: ${result['costs']['total_operational']:,.2f}")
        click.echo(f"Daily operational: ${result['costs']['daily_operational']:,.2f}")
        click.echo(f"Support (month): ${result['costs']['support_month']:,.2f}")
        click.echo(f"Support per day (÷2÷days): ${result['costs']['support_per_day']:,.2f}")
        click.echo("=" * 60)
        click.echo(f"DAILY RATE: ${result['costs']['daily_total']:,.2f}")
        click.echo(f"ANNUAL PROJECTION: ${result['costs']['annual_projection']:,.0f}")
        click.echo("=" * 60)


# init command removed - use backend API via 'cc profile create' instead


@cli.command()
def list_profiles():
    """List all profiles from backend API (no local caching)"""
    import requests
    
    api_secret = get_api_secret()
    if not api_secret:
        click.echo("No API secret configured.")
        click.echo("Run: cc configure --api-secret YOUR_SECRET")
        return
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/profiles",
            headers={'X-API-Secret': api_secret, 'Content-Type': 'application/json'},
            json={'operation': 'list'},
            timeout=10
        )
        
        if response.status_code != 200:
            click.echo(f"Error: {response.status_code} - {response.text}")
            return
        
        result = response.json()
        profiles = result.get('profiles', [])
        
        if not profiles:
            click.echo("No profiles found in backend.")
            click.echo("Contact admin to create profiles in DynamoDB.")
            return
        
        click.echo("Profiles (from backend API):")
        click.echo("")
        for profile in profiles:
            # Each profile is a dict, extract the profile_name
            if isinstance(profile, dict):
                name = profile.get('profile_name', 'unknown')
                # Skip exclusions entries
                if not name.startswith('exclusions:'):
                    accounts = profile.get('accounts', [])
                    click.echo(f"  {name}")
                    click.echo(f"    Accounts: {len(accounts)}")
                    click.echo("")
            else:
                click.echo(f"  {profile}")
        click.echo(f"Total: {len([p for p in profiles if isinstance(p, dict) and not p.get('profile_name', '').startswith('exclusions:')])} profile(s)")
        
    except Exception as e:
        click.echo(f"Error loading profiles: {e}")


# setup command removed - profiles are managed in DynamoDB backend only


@cli.command()
@click.option('--api-secret', help='API secret for DynamoDB profile access')
@click.option('--show', is_flag=True, help='Show current configuration')
def configure(api_secret, show):
    """
    Configure Cost Calculator CLI settings.
    
    This tool requires an API secret to access profiles stored in DynamoDB.
    The secret can be configured here or set via COST_API_SECRET environment variable.
    
    Examples:
        # Configure API secret
        cc configure --api-secret YOUR_SECRET_KEY
        
        # Show current configuration
        cc configure --show
        
        # Use environment variable instead (no configuration needed)
        export COST_API_SECRET=YOUR_SECRET_KEY
    """
    import os
    
    config_dir = Path.home() / '.config' / 'cost-calculator'
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / 'config.json'
    
    if show:
        # Show current configuration
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
                if 'api_secret' in config:
                    masked_secret = config['api_secret'][:8] + '...' + config['api_secret'][-4:]
                    click.echo(f"API Secret: {masked_secret} (configured)")
                else:
                    click.echo("API Secret: Not configured")
        else:
            click.echo("No configuration file found")
        
        # Check environment variable
        import os
        if os.environ.get('COST_API_SECRET'):
            click.echo("Environment: COST_API_SECRET is set")
        else:
            click.echo("Environment: COST_API_SECRET is not set")
        
        return
    
    if not api_secret:
        raise click.ClickException(
            "Please provide --api-secret or use --show to view current configuration\n"
            "Example: cc configure --api-secret YOUR_SECRET_KEY"
        )
    
    # Load existing config
    config = {}
    if config_file.exists():
        with open(config_file) as f:
            config = json.load(f)
    
    # Update API secret
    config['api_secret'] = api_secret
    
    # Save config
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Set restrictive permissions (Unix/Mac only - Windows uses different permission model)
    import platform
    if platform.system() != 'Windows':
        os.chmod(config_file, 0o600)
    
    masked_secret = api_secret[:8] + '...' + api_secret[-4:]
    click.echo(f"✓ API secret configured: {masked_secret}")
    click.echo(f"\nYou can now run: cc calculate --profile PROFILE_NAME")
    click.echo(f"\nNote: Profiles are stored in DynamoDB and accessed via the API.")

@cli.command()
@click.option('--profile', required=True, help='Profile name')
@click.option('--weeks', default=3, help='Number of weeks to analyze (default: 3)')
@click.option('--output', default='cost_trends.md', help='Output markdown file (default: cost_trends.md)')
@click.option('--json-output', is_flag=True, help='Output as JSON')
@click.option('--sso', help='AWS SSO profile name')
@click.option('--access-key-id', help='AWS Access Key ID')
@click.option('--secret-access-key', help='AWS Secret Access Key')
@click.option('--session-token', help='AWS Session Token')
def trends(profile, weeks, output, json_output, sso, access_key_id, secret_access_key, session_token):
    """
    Analyze cost trends with Week-over-Week and Trailing 30-Day comparisons.
    
    This command identifies cost changes by comparing consecutive weeks (WoW) and
    comparing each week to the same week 4 weeks ago (T-30). Perfect for catching
    both immediate spikes and sustained trends across services.
    
    \b
    KEY FEATURES:
    • Week-over-Week (WoW) comparisons - catch immediate changes
    • Trailing 30-Day (T-30) comparisons - filter noise, see sustained trends
    • Service-level aggregation (not usage types)
    • Top 10 increases and decreases per comparison
    • Automatic filtering (>$10 and >5% changes)
    • Markdown report generation
    • JSON output for automation
    
    \b
    HOW IT WORKS:
    1. Divides analysis period into weeks (Sunday-Saturday)
    2. Queries Cost Explorer for each week's costs by service
    3. Compares consecutive weeks (Week N vs Week N-1) for WoW
    4. Compares each week to 4 weeks prior (Week N vs Week N-4) for T-30
    5. Identifies top 10 increases and decreases for each comparison
    6. Generates markdown report with tables and summaries
    
    \b
    COMPARISON TYPES:
    
    Week-over-Week (WoW):
    • Compares each week to the previous week
    • Good for: Catching immediate spikes, recent changes
    • Example: Week of Nov 3 vs Week of Oct 27
    
    Trailing 30-Day (T-30):
    • Compares each week to the same week 4 weeks ago
    • Good for: Filtering noise, seeing sustained trends
    • Example: Week of Nov 3 vs Week of Oct 6
    
    \b
    WHEN TO USE:
    • Weekly cost monitoring and reporting
    • Identifying cost anomalies and spikes
    • Tracking service-level cost changes
    • Finding sustained cost trends vs one-time spikes
    • Generating executive summaries
    
    \b
    EXAMPLES:
    
    Basic usage - last 3 weeks:
        cc trends --profile khoros --sso khoros_umbrella
    
    Analyze more weeks:
        cc trends --profile khoros --sso khoros_umbrella --weeks 8
    
    Custom output file:
        cc trends --profile khoros --sso khoros_umbrella \\
            --output weekly_analysis.md
    
    JSON output for automation:
        cc trends --profile khoros --sso khoros_umbrella --json-output
    
    \b
    OUTPUT:
    Markdown report includes:
    • Summary of each comparison period
    • Tables of top 10 increases and decreases
    • Service name, previous cost, current cost, change amount, change %
    • Total row summing top 10 changes
    • Filtered to show only significant changes (>$10 and >5%)
    
    Console output shows:
    • Summary of increases/decreases per comparison
    • Top service changes
    • Report file location
    
    \b
    FILTERING:
    Changes must meet BOTH criteria to appear:
    • Absolute change > $10
    • Percentage change > 5%
    
    This filters out:
    • Tiny dollar amounts with high percentages
    • Large amounts with negligible percentage changes
    
    \b
    NOTES:
    • Weeks run Sunday-Saturday
    • Requires at least 2 weeks of data
    • T-30 comparisons require at least 5 weeks
    • Service costs are aggregated (all usage types combined)
    • Uses same exclusions as calculate command
    • Report saved to current directory by default
    
    \b
    SEE ALSO:
    • cc monthly - For month-over-month analysis
    • cc drill - To investigate specific service changes
    • cc trends-detailed - For custom granularity and date ranges
    • cc calculate - For overall cost calculations
    """
    
    # Load profile configuration
    config = load_profile(profile)
    config = apply_auth_options(config, sso, access_key_id, secret_access_key, session_token)
    
    click.echo(f"Analyzing last {weeks} weeks...")
    click.echo("")
    
    # Execute via API or locally
    trends_data = execute_trends(config, weeks)
    
    if json_output:
        # Output as JSON
        import json
        click.echo(json.dumps(trends_data, indent=2, default=str))
    else:
        # Generate markdown report
        markdown = format_trends_markdown(trends_data)
        
        # Save to file
        with open(output, 'w') as f:
            f.write(markdown)
        
        click.echo(f"✓ Trends report saved to {output}")
        click.echo("")
        
        # Show summary
        click.echo("WEEK-OVER-WEEK:")
        for comparison in trends_data['wow_comparisons']:
            prev_week = comparison['prev_week']['label']
            curr_week = comparison['curr_week']['label']
            num_increases = len(comparison['increases'])
            num_decreases = len(comparison['decreases'])
            
            click.echo(f"  {prev_week} → {curr_week}")
            click.echo(f"    Increases: {num_increases}, Decreases: {num_decreases}")
            
            if comparison['increases']:
                top = comparison['increases'][0]
                click.echo(f"    Top: {top['service']} (+${top['change']:,.2f})")
            
            click.echo("")
        
        click.echo("TRAILING 30-DAY (T-30):")
        for comparison in trends_data['t30_comparisons']:
            baseline_week = comparison['baseline_week']['label']
            curr_week = comparison['curr_week']['label']
            num_increases = len(comparison['increases'])
            num_decreases = len(comparison['decreases'])
            
            click.echo(f"  {curr_week} vs {baseline_week}")
            click.echo(f"    Increases: {num_increases}, Decreases: {num_decreases}")
            
            if comparison['increases']:
                top = comparison['increases'][0]
                click.echo(f"    Top: {top['service']} (+${top['change']:,.2f})")
            
            click.echo("")


@cli.command()
@click.option('--profile', required=True, help='Profile name')
@click.option('--months', default=6, help='Number of months to analyze (default: 6)')
@click.option('--output', default='monthly_trends.md', help='Output markdown file (default: monthly_trends.md)')
@click.option('--json-output', is_flag=True, help='Output as JSON')
@click.option('--sso', help='AWS SSO profile name')
@click.option('--access-key-id', help='AWS Access Key ID')
@click.option('--secret-access-key', help='AWS Secret Access Key')
@click.option('--session-token', help='AWS Session Token')
def monthly(profile, months, output, json_output, sso, access_key_id, secret_access_key, session_token):
    """
    Analyze month-over-month cost trends at service level.
    
    Compare costs between consecutive calendar months to identify sustained
    cost changes and trends. Perfect for monthly reporting and budget tracking.
    
    \b
    KEY FEATURES:
    • Month-over-month comparisons (Oct vs Sep, Sep vs Aug, etc.)
    • Service-level aggregation
    • Top 10 increases and decreases per comparison
    • Automatic filtering (>$50 and >5% changes)
    • Markdown report generation
    • JSON output for automation
    
    \b
    WHEN TO USE:
    • Monthly cost reporting and budgeting
    • Identifying sustained cost trends
    • Executive monthly summaries
    • Budget variance analysis
    • Long-term cost tracking
    
    \b
    EXAMPLES:
    
    Basic usage - last 6 months:
        cc monthly --profile khoros --sso khoros_umbrella
    
    Analyze more months:
        cc monthly --profile khoros --sso khoros_umbrella --months 12
    
    JSON output:
        cc monthly --profile khoros --sso khoros_umbrella --json-output
    
    \b
    OUTPUT:
    • Markdown report with month-over-month comparisons
    • Top 10 increases and decreases per month
    • Service costs and percentage changes
    • Filtered to significant changes (>$50 and >5%)
    
    \b
    SEE ALSO:
    • cc trends - For week-over-week analysis
    • cc drill - To investigate specific changes
    • cc calculate - For overall cost calculations
    """
    
    # Load profile
    config = load_profile(profile)
    config = apply_auth_options(config, sso, access_key_id, secret_access_key, session_token)
    
    click.echo(f"Analyzing last {months} months...")
    click.echo("")
    
    # Execute via API or locally
    monthly_data = execute_monthly(config, months)
    
    if json_output:
        # Output as JSON
        output_data = {
            'generated': datetime.now().isoformat(),
            'months': months,
            'comparisons': []
        }
        
        for comparison in monthly_data['comparisons']:
            output_data['comparisons'].append({
                'prev_month': comparison['prev_month']['label'],
                'curr_month': comparison['curr_month']['label'],
                'increases': comparison['increases'],
                'decreases': comparison['decreases'],
                'total_increase': comparison['total_increase'],
                'total_decrease': comparison['total_decrease']
            })
        
        click.echo(json.dumps(output_data, indent=2))
    else:
        # Generate markdown report
        markdown = format_monthly_markdown(monthly_data)
        
        # Save to file
        with open(output, 'w') as f:
            f.write(markdown)
        
        click.echo(f"✓ Monthly trends report saved to {output}")
        click.echo("")
        
        # Show summary
        for comparison in monthly_data['comparisons']:
            prev_month = comparison['prev_month']['label']
            curr_month = comparison['curr_month']['label']
            num_increases = len(comparison['increases'])
            num_decreases = len(comparison['decreases'])
            
            click.echo(f"{prev_month} → {curr_month}")
            click.echo(f"  Increases: {num_increases}, Decreases: {num_decreases}")
            
            if comparison['increases']:
                top = comparison['increases'][0]
                click.echo(f"  Top: {top['service']} (+${top['change']:,.2f})")
            
            click.echo("")


@cli.command()
@click.option('--profile', required=True, help='Profile name')
@click.option('--weeks', default=4, help='Number of weeks to analyze (default: 4)')
@click.option('--service', help='Filter by service name (e.g., "EC2 - Other")')
@click.option('--account', help='Filter by account ID')
@click.option('--usage-type', help='Filter by usage type')
@click.option('--dimension', type=click.Choice(['service', 'account', 'region', 'usage_type', 'resource', 'instance_type', 'operation', 'availability_zone']),
              help='Dimension to analyze by (overrides --service/--account filters)')
@click.option('--backend', type=click.Choice(['auto', 'ce', 'athena']), default='auto',
              help='Data source: auto (smart selection), ce (Cost Explorer), athena (CUR). Default: auto')
@click.option('--resources', is_flag=True, help='Show individual resource IDs (requires CUR, uses Athena)')
@click.option('--output', default='drill_down.md', help='Output markdown file (default: drill_down.md)')
@click.option('--json-output', is_flag=True, help='Output as JSON')
@click.option('--sso', help='AWS SSO profile name')
@click.option('--access-key-id', help='AWS Access Key ID')
@click.option('--secret-access-key', help='AWS Secret Access Key')
@click.option('--session-token', help='AWS Session Token')
def drill(profile, weeks, service, account, usage_type, dimension, backend, resources, output, json_output, sso, access_key_id, secret_access_key, session_token):
    """
    Drill down into cost changes by service, account, usage type, or resource.
    
    Investigate cost changes at different levels of granularity using a funnel
    approach. Start broad (all services), then drill into specific dimensions
    (accounts, regions, usage types, resources) to find root causes.
    
    \b
    KEY FEATURES:
    • Multi-dimensional analysis (service, account, region, usage type, resource)
    • Week-over-week cost comparisons
    • Automatic backend selection (Cost Explorer or Athena CUR)
    • Resource-level analysis with --resources flag
    • Flexible filtering by service, account, or usage type
    • Markdown reports and JSON output
    
    \b
    FUNNEL APPROACH:
    1. Start broad: cc drill --profile khoros --dimension service
       → See which services changed
    
    2. Drill by service: cc drill --profile khoros --service "EC2 - Other"
       → See which accounts for that service
    
    3. Drill deeper: cc drill --profile khoros --service "EC2 - Other" --account 123456
       → See usage types for that service + account
    
    4. Resource level: cc drill --profile khoros --service "EC2 - Other" --resources
       → See individual instance IDs and costs
    
    \b
    DIMENSIONS:
    • service - AWS service names (e.g., "EC2 - Other", "RDS")
    • account - AWS account IDs
    • region - AWS regions (e.g., "us-east-1")
    • usage_type - Detailed usage types (e.g., "BoxUsage:t3.medium")
    • resource - Individual resource IDs (requires --resources flag)
    • instance_type - EC2 instance types
    • operation - Operation types
    • availability_zone - Specific AZs
    
    \b
    BACKEND SELECTION:
    • auto (default) - Smart selection based on query
      - Uses Cost Explorer for service/account (fast)
      - Uses Athena for resource-level (detailed)
    • ce - Force Cost Explorer (faster, less granular)
    • athena - Force Athena CUR (slower, more granular)
    
    \b
    EXAMPLES:
    
    Analyze by service:
        cc drill --profile khoros --sso khoros_umbrella --dimension service
    
    Drill into specific service:
        cc drill --profile khoros --sso khoros_umbrella --service "EC2 - Other"
    
    Drill into service + account:
        cc drill --profile khoros --sso khoros_umbrella \\
            --service "EC2 - Other" --account 123456789012
    
    Resource-level analysis:
        cc drill --profile khoros --sso khoros_umbrella \\
            --service "EC2 - Other" --resources
    
    Analyze by region:
        cc drill --profile khoros --sso khoros_umbrella --dimension region
    
    Force Athena backend:
        cc drill --profile khoros --sso khoros_umbrella \\
            --dimension usage_type --backend athena
    
    \b
    OUTPUT:
    • Week-over-week comparisons for each dimension value
    • Top increases and decreases
    • Cost amounts and percentage changes
    • Resource IDs and tags (with --resources)
    • Markdown report saved to file
    
    \b
    NOTES:
    • --resources requires CUR data and Athena access
    • Cost Explorer is faster but less granular
    • Athena provides resource-level detail
    • Weeks run Sunday-Saturday
    • Requires at least 2 weeks of data
    
    \b
    SEE ALSO:
    • cc trends - For service-level trend analysis
    • cc investigate - For multi-stage investigation workflow
    • cc query - For custom Athena queries
    • cc tags - For tag-based cost analysis
        
        # Analyze by resource (auto-selects Athena - only source with resource IDs)
        cc drill --profile khoros --dimension resource --service AWSELB --account 820054669588
        
        # Force Athena backend for detailed analysis
        cc drill --profile khoros --dimension service --backend athena
    """
    
    # Load profile
    config = load_profile(profile)
    config = apply_auth_options(config, sso, access_key_id, secret_access_key, session_token)
    
    # Smart backend selection
    def select_backend(dimension, resources_flag, backend_choice):
        """Auto-select backend based on query requirements"""
        if backend_choice != 'auto':
            return backend_choice
        
        # Must use Athena if:
        if dimension == 'resource' or resources_flag:
            return 'athena'
        
        # Prefer CE for speed (unless explicitly requesting Athena)
        return 'ce'
    
    selected_backend = select_backend(dimension, resources, backend)
    
    # Show filters
    click.echo(f"Analyzing last {weeks} weeks...")
    if dimension:
        click.echo(f"  Dimension: {dimension}")
    if service:
        click.echo(f"  Service filter: {service}")
    if account:
        click.echo(f"  Account filter: {account}")
    if usage_type:
        click.echo(f"  Usage type filter: {usage_type}")
    if resources:
        click.echo(f"  Mode: Resource-level (CUR via Athena)")
    click.echo(f"  Backend: {selected_backend.upper()}")
    click.echo("")
    
    # Execute via API or locally
    drill_data = execute_drill(config, weeks, service, account, usage_type, resources, dimension, selected_backend)
    
    # Handle resource-level output differently
    if resources:
        from cost_calculator.cur import format_resource_output
        output_text = format_resource_output(drill_data)
        click.echo(output_text)
        return
    
    if json_output:
        # Output as JSON
        output_data = {
            'generated': datetime.now().isoformat(),
            'weeks': weeks,
            'filters': drill_data['filters'],
            'group_by': drill_data['group_by'],
            'comparisons': []
        }
        
        for comparison in drill_data['comparisons']:
            output_data['comparisons'].append({
                'prev_week': comparison['prev_week']['label'],
                'curr_week': comparison['curr_week']['label'],
                'increases': comparison['increases'],
                'decreases': comparison['decreases'],
                'total_increase': comparison['total_increase'],
                'total_decrease': comparison['total_decrease']
            })
        
        click.echo(json.dumps(output_data, indent=2))
    else:
        # Generate markdown report
        markdown = format_drill_down_markdown(drill_data)
        
        # Save to file
        with open(output, 'w') as f:
            f.write(markdown)
        
        click.echo(f"✓ Drill-down report saved to {output}")
        click.echo("")
        
        # Show summary
        group_by_label = {
            'SERVICE': 'services',
            'LINKED_ACCOUNT': 'accounts',
            'USAGE_TYPE': 'usage types',
            'REGION': 'regions'
        }.get(drill_data['group_by'], 'items')
        
        click.echo(f"Showing top {group_by_label}:")
        for comparison in drill_data['comparisons']:
            prev_week = comparison['prev_week']['label']
            curr_week = comparison['curr_week']['label']
            num_increases = len(comparison['increases'])
            num_decreases = len(comparison['decreases'])
            
            click.echo(f"{prev_week} → {curr_week}")
            click.echo(f"  Increases: {num_increases}, Decreases: {num_decreases}")
            
            if comparison['increases']:
                top = comparison['increases'][0]
                click.echo(f"  Top: {top['dimension'][:50]} (+${top['change']:,.2f})")
            
            click.echo("")


@cli.command()
@click.option('--profile', required=True, help='Profile name')
@click.option('--type', 'analysis_type', default='summary',
              type=click.Choice(['summary', 'volatility', 'trends', 'search']),
              help='Analysis type')
@click.option('--weeks', default=12, help='Number of weeks (default: 12)')
@click.option('--pattern', help='Service search pattern (for search type)')
@click.option('--min-cost', type=float, help='Minimum cost filter (for search type)')
@click.option('--json-output', is_flag=True, help='Output as JSON')
def analyze(profile, analysis_type, weeks, pattern, min_cost, json_output):
    """Perform pandas-based analysis (aggregations, volatility, trends, search)"""
    
    config = load_profile(profile)
    
    if not json_output:
        click.echo(f"Running {analysis_type} analysis for {weeks} weeks...")
    
    from cost_calculator.executor import execute_analyze
    result = execute_analyze(config, weeks, analysis_type, pattern, min_cost)
    
    if json_output:
        import json
        click.echo(json.dumps(result, indent=2, default=str))
    else:
        # Format output based on type
        if analysis_type == 'summary':
            click.echo(f"\n📊 Summary ({result.get('total_services', 0)} services)")
            click.echo(f"Weeks analyzed: {result.get('weeks_analyzed', 0)}")
            click.echo(f"\nTop 10 Services (by total change):")
            for svc in result.get('services', [])[:10]:
                click.echo(f"  {svc['service']}")
                click.echo(f"    Total: ${svc['change_sum']:,.2f}")
                click.echo(f"    Average: ${svc['change_mean']:,.2f}")
                click.echo(f"    Volatility: {svc['volatility']:.3f}")
        
        elif analysis_type == 'volatility':
            click.echo(f"\n📈 High Volatility Services:")
            for svc in result.get('high_volatility_services', [])[:10]:
                click.echo(f"  {svc['service']}: CV={svc['coefficient_of_variation']:.3f}")
            
            outliers = result.get('outliers', [])
            if outliers:
                click.echo(f"\n⚠️  Outliers ({len(outliers)}):")
                for o in outliers[:5]:
                    click.echo(f"  {o['service']} ({o['week']}): ${o['change']:,.2f} (z={o['z_score']:.2f})")
        
        elif analysis_type == 'trends':
            inc = result.get('increasing_trends', [])
            dec = result.get('decreasing_trends', [])
            
            click.echo(f"\n📈 Increasing Trends ({len(inc)}):")
            for t in inc[:5]:
                click.echo(f"  {t['service']}: ${t['avg_change']:,.2f}/week")
            
            click.echo(f"\n📉 Decreasing Trends ({len(dec)}):")
            for t in dec[:5]:
                click.echo(f"  {t['service']}: ${t['avg_change']:,.2f}/week")
        
        elif analysis_type == 'search':
            matches = result.get('matches', [])
            click.echo(f"\n🔍 Search Results ({len(matches)} matches)")
            if pattern:
                click.echo(f"Pattern: {pattern}")
            if min_cost:
                click.echo(f"Min cost: ${min_cost:,.2f}")
            
            for m in matches[:20]:
                click.echo(f"  {m['service']}: ${m['curr_cost']:,.2f}")


@cli.command()
@click.argument('operation', type=click.Choice(['list', 'get', 'create', 'update', 'delete']))
@click.option('--name', help='Profile name')
@click.option('--accounts', help='Comma-separated account IDs')
@click.option('--description', help='Profile description')
def profile(operation, name, accounts, description):
    """Manage profiles (CRUD operations)"""
    
    from cost_calculator.executor import execute_profile_operation
    
    # Parse accounts if provided
    account_list = None
    if accounts:
        account_list = [a.strip() for a in accounts.split(',')]
    
    result = execute_profile_operation(
        operation=operation,
        profile_name=name,
        accounts=account_list,
        description=description
    )
    
    if operation == 'list':
        profiles = result.get('profiles', [])
        click.echo(f"\n📋 Profiles ({len(profiles)}):")
        for p in profiles:
            click.echo(f"  {p['profile_name']}: {len(p.get('accounts', []))} accounts")
            if p.get('description'):
                click.echo(f"    {p['description']}")
    
    elif operation == 'get':
        profile_data = result.get('profile', {})
        click.echo(f"\n📋 Profile: {profile_data.get('profile_name')}")
        click.echo(f"Accounts: {len(profile_data.get('accounts', []))}")
        if profile_data.get('description'):
            click.echo(f"Description: {profile_data['description']}")
        click.echo(f"\nAccounts:")
        for acc in profile_data.get('accounts', []):
            click.echo(f"  {acc}")
    
    else:
        click.echo(result.get('message', 'Operation completed'))


@cli.command()
@click.option('--profile', required=True, help='Profile name')
@click.option('--sso', help='AWS SSO profile to use')
@click.option('--weeks', default=8, help='Number of weeks to analyze')
@click.option('--account', help='Focus on specific account ID')
@click.option('--service', help='Focus on specific service')
@click.option('--no-cloudtrail', is_flag=True, help='Skip CloudTrail analysis (faster)')
@click.option('--output', default='investigation_report.md', help='Output file path')
def investigate(profile, sso, weeks, account, service, no_cloudtrail, output):
    """
    Multi-stage cost investigation:
    1. Analyze cost trends and drill-downs
    2. Inventory actual resources in problem accounts
    3. Analyze CloudTrail events (optional)
    4. Generate comprehensive report
    """
    from cost_calculator.executor import execute_trends, execute_drill, get_credentials_dict
    from cost_calculator.api_client import call_lambda_api, is_api_configured
    from cost_calculator.forensics import format_investigation_report
    from datetime import datetime, timedelta
    
    click.echo("=" * 80)
    click.echo("COST INVESTIGATION")
    click.echo("=" * 80)
    click.echo(f"Profile: {profile}")
    click.echo(f"Weeks: {weeks}")
    if account:
        click.echo(f"Account: {account}")
    if service:
        click.echo(f"Service: {service}")
    click.echo("")
    
    # Load profile
    config = load_profile(profile)
    
    # Override with SSO if provided
    if sso:
        config['aws_profile'] = sso
    
    # Validate that we have a way to get credentials
    if 'aws_profile' not in config and 'credentials' not in config:
        import subprocess
        try:
            result = subprocess.run(
                ['aws', 'configure', 'list-profiles'],
                capture_output=True,
                text=True,
                timeout=5
            )
            available = result.stdout.strip().split('\n') if result.returncode == 0 else []
            suggestion = f"\nAvailable AWS profiles: {', '.join(available[:5])}" if available else ""
        except:
            suggestion = ""
        
        raise click.ClickException(
            f"Profile '{profile}' has no AWS authentication configured.\n"
            f"Use --sso flag to specify your AWS SSO profile:\n"
            f"  cc investigate --profile {profile} --sso YOUR_AWS_PROFILE{suggestion}"
        )
    
    # Step 1: Cost Analysis
    click.echo("Step 1/3: Analyzing cost trends...")
    try:
        trends_data = execute_trends(config, weeks)
        click.echo(f"✓ Found cost data for {weeks} weeks")
    except Exception as e:
        click.echo(f"✗ Error analyzing trends: {str(e)}")
        trends_data = None
    
    # Step 2: Drill-down
    click.echo("\nStep 2/3: Drilling down into costs...")
    drill_data = None
    if service or account:
        try:
            drill_data = execute_drill(config, weeks, service, account, None, False)
            click.echo(f"✓ Drill-down complete")
        except Exception as e:
            click.echo(f"✗ Error in drill-down: {str(e)}")
    
    # Step 3: Resource Inventory
    click.echo("\nStep 3/3: Inventorying resources...")
    inventories = []
    cloudtrail_analyses = []
    
    # Determine which accounts to investigate
    accounts_to_investigate = []
    if account:
        accounts_to_investigate = [account]
    else:
        # Extract top cost accounts from trends/drill data
        # For now, we'll need the user to specify
        click.echo("⚠️  No account specified. Use --account to inventory resources.")
    
    # For each account, do inventory and CloudTrail via backend API
    for acc_id in accounts_to_investigate:
        click.echo(f"\n  Investigating account {acc_id}...")
        
        # Get credentials (SSO or static)
        account_creds = get_credentials_dict(config)
        if not account_creds:
            click.echo(f"    ⚠️  No credentials available for account")
            continue
        
        # Inventory resources via backend API only
        if not is_api_configured():
            click.echo(f"    ✗ API not configured. Set COST_API_SECRET environment variable.")
            continue
        
        try:
            regions = ['us-west-2', 'us-east-1', 'eu-west-1']
            for region in regions:
                try:
                    inv = call_lambda_api(
                        'forensics',
                        account_creds,
                        [],  # accounts not needed for forensics
                        operation='inventory',
                        account_id=acc_id,
                        region=region
                    )
                    
                    if not inv.get('error'):
                        inventories.append(inv)
                        click.echo(f"    ✓ Inventory complete for {region}")
                        click.echo(f"      - EC2: {len(inv['ec2_instances'])} instances")
                        click.echo(f"      - EFS: {len(inv['efs_file_systems'])} file systems ({inv.get('total_efs_size_gb', 0):,.0f} GB)")
                        click.echo(f"      - ELB: {len(inv['load_balancers'])} load balancers")
                        break
                except Exception as e:
                    continue
        except Exception as e:
            click.echo(f"    ✗ Inventory error: {str(e)}")
        
        # CloudTrail analysis via backend API only
        if not no_cloudtrail:
            if not is_api_configured():
                click.echo(f"    ✗ CloudTrail skipped: API not configured")
            else:
                try:
                    start_date = (datetime.now() - timedelta(days=weeks * 7)).isoformat() + 'Z'
                    end_date = datetime.now().isoformat() + 'Z'
                    
                    ct_analysis = call_lambda_api(
                        'forensics',
                        account_creds,
                        [],
                        operation='cloudtrail',
                        account_id=acc_id,
                        start_date=start_date,
                        end_date=end_date,
                        region='us-west-2'
                    )
                    
                    cloudtrail_analyses.append(ct_analysis)
                    
                    if ct_analysis.get('error'):
                        click.echo(f"    ⚠️  CloudTrail: {ct_analysis['error']}")
                    else:
                        click.echo(f"    ✓ CloudTrail analysis complete")
                        click.echo(f"      - {len(ct_analysis['event_summary'])} event types")
                        click.echo(f"      - {len(ct_analysis['write_events'])} resource changes")
                except Exception as e:
                    click.echo(f"    ✗ CloudTrail error: {str(e)}")
    
    # Generate report
    click.echo(f"\nGenerating report...")
    report = format_investigation_report(trends_data, inventories, cloudtrail_analyses if not no_cloudtrail else None)
    
    # Write to file
    with open(output, 'w') as f:
        f.write(report)
    
    click.echo(f"\n✓ Investigation complete!")
    click.echo(f"✓ Report saved to: {output}")
    click.echo("")


def find_account_profile(account_id):
    """
    Find the SSO profile name for a given account ID
    Returns profile name or None
    """
    import subprocess
    
    try:
        # Get list of profiles
        result = subprocess.run(
            ['aws', 'configure', 'list-profiles'],
            capture_output=True,
            text=True
        )
        
        profiles = result.stdout.strip().split('\n')
        
        # Check each profile
        for profile in profiles:
            try:
                result = subprocess.run(
                    ['aws', 'sts', 'get-caller-identity', '--profile', profile],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if account_id in result.stdout:
                    return profile
            except:
                continue
        
        return None
    except:
        return None


@cli.command()
@click.option('--profile', required=True, help='Profile name')
@click.option('--start-date', help='Start date (YYYY-MM-DD)')
@click.option('--end-date', help='End date (YYYY-MM-DD)')
@click.option('--days', type=int, default=10, help='Number of days to analyze (default: 10)')
@click.option('--service', help='Filter by service name')
@click.option('--account', help='Filter by account ID')
@click.option('--sso', help='AWS SSO profile name')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def daily(profile, start_date, end_date, days, service, account, sso, output_json):
    """
    Get daily cost breakdown with granular detail.
    
    Shows day-by-day costs for specific services and accounts, useful for:
    - Identifying cost spikes on specific dates
    - Validating daily cost patterns
    - Calculating precise daily averages
    
    Examples:
        # Last 10 days of CloudWatch costs for specific account
        cc daily --profile khoros --days 10 --service AmazonCloudWatch --account 820054669588
        
        # Custom date range with JSON output for automation
        cc daily --profile khoros --start-date 2025-10-28 --end-date 2025-11-06 --json
        
        # Find high-cost days using jq
        cc daily --profile khoros --days 30 --json | jq '.daily_costs | map(select(.cost > 1000))'
    """
    # Load profile
    config = load_profile(profile)
    
    # Apply SSO if provided
    if sso:
        config['aws_profile'] = sso
    
    # Calculate date range
    if end_date:
        end = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        end = datetime.now()
    
    if start_date:
        start = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        start = end - timedelta(days=days)
    
    click.echo(f"Daily breakdown: {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")
    if service:
        click.echo(f"Service filter: {service}")
    if account:
        click.echo(f"Account filter: {account}")
    click.echo("")
    
    # Get credentials
    try:
        if 'aws_profile' in config:
            session = boto3.Session(profile_name=config['aws_profile'])
        else:
            creds = config['credentials']
            session = boto3.Session(
                aws_access_key_id=creds['aws_access_key_id'],
                aws_secret_access_key=creds['aws_secret_access_key'],
                aws_session_token=creds.get('aws_session_token')
            )
        
        ce_client = session.client('ce', region_name='us-east-1')
        
        # Build filter
        filter_parts = []
        
        # Account filter
        if account:
            filter_parts.append({
                "Dimensions": {
                    "Key": "LINKED_ACCOUNT",
                    "Values": [account]
                }
            })
        else:
            filter_parts.append({
                "Dimensions": {
                    "Key": "LINKED_ACCOUNT",
                    "Values": config['accounts']
                }
            })
        
        # Service filter
        if service:
            filter_parts.append({
                "Dimensions": {
                    "Key": "SERVICE",
                    "Values": [service]
                }
            })
        
        # Exclude support and tax
        filter_parts.append({
            "Not": {
                "Dimensions": {
                    "Key": "RECORD_TYPE",
                    "Values": ["Tax", "Support"]
                }
            }
        })
        
        cost_filter = {"And": filter_parts} if len(filter_parts) > 1 else filter_parts[0]
        
        # Get daily costs
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': start.strftime('%Y-%m-%d'),
                'End': (end + timedelta(days=1)).strftime('%Y-%m-%d')
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost'],
            Filter=cost_filter
        )
        
        # Collect results
        daily_costs = []
        total = 0
        for day in response['ResultsByTime']:
            date = day['TimePeriod']['Start']
            cost = float(day['Total']['UnblendedCost']['Amount'])
            total += cost
            daily_costs.append({'date': date, 'cost': cost})
        
        num_days = len(response['ResultsByTime'])
        daily_avg = total / num_days if num_days > 0 else 0
        annual = daily_avg * 365
        
        # Output results
        if output_json:
            import json
            result = {
                'period': {
                    'start': start.strftime('%Y-%m-%d'),
                    'end': end.strftime('%Y-%m-%d'),
                    'days': num_days
                },
                'filters': {
                    'service': service,
                    'account': account
                },
                'daily_costs': daily_costs,
                'summary': {
                    'total': total,
                    'daily_avg': daily_avg,
                    'annual_projection': annual
                }
            }
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo("Date       | Cost")
            click.echo("-----------|-----------")
            for item in daily_costs:
                click.echo(f"{item['date']} | ${item['cost']:,.2f}")
            click.echo("-----------|-----------")
            click.echo(f"Total      | ${total:,.2f}")
            click.echo(f"Daily Avg  | ${daily_avg:,.2f}")
            click.echo(f"Annual     | ${annual:,.0f}")
        
    except Exception as e:
        raise click.ClickException(f"Failed to get daily costs: {e}")


@cli.command()
@click.option('--profile', required=True, help='Profile name')
@click.option('--account', help='Account ID to compare')
@click.option('--service', help='Service to compare')
@click.option('--before', required=True, help='Before period (YYYY-MM-DD:YYYY-MM-DD)')
@click.option('--after', required=True, help='After period (YYYY-MM-DD:YYYY-MM-DD)')
@click.option('--expected-reduction', type=float, help='Expected reduction percentage')
@click.option('--sso', help='AWS SSO profile name')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def compare(profile, account, service, before, after, expected_reduction, sso, output_json):
    """
    Compare costs between two periods for validation and analysis.
    
    Perfect for:
    - Validating cost optimization savings
    - Before/after migration analysis
    - Measuring impact of infrastructure changes
    - Automated savings validation in CI/CD
    
    Examples:
        # Validate Datadog migration savings (expect 50% reduction)
        cc compare --profile khoros --account 180770971501 --service AmazonCloudWatch \
          --before "2025-10-28:2025-11-06" --after "2025-11-17:2025-11-26" --expected-reduction 50
        
        # Compare total costs across all accounts
        cc compare --profile khoros --before "2025-10-01:2025-10-31" --after "2025-11-01:2025-11-30"
        
        # JSON output for automated validation
        cc compare --profile khoros --service EC2 --before "2025-10-01:2025-10-07" \
          --after "2025-11-08:2025-11-14" --json | jq '.comparison.met_expectation'
    """
    # Load profile
    config = load_profile(profile)
    
    # Apply SSO if provided
    if sso:
        config['aws_profile'] = sso
    
    # Parse periods
    try:
        before_start, before_end = before.split(':')
        after_start, after_end = after.split(':')
    except ValueError:
        raise click.ClickException("Period format must be 'YYYY-MM-DD:YYYY-MM-DD'")
    
    if not output_json:
        click.echo(f"Comparing periods:")
        click.echo(f"  Before: {before_start} to {before_end}")
        click.echo(f"  After:  {after_start} to {after_end}")
        if service:
            click.echo(f"  Service: {service}")
        if account:
            click.echo(f"  Account: {account}")
        click.echo("")
    
    # Get credentials
    try:
        if 'aws_profile' in config:
            session = boto3.Session(profile_name=config['aws_profile'])
        else:
            creds = config['credentials']
            session = boto3.Session(
                aws_access_key_id=creds['aws_access_key_id'],
                aws_secret_access_key=creds['aws_secret_access_key'],
                aws_session_token=creds.get('aws_session_token')
            )
        
        ce_client = session.client('ce', region_name='us-east-1')
        
        # Build filter
        def build_filter():
            filter_parts = []
            
            if account:
                filter_parts.append({
                    "Dimensions": {
                        "Key": "LINKED_ACCOUNT",
                        "Values": [account]
                    }
                })
            else:
                filter_parts.append({
                    "Dimensions": {
                        "Key": "LINKED_ACCOUNT",
                        "Values": config['accounts']
                    }
                })
            
            if service:
                filter_parts.append({
                    "Dimensions": {
                        "Key": "SERVICE",
                        "Values": [service]
                    }
                })
            
            filter_parts.append({
                "Not": {
                    "Dimensions": {
                        "Key": "RECORD_TYPE",
                        "Values": ["Tax", "Support"]
                    }
                }
            })
            
            return {"And": filter_parts} if len(filter_parts) > 1 else filter_parts[0]
        
        cost_filter = build_filter()
        
        # Get before period costs
        before_response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': before_start,
                'End': (datetime.strptime(before_end, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost'],
            Filter=cost_filter
        )
        
        # Get after period costs
        after_response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': after_start,
                'End': (datetime.strptime(after_end, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost'],
            Filter=cost_filter
        )
        
        # Calculate totals
        before_total = sum(float(day['Total']['UnblendedCost']['Amount']) for day in before_response['ResultsByTime'])
        after_total = sum(float(day['Total']['UnblendedCost']['Amount']) for day in after_response['ResultsByTime'])
        
        before_days = len(before_response['ResultsByTime'])
        after_days = len(after_response['ResultsByTime'])
        
        before_daily = before_total / before_days if before_days > 0 else 0
        after_daily = after_total / after_days if after_days > 0 else 0
        
        reduction = before_daily - after_daily
        reduction_pct = (reduction / before_daily * 100) if before_daily > 0 else 0
        annual_savings = reduction * 365
        
        # Output results
        if output_json:
            import json
            result = {
                'before': {
                    'period': {'start': before_start, 'end': before_end},
                    'total': before_total,
                    'daily_avg': before_daily,
                    'days': before_days
                },
                'after': {
                    'period': {'start': after_start, 'end': after_end},
                    'total': after_total,
                    'daily_avg': after_daily,
                    'days': after_days
                },
                'comparison': {
                    'daily_reduction': reduction,
                    'reduction_pct': reduction_pct,
                    'annual_savings': annual_savings
                }
            }
            
            if expected_reduction is not None:
                result['comparison']['expected_reduction_pct'] = expected_reduction
                result['comparison']['met_expectation'] = reduction_pct >= expected_reduction
            
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo("Before Period:")
            click.echo(f"  Total: ${before_total:,.2f}")
            click.echo(f"  Daily Avg: ${before_daily:,.2f}")
            click.echo(f"  Days: {before_days}")
            click.echo("")
            click.echo("After Period:")
            click.echo(f"  Total: ${after_total:,.2f}")
            click.echo(f"  Daily Avg: ${after_daily:,.2f}")
            click.echo(f"  Days: {after_days}")
            click.echo("")
            click.echo("Comparison:")
            click.echo(f"  Daily Reduction: ${reduction:,.2f}")
            click.echo(f"  Reduction %: {reduction_pct:.1f}%")
            click.echo(f"  Annual Savings: ${annual_savings:,.0f}")
            
            if expected_reduction is not None:
                click.echo("")
                if reduction_pct >= expected_reduction:
                    click.echo(f"✅ Savings achieved: {reduction_pct:.1f}% (expected {expected_reduction}%)")
                else:
                    click.echo(f"⚠️  Below target: {reduction_pct:.1f}% (expected {expected_reduction}%)")
        
    except Exception as e:
        raise click.ClickException(f"Comparison failed: {e}")


@cli.command()
@click.option('--profile', required=True, help='Profile name')
@click.option('--tag-key', required=True, help='Tag key to filter by')
@click.option('--tag-value', help='Tag value to filter by (optional)')
@click.option('--start-date', help='Start date (YYYY-MM-DD)')
@click.option('--end-date', help='End date (YYYY-MM-DD)')
@click.option('--days', type=int, default=30, help='Number of days to analyze (default: 30)')
@click.option('--sso', help='AWS SSO profile name')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def tags(profile, tag_key, tag_value, start_date, end_date, days, sso, output_json):
    """
    Analyze costs grouped by resource tags for cost attribution.
    
    Useful for:
    - Cost allocation by team, project, or environment
    - Identifying untagged resources (cost attribution gaps)
    - Tracking costs by cost center or department
    - Validating tagging compliance
    
    Examples:
        # See all costs by Environment tag
        cc tags --profile khoros --tag-key "Environment" --days 30
        
        # Filter to specific tag value
        cc tags --profile khoros --tag-key "Team" --tag-value "Platform" --days 30
        
        # Find top cost centers with JSON output
        cc tags --profile khoros --tag-key "CostCenter" --days 30 --json | \
          jq '.tag_costs | sort_by(-.cost) | .[:5]'
        
        # Identify untagged resources (look for empty tag values)
        cc tags --profile khoros --tag-key "Owner" --days 7
    """
    # Load profile
    config = load_profile(profile)
    
    # Apply SSO if provided
    if sso:
        config['aws_profile'] = sso
    
    # Calculate date range
    if end_date:
        end = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        end = datetime.now()
    
    if start_date:
        start = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        start = end - timedelta(days=days)
    
    if not output_json:
        click.echo(f"Tag-based cost analysis: {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")
        click.echo(f"Tag key: {tag_key}")
        if tag_value:
            click.echo(f"Tag value: {tag_value}")
        click.echo("")
    
    # Get credentials
    try:
        if 'aws_profile' in config:
            session = boto3.Session(profile_name=config['aws_profile'])
        else:
            creds = config['credentials']
            session = boto3.Session(
                aws_access_key_id=creds['aws_access_key_id'],
                aws_secret_access_key=creds['aws_secret_access_key'],
                aws_session_token=creds.get('aws_session_token')
            )
        
        ce_client = session.client('ce', region_name='us-east-1')
        
        # Build filter
        filter_parts = [
            {
                "Dimensions": {
                    "Key": "LINKED_ACCOUNT",
                    "Values": config['accounts']
                }
            },
            {
                "Not": {
                    "Dimensions": {
                        "Key": "RECORD_TYPE",
                        "Values": ["Tax", "Support"]
                    }
                }
            }
        ]
        
        # Add tag filter if value specified
        if tag_value:
            filter_parts.append({
                "Tags": {
                    "Key": tag_key,
                    "Values": [tag_value]
                }
            })
        
        cost_filter = {"And": filter_parts}
        
        # Get costs grouped by tag values
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': start.strftime('%Y-%m-%d'),
                'End': (end + timedelta(days=1)).strftime('%Y-%m-%d')
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[{
                'Type': 'TAG',
                'Key': tag_key
            }],
            Filter=cost_filter
        )
        
        # Collect results
        tag_costs = {}
        for period in response['ResultsByTime']:
            for group in period['Groups']:
                tag_val = group['Keys'][0].split('$')[1] if '$' in group['Keys'][0] else group['Keys'][0]
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                tag_costs[tag_val] = tag_costs.get(tag_val, 0) + cost
        
        # Sort by cost
        sorted_tags = sorted(tag_costs.items(), key=lambda x: x[1], reverse=True)
        
        total = sum(tag_costs.values())
        num_days = (end - start).days
        daily_avg = total / num_days if num_days > 0 else 0
        
        # Output results
        if output_json:
            import json
            result = {
                'period': {
                    'start': start.strftime('%Y-%m-%d'),
                    'end': end.strftime('%Y-%m-%d'),
                    'days': num_days
                },
                'tag_key': tag_key,
                'tag_value_filter': tag_value,
                'tag_costs': [{'tag_value': k, 'cost': v, 'percentage': (v/total*100) if total > 0 else 0} for k, v in sorted_tags],
                'summary': {
                    'total': total,
                    'daily_avg': daily_avg,
                    'annual_projection': daily_avg * 365
                }
            }
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"Tag Value{' '*(30-len('Tag Value'))} | Cost       | %")
            click.echo("-" * 60)
            for tag_val, cost in sorted_tags:
                pct = (cost / total * 100) if total > 0 else 0
                tag_display = tag_val[:30].ljust(30)
                click.echo(f"{tag_display} | ${cost:>9,.2f} | {pct:>5.1f}%")
            click.echo("-" * 60)
            click.echo(f"{'Total'.ljust(30)} | ${total:>9,.2f} | 100.0%")
            click.echo("")
            click.echo(f"Daily Avg: ${daily_avg:,.2f}")
            click.echo(f"Annual Projection: ${daily_avg * 365:,.0f}")
        
    except Exception as e:
        raise click.ClickException(f"Tag analysis failed: {e}")


@cli.command()
@click.option('--profile', required=True, help='Profile name')
@click.option('--query', required=True, help='SQL query to execute')
@click.option('--database', default='athenacurcfn_cloud_intelligence_dashboard', help='Athena database name')
@click.option('--output-bucket', help='S3 bucket for query results (default: from profile)')
@click.option('--sso', help='AWS SSO profile name')
def query(profile, query, database, output_bucket, sso):
    """
    Execute custom Athena SQL query on CUR data
    
    Example:
        cc query --profile khoros --query "SELECT line_item_usage_account_id, SUM(line_item_unblended_cost) as cost FROM cloud_intelligence_dashboard WHERE line_item_usage_start_date >= DATE '2025-11-01' GROUP BY 1 ORDER BY 2 DESC LIMIT 10"
    """
    # Load profile
    config = load_profile(profile)
    
    # Apply SSO if provided
    if sso:
        config['aws_profile'] = sso
    
    # Get credentials
    try:
        if 'aws_profile' in config:
            session = boto3.Session(profile_name=config['aws_profile'])
        else:
            creds = config['credentials']
            session = boto3.Session(
                aws_access_key_id=creds['aws_access_key_id'],
                aws_secret_access_key=creds['aws_secret_access_key'],
                aws_session_token=creds.get('aws_session_token')
            )
        
        athena_client = session.client('athena', region_name='us-east-1')
        
        # Default output location
        if not output_bucket:
            output_bucket = 's3://khoros-finops-athena/athena/'
        
        click.echo(f"Executing query on database: {database}")
        click.echo(f"Output location: {output_bucket}")
        click.echo("")
        
        # Execute query
        response = athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': database},
            ResultConfiguration={'OutputLocation': output_bucket}
        )
        
        query_id = response['QueryExecutionId']
        click.echo(f"Query ID: {query_id}")
        click.echo("Waiting for query to complete...")
        
        # Wait for completion
        import time
        max_wait = 60
        waited = 0
        while waited < max_wait:
            status_response = athena_client.get_query_execution(QueryExecutionId=query_id)
            status = status_response['QueryExecution']['Status']['State']
            
            if status == 'SUCCEEDED':
                click.echo("✓ Query completed successfully")
                break
            elif status in ['FAILED', 'CANCELLED']:
                reason = status_response['QueryExecution']['Status'].get('StateChangeReason', 'Unknown')
                raise click.ClickException(f"Query {status}: {reason}")
            
            time.sleep(2)
            waited += 2
        
        if waited >= max_wait:
            raise click.ClickException(f"Query timeout after {max_wait}s. Check query ID: {query_id}")
        
        # Get results
        results = athena_client.get_query_results(QueryExecutionId=query_id)
        
        # Display results
        rows = results['ResultSet']['Rows']
        if not rows:
            click.echo("No results returned")
            return
        
        # Header
        headers = [col['VarCharValue'] for col in rows[0]['Data']]
        click.echo(" | ".join(headers))
        click.echo("-" * (len(" | ".join(headers))))
        
        # Data rows
        for row in rows[1:]:
            values = [col.get('VarCharValue', '') for col in row['Data']]
            click.echo(" | ".join(values))
        
        click.echo("")
        click.echo(f"Returned {len(rows)-1} rows")
        
    except Exception as e:
        raise click.ClickException(f"Query failed: {e}")


@cli.group()
def exclusions():
    """
    Manage cost exclusions (services/types to exclude from calculations).
    
    Exclusions are stored in DynamoDB and apply globally or per-profile.
    Common exclusions: Tax, Support, OCBLateFee, Refunds, Credits
    """
    pass


@exclusions.command('show')
@click.option('--profile', help='Show profile-specific exclusions (default: global)')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def show_exclusions(profile, output_json):
    """Show current exclusions configuration"""
    import requests
    
    api_secret = get_api_secret()
    if not api_secret:
        raise click.ClickException(
            "No API secret configured.\n"
            "Run: cc configure --api-secret YOUR_SECRET"
        )
    
    try:
        response = requests.post(
            PROFILES_API_URL,
            headers={'X-API-Secret': api_secret, 'Content-Type': 'application/json'},
            json={'operation': 'get_exclusions', 'profile_name': profile},
            timeout=10
        )
        
        if response.status_code == 200:
            exclusions_data = response.json().get('exclusions', {})
            
            if output_json:
                click.echo(json.dumps(exclusions_data, indent=2))
            else:
                scope = profile if profile else "global"
                click.echo(f"Exclusions ({scope}):")
                click.echo("")
                
                if exclusions_data.get('record_types'):
                    click.echo("Record Types:")
                    for rt in exclusions_data['record_types']:
                        click.echo(f"  - {rt}")
                    click.echo("")
                
                if exclusions_data.get('services'):
                    click.echo("Services:")
                    for svc in exclusions_data['services']:
                        click.echo(f"  - {svc}")
                    click.echo("")
                
                if exclusions_data.get('line_item_types'):
                    click.echo("Line Item Types:")
                    for lit in exclusions_data['line_item_types']:
                        click.echo(f"  - {lit}")
                    click.echo("")
                
                if exclusions_data.get('usage_types'):
                    click.echo("Usage Types:")
                    for ut in exclusions_data['usage_types']:
                        click.echo(f"  - {ut}")
        else:
            raise click.ClickException(f"Failed to fetch exclusions: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        raise click.ClickException(f"API request failed: {e}")


@exclusions.command('add')
@click.option('--record-type', help='Add record type exclusion (e.g., Tax, Support)')
@click.option('--service', help='Add service exclusion (e.g., OCBLateFee)')
@click.option('--line-item-type', help='Add line item type exclusion (e.g., Refund, Credit)')
@click.option('--usage-type', help='Add usage type exclusion')
@click.option('--profile', help='Add to profile-specific exclusions (default: global)')
def add_exclusion(record_type, service, line_item_type, usage_type, profile):
    """Add an exclusion"""
    import requests
    
    if not any([record_type, service, line_item_type, usage_type]):
        raise click.ClickException(
            "Must specify at least one of: --record-type, --service, --line-item-type, --usage-type"
        )
    
    api_secret = get_api_secret()
    if not api_secret:
        raise click.ClickException(
            "No API secret configured.\n"
            "Run: cc configure --api-secret YOUR_SECRET"
        )
    
    # Get current exclusions
    try:
        response = requests.post(
            PROFILES_API_URL,
            headers={'X-API-Secret': api_secret, 'Content-Type': 'application/json'},
            json={'operation': 'get_exclusions', 'profile_name': profile},
            timeout=10
        )
        
        if response.status_code == 200:
            exclusions_data = response.json().get('exclusions', {})
        else:
            exclusions_data = {
                'record_types': [],
                'services': [],
                'line_item_types': [],
                'usage_types': []
            }
        
        # Add new exclusions
        if record_type and record_type not in exclusions_data.get('record_types', []):
            exclusions_data.setdefault('record_types', []).append(record_type)
        
        if service and service not in exclusions_data.get('services', []):
            exclusions_data.setdefault('services', []).append(service)
        
        if line_item_type and line_item_type not in exclusions_data.get('line_item_types', []):
            exclusions_data.setdefault('line_item_types', []).append(line_item_type)
        
        if usage_type and usage_type not in exclusions_data.get('usage_types', []):
            exclusions_data.setdefault('usage_types', []).append(usage_type)
        
        # Update exclusions
        update_response = requests.post(
            PROFILES_API_URL,
            headers={'X-API-Secret': api_secret, 'Content-Type': 'application/json'},
            json={
                'operation': 'update_exclusions',
                'profile_name': profile,
                'record_types': exclusions_data.get('record_types', []),
                'services': exclusions_data.get('services', []),
                'line_item_types': exclusions_data.get('line_item_types', []),
                'usage_types': exclusions_data.get('usage_types', [])
            },
            timeout=10
        )
        
        if update_response.status_code == 200:
            scope = profile if profile else "global"
            click.echo(f"✓ Exclusion added to {scope} config")
            if record_type:
                click.echo(f"  Record Type: {record_type}")
            if service:
                click.echo(f"  Service: {service}")
            if line_item_type:
                click.echo(f"  Line Item Type: {line_item_type}")
            if usage_type:
                click.echo(f"  Usage Type: {usage_type}")
        else:
            raise click.ClickException(f"Failed to update exclusions: {update_response.status_code}")
    
    except requests.exceptions.RequestException as e:
        raise click.ClickException(f"API request failed: {e}")


@exclusions.command('remove')
@click.option('--record-type', help='Remove record type exclusion')
@click.option('--service', help='Remove service exclusion')
@click.option('--line-item-type', help='Remove line item type exclusion')
@click.option('--usage-type', help='Remove usage type exclusion')
@click.option('--profile', help='Remove from profile-specific exclusions (default: global)')
def remove_exclusion(record_type, service, line_item_type, usage_type, profile):
    """Remove an exclusion"""
    import requests
    
    if not any([record_type, service, line_item_type, usage_type]):
        raise click.ClickException(
            "Must specify at least one of: --record-type, --service, --line-item-type, --usage-type"
        )
    
    api_secret = get_api_secret()
    if not api_secret:
        raise click.ClickException(
            "No API secret configured.\n"
            "Run: cc configure --api-secret YOUR_SECRET"
        )
    
    # Get current exclusions
    try:
        response = requests.post(
            PROFILES_API_URL,
            headers={'X-API-Secret': api_secret, 'Content-Type': 'application/json'},
            json={'operation': 'get_exclusions', 'profile_name': profile},
            timeout=10
        )
        
        if response.status_code == 200:
            exclusions_data = response.json().get('exclusions', {})
        else:
            raise click.ClickException("No exclusions found")
        
        # Remove exclusions
        if record_type and record_type in exclusions_data.get('record_types', []):
            exclusions_data['record_types'].remove(record_type)
        
        if service and service in exclusions_data.get('services', []):
            exclusions_data['services'].remove(service)
        
        if line_item_type and line_item_type in exclusions_data.get('line_item_types', []):
            exclusions_data['line_item_types'].remove(line_item_type)
        
        if usage_type and usage_type in exclusions_data.get('usage_types', []):
            exclusions_data['usage_types'].remove(usage_type)
        
        # Update exclusions
        update_response = requests.post(
            PROFILES_API_URL,
            headers={'X-API-Secret': api_secret, 'Content-Type': 'application/json'},
            json={
                'operation': 'update_exclusions',
                'profile_name': profile,
                'record_types': exclusions_data.get('record_types', []),
                'services': exclusions_data.get('services', []),
                'line_item_types': exclusions_data.get('line_item_types', []),
                'usage_types': exclusions_data.get('usage_types', [])
            },
            timeout=10
        )
        
        if update_response.status_code == 200:
            scope = profile if profile else "global"
            click.echo(f"✓ Exclusion removed from {scope} config")
        else:
            raise click.ClickException(f"Failed to update exclusions: {update_response.status_code}")
    
    except requests.exceptions.RequestException as e:
        raise click.ClickException(f"API request failed: {e}")


@cli.command('trends-detailed')
@click.option('--profile', required=True, help='Profile name')
@click.option('--accounts', help='Comma-separated account IDs (optional, defaults to all profile accounts)')
@click.option('--services', help='Comma-separated service names (optional, defaults to top N)')
@click.option('--start-date', help='Start date (YYYY-MM-DD, defaults to 30 days before end-date)')
@click.option('--end-date', help='End date (YYYY-MM-DD, defaults to T-2)')
@click.option('--granularity', type=click.Choice(['DAILY', 'HOURLY'], case_sensitive=False), default='DAILY', help='Time granularity')
@click.option('--top-n', type=int, default=20, help='Number of top services to return')
@click.option('--filter-spikes/--no-filter-spikes', default=True, help='Filter out anomalous spikes (>100% day-over-day)')
@click.option('--spike-threshold', type=float, default=2.0, help='Spike threshold multiplier (2.0 = 100% increase)')
@click.option('--trendline', is_flag=True, help='Fit smooth trendline over spiky data (removes outliers)')
@click.option('--outlier-threshold', type=float, default=2.5, help='Standard deviations from mean to consider outlier')
@click.option('--output', default='trends_detailed.csv', help='Output CSV file')
@click.option('--chart', is_flag=True, help='Generate trend chart (PNG)')
@click.option('--json-output', is_flag=True, help='Output as JSON instead of CSV')
@click.option('--sso', help='AWS SSO profile name')
@click.option('--access-key-id', help='AWS Access Key ID')
@click.option('--secret-access-key', help='AWS Secret Access Key')
@click.option('--session-token', help='AWS Session Token')
def trends_detailed(profile, accounts, services, start_date, end_date, granularity, 
                   top_n, filter_spikes, spike_threshold, trendline, outlier_threshold,
                   output, chart, json_output,
                   sso, access_key_id, secret_access_key, session_token):
    """
    Detailed cost trends with flexible granularity and filtering.
    
    Supports:
    - Daily or Hourly granularity
    - Account filtering (specific accounts or all)
    - Service filtering (specific services or top N)
    - Spike detection and removal (one-time charges)
    - Automatic exclusions (Tax, Support, etc.)
    
    Examples:
    
      # Top 20 services for 2 specific accounts, daily, last 30 days
      cc trends-detailed --profile khoros --accounts "820054669588,180770971501" --sso khoros_umbrella
      
      # Hourly granularity for specific date range
      cc trends-detailed --profile khoros --granularity HOURLY --start-date 2025-11-01 --end-date 2025-11-05 --sso khoros_umbrella
      
      # Top 10 services with chart
      cc trends-detailed --profile khoros --top-n 10 --chart --sso khoros_umbrella
      
      # Specific services only
      cc trends-detailed --profile khoros --services "EC2,RDS,CloudWatch" --sso khoros_umbrella
    """
    import requests
    from datetime import datetime, timedelta
    
    # Load profile configuration
    config = load_profile(profile)
    config = apply_auth_options(config, sso, access_key_id, secret_access_key, session_token)
    
    # Get credentials
    from cost_calculator.executor import get_credentials_dict
    credentials = get_credentials_dict(config)
    if not credentials:
        raise click.ClickException("Failed to get AWS credentials. Check your AWS SSO session.")
    
    # Parse accounts and services
    account_list = [acc.strip() for acc in accounts.split(',')] if accounts else None
    service_list = [svc.strip() for svc in services.split(',')] if services else None
    
    # Build request
    request_data = {
        'profile': profile,
        'credentials': credentials,
        'granularity': granularity.upper(),
        'top_n': top_n,
        'filter_spikes': filter_spikes,
        'spike_threshold': spike_threshold,
        'fit_trendline': trendline,
        'outlier_threshold': outlier_threshold
    }
    
    if start_date:
        request_data['start_date'] = start_date
    if end_date:
        request_data['end_date'] = end_date
    if account_list:
        request_data['accounts'] = account_list
    if service_list:
        request_data['services'] = service_list
    
    # Get API secret
    api_secret = get_api_secret()
    if not api_secret:
        raise click.ClickException(
            "No API secret configured.\n"
            "Run: cc configure --api-secret YOUR_SECRET"
        )
    
    # Call API
    click.echo(f"Fetching {granularity.lower()} cost trends...")
    if account_list:
        click.echo(f"  Accounts: {', '.join(account_list)}")
    if service_list:
        click.echo(f"  Services: {', '.join(service_list)}")
    else:
        click.echo(f"  Top {top_n} services")
    click.echo(f"  Spike filtering: {'enabled' if filter_spikes else 'disabled'}")
    click.echo("")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/trends-detailed",
            headers={'X-API-Secret': api_secret, 'Content-Type': 'application/json'},
            json=request_data,
            timeout=300  # 5 minutes for large queries
        )
        
        if response.status_code != 200:
            raise click.ClickException(f"API call failed: {response.status_code} - {response.text}")
        
        result = response.json()
        
        if json_output:
            # Output as JSON
            click.echo(json.dumps(result, indent=2))
        else:
            # Generate CSV
            import csv
            
            with open(output, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Get all dates from first service
                if result['services']:
                    dates = sorted(result['services'][0]['daily_costs'].keys())
                    
                    # Header
                    writer.writerow(['Service', 'Total', 'Daily Avg', 'Min', 'Max'] + dates)
                    
                    # Data rows
                    for service in result['services']:
                        row = [
                            service['name'],
                            service['total'],
                            service['daily_average'],
                            service['min'],
                            service['max']
                        ]
                        row.extend([service['daily_costs'].get(date, 0.0) for date in dates])
                        writer.writerow(row)
            
            click.echo(f"✓ Trends data saved to {output}")
            
            # Show summary
            summary = result['summary']
            click.echo("")
            click.echo(f"Total Cost: ${summary['total_cost']:,.2f}")
            click.echo(f"Daily Average: ${summary['daily_average']:,.2f}")
            click.echo(f"Services: {summary['num_services']}")
            click.echo(f"Periods: {summary['num_periods']}")
            
            # Show share_id if available
            if 'share_id' in result:
                click.echo("")
                click.echo(f"💾 Share ID: {result['share_id']}")
                click.echo(f"   To share: cc share --id {result['share_id']}")
            
            # Generate chart if requested
            if chart:
                try:
                    import matplotlib.pyplot as plt
                    import matplotlib.dates as mdates
                    from datetime import datetime as dt
                    
                    chart_file = output.replace('.csv', '.png')
                    
                    # Prepare data
                    dates = sorted(result['services'][0]['daily_costs'].keys())
                    date_objects = [dt.fromisoformat(d) for d in dates]
                    
                    # Create plot
                    fig, ax = plt.subplots(figsize=(16, 10))
                    
                    for service in result['services'][:10]:  # Top 10 only
                        costs = [service['daily_costs'].get(date, 0.0) for date in dates]
                        
                        if trendline and 'trendline' in service:
                            # Plot raw data with lighter color and smaller markers
                            line = ax.plot(date_objects, costs, marker='o', alpha=0.3, 
                                         linewidth=1, markersize=3, linestyle='--')[0]
                            # Plot trendline with same color but bolder
                            trendline_costs = [service['trendline'].get(date, 0.0) for date in dates]
                            ax.plot(date_objects, trendline_costs, color=line.get_color(),
                                  label=service['name'], linewidth=3, markersize=0)
                        else:
                            # Plot raw data only
                            ax.plot(date_objects, costs, marker='o', label=service['name'], 
                                  linewidth=2, markersize=4)
                    
                    title = f'Top 10 Services - {granularity.title()} Cost Trends'
                    if trendline:
                        title += ' (with Fitted Trendlines)'
                    title += f"\nAccounts: {', '.join(account_list) if account_list else 'All'}"
                    ax.set_title(title, fontsize=14, fontweight='bold')
                    ax.set_xlabel('Date', fontsize=12)
                    ax.set_ylabel(f'{granularity.title()} Cost ($)', fontsize=12)
                    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=9)
                    
                    # Add granular Y-axis gridlines
                    from matplotlib.ticker import MultipleLocator
                    ax.yaxis.set_major_locator(MultipleLocator(500))  # Major gridlines every $500
                    ax.yaxis.set_minor_locator(MultipleLocator(100))  # Minor gridlines every $100
                    ax.grid(True, which='major', alpha=0.4, linewidth=0.8)
                    ax.grid(True, which='minor', alpha=0.2, linewidth=0.4)
                    
                    if granularity == 'DAILY':
                        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//15)))
                    else:
                        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
                        ax.xaxis.set_major_locator(mdates.HourLocator(interval=max(1, len(dates)//15)))
                    
                    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
                    plt.tight_layout()
                    plt.savefig(chart_file, dpi=150, bbox_inches='tight')
                    
                    click.echo(f"✓ Chart saved to {chart_file}")
                except ImportError:
                    click.echo("⚠ matplotlib not installed, skipping chart generation")
    
    except requests.exceptions.RequestException as e:
        raise click.ClickException(f"API request failed: {e}")


@cli.command('daily-report')
@click.option('--profile', required=True, help='Profile name')
@click.option('--offset', default=2, help='Days back from today (default: 2 = T-2)')
@click.option('--window', default=30, help='Number of days to query (default: 30)')
@click.option('--top-services', default=20, help='Number of top services to include (default: 20)')
@click.option('--top-accounts', default=5, help='Number of top accounts to include (default: 5)')
@click.option('--share', is_flag=True, help='Generate shareable chart URL')
@click.option('--sso', help='AWS SSO profile to use')
@click.option('--access-key-id', help='AWS Access Key ID')
@click.option('--secret-access-key', help='AWS Secret Access Key')
@click.option('--session-token', help='AWS Session Token')
def daily_report(profile, offset, window, top_services, top_accounts, share, sso, access_key_id, secret_access_key, session_token):
    """
    Generate unified daily cost report for all accounts and services.
    
    This command queries AWS Cost Explorer day-by-day to retrieve comprehensive
    cost data across all accounts and services in your profile. Unlike other
    commands that aggregate data, this provides granular daily breakdowns perfect
    for creating interactive visualizations and detailed cost analysis.
    
    \b
    KEY FEATURES:
    • Day-by-day Cost Explorer queries for complete data coverage
    • All accounts × all services cost breakdown
    • Configurable date ranges (offset + window pattern)
    • Interactive shareable charts with --share flag
    • Top N accounts and services filtering
    • Automatic exclusions (Tax, Support, OCBLateFee)
    
    \b
    HOW IT WORKS:
    1. Loads profile from backend (accounts, exclusions, config)
    2. Queries Cost Explorer once per day in the date range
    3. Aggregates costs by account, service, and date
    4. Returns unified data structure for visualization
    5. Optionally uploads to S3 for shareable chart URL
    
    \b
    DATE RANGE:
    • offset: Days back from today (default: 2 = T-2)
      - Avoids incomplete data from recent days
      - T-2 means "2 days ago"
    • window: Number of days to analyze (default: 30)
      - Total days = window (e.g., 30 days)
      - Date range: (today - offset - window) to (today - offset)
    
    \b
    OUTPUT INCLUDES:
    • Date range and days with actual data
    • Total cost and daily average across all accounts
    • Top N accounts by total cost (default: 5)
    • Top N services by total cost (default: 20)
    • Daily cost breakdown for each account × service combination
    • Metadata: total accounts, total services, exclusions applied
    
    \b
    SHAREABLE CHARTS (--share):
    • Uploads data to S3 bucket
    • Generates unique chart URL
    • Interactive visualization with:
      - Account pills (TOTAL + top accounts)
      - Service pills (Daily Total Cost + top services)
      - Click to filter by account/service
      - Zoom/pan timeline
      - Live stats and highlighting
    
    \b
    EXAMPLES:
    
    Basic usage - last 30 days:
        cc daily-report --profile khoros --sso my_sso_profile
    
    Custom date range - 60 days:
        cc daily-report --profile khoros --sso my_sso_profile --window 60
    
    From Oct 1 to Nov 9 (40 days):
        cc daily-report --profile khoros --sso my_sso_profile --offset 2 --window 40
    
    Generate shareable chart:
        cc daily-report --profile khoros --sso my_sso_profile --share
    
    More accounts and services:
        cc daily-report --profile khoros --sso my_sso_profile \\
            --top-accounts 10 --top-services 30
    
    With static credentials:
        cc daily-report --profile khoros \\
            --access-key-id ASIA... \\
            --secret-access-key ... \\
            --session-token ...
    
    \b
    PERFORMANCE:
    • Queries: 1 per day in window (e.g., 30 queries for 30 days)
    • Duration: ~4 seconds per day (~2 minutes for 30 days)
    • Data size: ~100-200KB for 30 days × 48 accounts × 20 services
    • Caching: Backend caches profile data, frontend caches chart data
    
    \b
    USE CASES:
    • Track daily cost trends across all accounts
    • Identify cost spikes on specific dates
    • Compare account spending patterns
    • Share interactive cost visualizations with stakeholders
    • Export comprehensive data for custom analysis
    • Monitor service-level cost changes over time
    
    \b
    NOTES:
    • Requires AWS credentials with Cost Explorer read access
    • Profile must exist in backend DynamoDB
    • --share requires S3 write access to chart bucket
    • Data excludes Tax, Support, and OCBLateFee by default
    • Uses UnblendedCost metric from Cost Explorer
    """
    from cost_calculator.executor import get_credentials_dict
    from cost_calculator.api_client import call_lambda_api
    import requests
    import json
    
    try:
        # Load profile config
        config = {'profile_name': profile}
        config = apply_auth_options(config, sso, access_key_id, secret_access_key, session_token)
        
        # Get credentials
        credentials = get_credentials_dict(config)
        if not credentials:
            raise click.ClickException("Failed to get AWS credentials. Check your AWS SSO session.")
        
        # Calculate date range for display
        from datetime import datetime, timedelta
        end_date = (datetime.now() - timedelta(days=offset)).strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=offset + window)).strftime('%Y-%m-%d')
        
        click.echo(f"Fetching daily cost data for {profile}...")
        click.echo(f"Date range: {start_date} to {end_date} ({window} days)")
        click.echo(f"This will take ~{window * 4} seconds ({window} queries)...")
        click.echo("")
        
        # Call API
        result = call_lambda_api(
            'daily-report',
            credentials,
            profile=profile,
            offset=offset,
            window=window,
            top_services=top_services,
            top_accounts=top_accounts
        )
        
        # Display summary
        click.echo("✅ Daily Report Generated")
        click.echo("")
        click.echo(f"📊 Summary:")
        click.echo(f"  Date Range: {result['metadata']['date_range']}")
        click.echo(f"  Days with Data: {len(result['metadata']['dates_with_data'])}")
        click.echo(f"  Total Cost: ${result['summary']['total_cost']:,.2f}")
        click.echo(f"  Daily Average: ${result['summary']['daily_average']:,.2f}")
        click.echo(f"  Total Accounts: {result['metadata']['total_accounts']}")
        click.echo(f"  Total Services: {result['metadata']['total_services']}")
        click.echo("")
        
        click.echo(f"🏢 Top Accounts:")
        for acc in result['metadata']['accounts'][:6]:
            if acc == 'TOTAL':
                click.echo(f"  • {acc} (All accounts aggregated)")
            else:
                click.echo(f"  • {acc}")
        click.echo("")
        
        click.echo(f"⚙️  Top Services:")
        for svc in result['metadata']['services'][:6]:
            click.echo(f"  • {svc}")
        click.echo("")
        
        # Generate shareable chart if requested
        if share:
            import hashlib
            import os
            
            click.echo("Generating shareable chart...")
            
            # Generate share ID
            share_id = hashlib.md5(os.urandom(16)).hexdigest()[:12]
            
            # Upload to S3
            import boto3
            s3_session = boto3.Session(profile_name=sso) if sso else boto3.Session()
            s3_client = s3_session.client('s3')
            
            s3_client.put_object(
                Bucket='chart.costcop.cloudfix.dev',
                Key=f'data/{share_id}.json',
                Body=json.dumps(result),
                ContentType='application/json',
                CacheControl='public, max-age=3600'
            )
            
            chart_url = f"http://chart.costcop.cloudfix.dev.s3-website-us-east-1.amazonaws.com/?id={share_id}"
            click.echo("")
            click.echo("✅ Shareable Chart Created!")
            click.echo("")
            click.echo(f"🔗 Chart URL:")
            click.echo(f"   {chart_url}")
            click.echo("")
            click.echo("📊 Features:")
            click.echo("  • Interactive account and service pills")
            click.echo("  • Click TOTAL + Daily Total Cost = All accounts, all services")
            click.echo("  • Click account + service = Specific combination")
            click.echo("  • Zoom/pan with live stats")
            click.echo("  • Service pill highlighting")
        
    except Exception as e:
        raise click.ClickException(f"Daily report failed: {e}")


@cli.command('info')
@click.option('--command', help='Get detailed help for a specific command')
@click.option('--list-commands', is_flag=True, help='List all available commands')
@click.option('--category', help='List commands in a category (core, analysis, management, advanced, setup)')
@click.option('--json-output', is_flag=True, help='Output as JSON for programmatic access')
@click.option('--examples', is_flag=True, help='Show detailed examples')
def info(command, list_commands, category, json_output, examples):
    """
    Get comprehensive help and examples for CLI commands.
    
    This command provides detailed documentation, examples, and usage patterns
    for all CLI commands. Perfect for both human users and AI agents to discover
    and understand all functionality.
    
    Examples:
    
      # List all commands
      cc info --list-commands
      
      # Get detailed help for a command
      cc info --command calculate
      
      # Get examples for a command
      cc info --command trends-detailed --examples
      
      # List commands by category
      cc info --category core
      
      # Get all help as JSON (for AI agents)
      cc info --json-output
      
      # Get specific command help as JSON
      cc info --command calculate --json-output
    """
    from cost_calculator.help_content import (
        get_command_help,
        get_all_commands,
        get_commands_by_category,
        format_examples,
        get_all_examples_json,
        COMMAND_CATEGORIES
    )
    import json
    
    # List all commands
    if list_commands:
        if json_output:
            output = {
                'commands': get_all_commands(),
                'categories': COMMAND_CATEGORIES
            }
            click.echo(json.dumps(output, indent=2))
        else:
            click.echo("\n=== Available Commands ===\n")
            for cat, cmds in COMMAND_CATEGORIES.items():
                click.echo(f"\n{cat.upper()}:")
                for cmd in cmds:
                    help_data = get_command_help(cmd)
                    short_desc = help_data.get('short', 'No description')
                    click.echo(f"  {cmd:<20} {short_desc}")
        return
    
    # List commands by category
    if category:
        cmds = get_commands_by_category(category)
        if not cmds:
            click.echo(f"Unknown category: {category}")
            click.echo(f"Available categories: {', '.join(COMMAND_CATEGORIES.keys())}")
            return
        
        if json_output:
            output = {
                'category': category,
                'commands': [
                    {
                        'name': cmd,
                        'help': get_command_help(cmd)
                    }
                    for cmd in cmds
                ]
            }
            click.echo(json.dumps(output, indent=2))
        else:
            click.echo(f"\n=== {category.upper()} Commands ===\n")
            for cmd in cmds:
                help_data = get_command_help(cmd)
                click.echo(f"\n{cmd}")
                click.echo(f"  {help_data.get('short', 'No description')}")
        return
    
    # Get help for specific command
    if command:
        help_data = get_command_help(command)
        if not help_data:
            click.echo(f"No help available for command: {command}")
            click.echo(f"\nAvailable commands: {', '.join(get_all_commands())}")
            return
        
        if json_output:
            click.echo(json.dumps({command: help_data}, indent=2))
        elif examples:
            click.echo(format_examples(command))
        else:
            # Show concise help
            click.echo(f"\n=== {command} ===\n")
            click.echo(help_data.get('long', ''))
            click.echo(f"\nFor detailed examples, run: cc info --command {command} --examples")
        return
    
    # Default: show all help as JSON or summary
    if json_output:
        click.echo(json.dumps(get_all_examples_json(), indent=2))
    else:
        click.echo("\n=== AWS Cost Calculator - Comprehensive Help ===\n")
        click.echo("Get detailed help and examples for any command.\n")
        click.echo("Usage:")
        click.echo("  cc info --list-commands              # List all commands")
        click.echo("  cc info --command COMMAND            # Get help for a command")
        click.echo("  cc info --command COMMAND --examples # Get detailed examples")
        click.echo("  cc info --category CATEGORY          # List commands by category")
        click.echo("  cc info --json-output                # Get all help as JSON")
        click.echo("\nCategories:")
        for cat in COMMAND_CATEGORIES.keys():
            click.echo(f"  - {cat}")
        click.echo("\nFor AI agents: Use --json-output for programmatic access to all help content.")


@cli.command('share')
@click.option('--id', 'share_id', required=True, help='Share ID from previous analysis command')
@click.option('--title', help='Title for the shared chart')
@click.option('--description', help='Optional description')
def share(share_id, title, description):
    """
    Create a shareable interactive chart link.
    
    After running any analysis command (trends-detailed, calculate, etc.),
    use the share_id to create a public, interactive chart that can be
    shared with anyone via URL.
    
    Examples:
    
      # Basic share
      cc share --id abc123
      
      # With title
      cc share --id abc123 --title "Q4 Cost Analysis"
      
      # With description
      cc share --id abc123 --title "Q4 Analysis" --description "Cost spike investigation"
    
    The generated URL will point to an interactive React app where viewers can:
    - Toggle services on/off
    - Zoom in/out
    - Filter by date range
    - Export data
    
    No authentication required to view the shared chart.
    """
    import requests
    
    try:
        # Get API secret
        api_secret = os.environ.get('COST_API_SECRET')
        if not api_secret:
            # Try to load from config
            config_file = os.path.expanduser('~/.config/cost-calculator/config.json')
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    api_secret = config.get('api_secret')
        
        if not api_secret:
            raise click.ClickException(
                "No API secret configured.\n"
                "Run: cc configure --api-secret YOUR_SECRET\n"
                "Or set environment variable: export COST_API_SECRET=YOUR_SECRET"
            )
        
        # Call share API endpoint
        share_api_url = "https://api.costcop.cloudfix.dev/share"
        
        click.echo(f"Creating shareable link for {share_id}...")
        
        response = requests.post(
            share_api_url,
            headers={
                'X-API-Secret': api_secret,
                'Content-Type': 'application/json'
            },
            json={
                'share_id': share_id,
                'title': title or 'Cost Analysis',
                'description': description or ''
            },
            timeout=30
        )
        
        if response.status_code == 404:
            raise click.ClickException(
                f"Share ID '{share_id}' not found.\n"
                f"Make sure you've run an analysis command first and copied the correct share_id."
            )
        elif response.status_code == 401:
            raise click.ClickException("Invalid API secret")
        elif response.status_code != 200:
            error_msg = response.json().get('error', 'Unknown error')
            raise click.ClickException(f"Failed to create share: {error_msg}")
        
        result = response.json()
        
        click.echo("\n" + "="*60)
        click.echo("✅ Shareable link created!")
        click.echo("="*60)
        click.echo(f"\n🔗 Share URL:")
        click.echo(f"   {result['share_url']}")
        click.echo(f"\n📊 Features:")
        click.echo("   • Interactive chart with filters")
        click.echo("   • Toggle services on/off")
        click.echo("   • Zoom and pan")
        click.echo("   • No authentication required")
        click.echo(f"\n📝 Title: {result.get('title', 'N/A')}")
        click.echo(f"🆔 Share ID: {result['share_id']}")
        click.echo(f"📅 Created: {result.get('created_at', 'N/A')}")
        click.echo("\n" + "="*60)
        
    except requests.exceptions.RequestException as e:
        raise click.ClickException(f"API request failed: {e}")


if __name__ == '__main__':
    cli()

"""
Comprehensive help content and examples for all CLI commands.

This module provides detailed documentation and examples for each command,
enabling both human users and AI agents to discover and understand all functionality.
"""

# Command categories for organization
COMMAND_CATEGORIES = {
    'core': ['calculate', 'daily', 'trends', 'monthly'],
    'analysis': ['analyze', 'drill', 'compare', 'investigate'],
    'management': ['profile', 'configure', 'exclusions'],
    'advanced': ['trends-detailed', 'query', 'tags', 'forensics'],
    'setup': ['setup-api', 'setup-cur', 'list-profiles']
}

# Detailed help content for each command
COMMAND_HELP = {
    'calculate': {
        'short': 'Calculate AWS costs for a specific period',
        'long': '''Calculate total AWS costs across all accounts in a profile for a specified time period.
        
This is the primary command for getting quick cost totals. It uses AWS Cost Explorer
to retrieve unblended costs and can output results in markdown or JSON format.

The command defaults to T-2 (2 days ago) to avoid incomplete data from Cost Explorer's lag.''',
        'examples': [
            {
                'title': 'Basic cost calculation (last 30 days, T-2)',
                'command': 'cc calculate --profile myprofile --sso my_sso_profile',
                'description': 'Calculate costs for the last 30 days, ending 2 days ago'
            },
            {
                'title': 'Specific date range',
                'command': 'cc calculate --profile myprofile --sso my_sso_profile --start-date 2025-11-01 --end-date 2025-11-10',
                'description': 'Calculate costs for a specific date range'
            },
            {
                'title': 'Custom offset and window',
                'command': 'cc calculate --profile myprofile --sso my_sso_profile --offset 5 --window 60',
                'description': 'Calculate costs for 60 days, ending 5 days ago'
            },
            {
                'title': 'JSON output for automation',
                'command': 'cc calculate --profile myprofile --sso my_sso_profile --json-output',
                'description': 'Output results as JSON for parsing by scripts'
            },
            {
                'title': 'Save to custom file',
                'command': 'cc calculate --profile myprofile --sso my_sso_profile --output costs_nov.md',
                'description': 'Save markdown report to a specific file'
            },
            {
                'title': 'Using static credentials',
                'command': 'cc calculate --profile myprofile --access-key-id ASIA... --secret-access-key ... --session-token ...',
                'description': 'Use static AWS credentials instead of SSO'
            },
            {
                'title': 'Using environment variables',
                'command': 'export AWS_PROFILE=my_sso && cc calculate --profile myprofile',
                'description': 'Use AWS credentials from environment variables'
            }
        ],
        'parameters': {
            '--profile': 'Profile name (required) - must exist in backend DynamoDB',
            '--sso': 'AWS SSO profile name for authentication',
            '--access-key-id': 'AWS access key ID (alternative to SSO)',
            '--secret-access-key': 'AWS secret access key (alternative to SSO)',
            '--session-token': 'AWS session token (for temporary credentials)',
            '--start-date': 'Start date (YYYY-MM-DD format)',
            '--end-date': 'End date (YYYY-MM-DD format)',
            '--offset': 'Days to offset from today (default: 2 for T-2)',
            '--window': 'Number of days to analyze (default: 30)',
            '--output': 'Output file path (default: cost_report.md)',
            '--json-output': 'Output as JSON instead of markdown'
        },
        'notes': [
            'Cost Explorer has a 24-48 hour lag, so T-2 (offset=2) is recommended',
            'All costs are unblended costs (actual costs paid)',
            'Costs are aggregated across all accounts in the profile',
            'Exclusions configured in the profile are automatically applied'
        ]
    },
    
    'trends-detailed': {
        'short': 'Detailed cost trends with flexible granularity and filtering',
        'long': '''Analyze cost trends with daily or hourly granularity, advanced filtering, and trendline fitting.

This command provides the most flexible cost trend analysis with:
- Daily or Hourly granularity
- Account-level filtering
- Service-level filtering  
- Spike detection and removal
- Trendline fitting for smooth visualization
- Automatic exclusions (Tax, Support, Credits, etc.)

Perfect for detailed cost investigation and trend analysis.''',
        'examples': [
            {
                'title': 'Top 20 services for specific accounts',
                'command': 'cc trends-detailed --profile khoros --accounts "820054669588,180770971501" --sso khoros_umbrella --chart',
                'description': 'Analyze top 20 services for two specific accounts with chart visualization'
            },
            {
                'title': 'With smooth trendlines',
                'command': 'cc trends-detailed --profile khoros --accounts "820054669588,180770971501" --trendline --chart --sso khoros_umbrella',
                'description': 'Add fitted trendlines to remove spikes and show smooth trends'
            },
            {
                'title': 'Top 10 services only',
                'command': 'cc trends-detailed --profile khoros --top-n 10 --sso khoros_umbrella',
                'description': 'Limit analysis to top 10 services by cost'
            },
            {
                'title': 'Specific services',
                'command': 'cc trends-detailed --profile khoros --services "EC2 - Other,Amazon RDS,CloudWatch" --sso khoros_umbrella',
                'description': 'Analyze only specific services'
            },
            {
                'title': 'Custom date range',
                'command': 'cc trends-detailed --profile khoros --start-date 2025-11-01 --end-date 2025-11-15 --sso khoros_umbrella',
                'description': 'Analyze a specific date range'
            },
            {
                'title': 'Hourly granularity (future)',
                'command': 'cc trends-detailed --profile khoros --granularity HOURLY --start-date 2025-11-01 --end-date 2025-11-02 --sso khoros_umbrella',
                'description': 'Hourly cost breakdown (requires Athena/CUR setup)'
            },
            {
                'title': 'No spike filtering',
                'command': 'cc trends-detailed --profile khoros --no-filter-spikes --sso khoros_umbrella',
                'description': 'Include all charges including one-time spikes'
            },
            {
                'title': 'Aggressive outlier removal',
                'command': 'cc trends-detailed --profile khoros --trendline --outlier-threshold 1.5 --sso khoros_umbrella',
                'description': 'More aggressive outlier detection (1.5 std devs instead of 2.5)'
            },
            {
                'title': 'JSON output for automation',
                'command': 'cc trends-detailed --profile khoros --json-output --sso khoros_umbrella',
                'description': 'Output as JSON for programmatic processing'
            }
        ],
        'parameters': {
            '--profile': 'Profile name (required)',
            '--accounts': 'Comma-separated account IDs (optional, defaults to all)',
            '--services': 'Comma-separated service names (optional, defaults to top N)',
            '--start-date': 'Start date YYYY-MM-DD (defaults to 30 days before end)',
            '--end-date': 'End date YYYY-MM-DD (defaults to T-2)',
            '--granularity': 'DAILY or HOURLY (default: DAILY)',
            '--top-n': 'Number of top services (default: 20)',
            '--filter-spikes': 'Filter anomalous spikes >100% day-over-day (default: true)',
            '--spike-threshold': 'Spike threshold multiplier (default: 2.0 = 100%)',
            '--trendline': 'Fit smooth trendline over spiky data',
            '--outlier-threshold': 'Std devs from mean for outlier detection (default: 2.5)',
            '--output': 'Output CSV file (default: trends_detailed.csv)',
            '--chart': 'Generate PNG chart visualization',
            '--json-output': 'Output as JSON instead of CSV'
        },
        'notes': [
            'Automatically excludes Tax, Support, Credits, Refunds, Savings Plans',
            'Spike filtering removes one-time charges like monthly tax',
            'Trendline fitting uses outlier detection + moving average smoothing',
            'Chart shows raw data (faded) and trendline (bold) when --trendline is used',
            'Hourly granularity requires CUR (Cost and Usage Report) setup'
        ]
    },
    
    'daily': {
        'short': 'Get daily cost breakdown with granular detail',
        'long': '''Retrieve daily cost breakdowns grouped by service, account, or other dimensions.

This command provides day-by-day cost details, useful for identifying specific days
with cost spikes or unusual patterns.''',
        'examples': [
            {
                'title': 'Daily costs for last 7 days',
                'command': 'cc daily --profile myprofile --days 7 --sso my_sso_profile',
                'description': 'Get daily breakdown for the past week'
            },
            {
                'title': 'Daily costs by service',
                'command': 'cc daily --profile myprofile --days 30 --group-by SERVICE --sso my_sso_profile',
                'description': 'Group daily costs by AWS service'
            },
            {
                'title': 'Daily costs by account',
                'command': 'cc daily --profile myprofile --days 30 --group-by ACCOUNT --sso my_sso_profile',
                'description': 'Group daily costs by AWS account'
            },
            {
                'title': 'Specific account only',
                'command': 'cc daily --profile myprofile --account 123456789012 --days 30 --sso my_sso_profile',
                'description': 'Daily costs for a single account'
            },
            {
                'title': 'JSON output',
                'command': 'cc daily --profile myprofile --days 7 --json-output --sso my_sso_profile',
                'description': 'Output as JSON for automation'
            }
        ],
        'parameters': {
            '--profile': 'Profile name (required)',
            '--days': 'Number of days to analyze (default: 7)',
            '--group-by': 'Grouping dimension: SERVICE, ACCOUNT, REGION, etc.',
            '--account': 'Filter by specific account ID',
            '--json-output': 'Output as JSON'
        },
        'notes': [
            'Uses Cost Explorer API with daily granularity',
            'Subject to Cost Explorer 24-48 hour lag',
            'Useful for identifying specific days with cost anomalies'
        ]
    },
    
    'analyze': {
        'short': 'Perform pandas-based analysis (aggregations, volatility, trends)',
        'long': '''Advanced cost analysis using pandas for statistical operations.

Provides multiple analysis types:
- summary: Aggregate statistics
- volatility: Cost variance and volatility metrics
- trends: Trend detection and forecasting
- search: Search for services matching patterns''',
        'examples': [
            {
                'title': 'Summary statistics',
                'command': 'cc analyze --profile myprofile --type summary --sso my_sso_profile',
                'description': 'Get aggregate cost statistics'
            },
            {
                'title': 'Volatility analysis',
                'command': 'cc analyze --profile myprofile --type volatility --weeks 12 --sso my_sso_profile',
                'description': 'Analyze cost volatility over 12 weeks'
            },
            {
                'title': 'Trend analysis',
                'command': 'cc analyze --profile myprofile --type trends --weeks 8 --sso my_sso_profile',
                'description': 'Detect cost trends over 8 weeks'
            },
            {
                'title': 'Search for services',
                'command': 'cc analyze --profile myprofile --type search --pattern "EC2" --min-cost 100 --sso my_sso_profile',
                'description': 'Find services matching pattern with minimum cost threshold'
            }
        ],
        'parameters': {
            '--profile': 'Profile name (required)',
            '--type': 'Analysis type: summary, volatility, trends, search',
            '--weeks': 'Number of weeks to analyze (default: 12)',
            '--pattern': 'Service search pattern (for search type)',
            '--min-cost': 'Minimum cost filter (for search type)',
            '--json-output': 'Output as JSON'
        },
        'notes': [
            'Uses pandas for advanced statistical analysis',
            'Requires sufficient historical data for meaningful results',
            'Volatility metrics help identify unstable cost patterns'
        ]
    },
    
    'profile': {
        'short': 'Manage profiles (CRUD operations)',
        'long': '''Create, read, update, and delete cost calculator profiles.

Profiles are stored in DynamoDB and contain:
- Account IDs to analyze
- AWS credentials configuration
- Exclusion rules
- Default settings''',
        'examples': [
            {
                'title': 'Create new profile',
                'command': 'cc profile create --name myprofile --accounts "123456789012,987654321098" --aws-profile my_sso',
                'description': 'Create a new profile with accounts'
            },
            {
                'title': 'List all profiles',
                'command': 'cc profile list',
                'description': 'Show all available profiles'
            },
            {
                'title': 'Get profile details',
                'command': 'cc profile get --name myprofile',
                'description': 'Show detailed profile configuration'
            },
            {
                'title': 'Update profile accounts',
                'command': 'cc profile update --name myprofile --accounts "111,222,333"',
                'description': 'Update the accounts in a profile'
            },
            {
                'title': 'Delete profile',
                'command': 'cc profile delete --name myprofile',
                'description': 'Remove a profile from DynamoDB'
            }
        ],
        'parameters': {
            '--name': 'Profile name',
            '--accounts': 'Comma-separated account IDs',
            '--aws-profile': 'AWS SSO profile name',
            '--description': 'Profile description'
        },
        'notes': [
            'Profiles are stored in DynamoDB (backend)',
            'All commands use profiles to know which accounts to analyze',
            'Profiles can include exclusion rules for filtering costs'
        ]
    }
}

# Add more commands...
# (I'll continue with the rest in the next part)

def get_command_help(command_name):
    """Get detailed help for a specific command."""
    return COMMAND_HELP.get(command_name, {})

def get_all_commands():
    """Get list of all available commands."""
    return list(COMMAND_HELP.keys())

def get_commands_by_category(category):
    """Get commands in a specific category."""
    return COMMAND_CATEGORIES.get(category, [])

def format_examples(command_name):
    """Format examples for a command as markdown."""
    help_data = get_command_help(command_name)
    if not help_data or 'examples' not in help_data:
        return "No examples available."
    
    output = []
    output.append(f"\n# Examples for '{command_name}'\n")
    output.append(help_data.get('long', ''))
    output.append("\n## Examples:\n")
    
    for i, example in enumerate(help_data['examples'], 1):
        output.append(f"\n### {i}. {example['title']}")
        output.append(f"\n```bash\n{example['command']}\n```")
        output.append(f"\n{example['description']}\n")
    
    if 'parameters' in help_data:
        output.append("\n## Parameters:\n")
        for param, desc in help_data['parameters'].items():
            output.append(f"- **{param}**: {desc}")
    
    if 'notes' in help_data:
        output.append("\n## Notes:\n")
        for note in help_data['notes']:
            output.append(f"- {note}")
    
    return '\n'.join(output)

def get_all_examples_json():
    """Get all examples in JSON format for programmatic access."""
    return {
        'commands': COMMAND_HELP,
        'categories': COMMAND_CATEGORIES
    }

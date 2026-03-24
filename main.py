from __future__ import print_function
import sys, warnings
import argparse
import logging
from datetime import datetime
import deepsecurity
from deepsecurity.rest import ApiException
from pprint import pprint


import os
from dotenv import load_dotenv

load_dotenv()

# Check for API key
api_key = os.getenv("V1WS_API_KEY")

if not api_key:
    print("ERROR: API key not found!")
    print("Please set up your environment variables:")
    print("1. Create a .env file in this directory")
    print("2. Add your API key: V1WS_API_KEY=your_api_key_here")
    print("3. Get your API key from Deep Security Manager > Administration > API Keys")
    sys.exit(1)

# Configure pretty logging
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format: [TIMESTAMP] [LEVEL] MESSAGE
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted = f"[{timestamp}] [{log_color}{record.levelname}{reset}] {record.getMessage()}"
        return formatted

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter())
logger.addHandler(handler)

def log_info(message):
    logger.info(message)

def log_warning(message):
    logger.warning(message)

def log_error(message):
    logger.error(message)

def log_success(message):
    logger.info(f"✅ {message}")

def log_processing(message):
    logger.info(f"⏳ {message}")

def log_found(message):
    logger.info(f"🔍 {message}")

if not sys.warnoptions:
	warnings.simplefilter("ignore")
configuration = deepsecurity.Configuration()
#
# United States	    https://workload.us-1.cloudone.trendmicro.com/api
# Australia.  	    https://workload.au-1.cloudone.trendmicro.com/api
# Germany (EU)	    https://workload.de-1.cloudone.trendmicro.com/api
# Singapore 	    https://workload.sg-1.cloudone.trendmicro.com/api
# India	            https://workload.in-1.cloudone.trendmicro.com/api
# Japan	            https://workload.jp-1.cloudone.trendmicro.com/api
# Canada	        https://workload.ca-1.cloudone.trendmicro.com/api
# United Kingdom	https://workload.gb-1.cloudone.trendmicro.com/api
# 
# Note: configuration.host will be set dynamically based on --region parameter


# Authentication
configuration.api_key['api-secret-key'] = api_key

# Region mapping
REGION_HOSTS = {
    'us': 'https://workload.us-1.cloudone.trendmicro.com/api',
    'au': 'https://workload.au-1.cloudone.trendmicro.com/api', 
    'de': 'https://workload.de-1.cloudone.trendmicro.com/api',
    'sg': 'https://workload.sg-1.cloudone.trendmicro.com/api',
    'in': 'https://workload.in-1.cloudone.trendmicro.com/api',
    'jp': 'https://workload.jp-1.cloudone.trendmicro.com/api',
    'ca': 'https://workload.ca-1.cloudone.trendmicro.com/api',
    'gb': 'https://workload.gb-1.cloudone.trendmicro.com/api',
    'trend': 'https://workload.trend-us-1.cloudone.trendmicro.com/api'
}

REGION_NAMES = {
    'us': 'United States',
    'au': 'Australia', 
    'de': 'Germany (EU)',
    'sg': 'Singapore',
    'in': 'India',
    'jp': 'Japan',
    'ca': 'Canada',
    'gb': 'United Kingdom',
    'trend': 'Trend US'
}


def iterate_computers(configuration):
    log_processing("Fetching computers from Deep Security...")
    api_instance = deepsecurity.ComputersApi(deepsecurity.ApiClient(configuration))
    api_version = 'v1'
    expand_options = deepsecurity.Expand()
    expand_options.add(expand_options.none)
    expand = expand_options.list()
    overrides = False
    api_response = api_instance.list_computers(api_version, expand=expand, overrides=overrides)
    computer_count = len(api_response.computers)
    log_success(f"Found {computer_count} computers")
    for computer in api_response.computers:
        yield computer.id

def iterate_device_ids(configuration):
    device_count = 0
    for computer_id in iterate_computers(configuration):
        log_processing(f"Processing computer {computer_id}")
        api_instance = deepsecurity.ComputerDeviceControlExceptionRulesApi(deepsecurity.ApiClient(configuration))
        api_version = 'v1'
        overrides = False
        api_response = api_instance.list_exception_rules_on_computer(computer_id, api_version, overrides=overrides)
        computer_device_count = len(api_response.exception_rules)
        if computer_device_count > 0:
            log_found(f"Found {computer_device_count} device exceptions on computer {computer_id}")
        for exception in api_response.exception_rules:
            device_count += 1
            yield exception.device_id
    log_success(f"Total unique device IDs found: {device_count}")


def add_exception_rule(configuration, policy_id, exception_rules):
    rule_count = len(exception_rules.exception_rules)
    log_processing(f"Adding {rule_count} exception rules to policy {policy_id}")
    api_instance = deepsecurity.PolicyDeviceControlExceptionRulesApi(deepsecurity.ApiClient(configuration))
    api_version = 'v1'
    overrides = False
    try:
        api_response = api_instance.add_exception_rules_on_policy(policy_id, exception_rules, api_version, overrides=overrides)
        log_success(f"Successfully added {rule_count} exception rules to policy {policy_id}")
        return api_response
    except ApiException as e:
        log_error(f"Failed to add exception rules to policy {policy_id}: {e}")
        return None

def main():
    # Create help text with region list
    region_help = "Deep Security region. Available regions:\n"
    for code, name in REGION_NAMES.items():
        region_help += f"  {code}: {name}\n"
    region_help += "Default: us"
    
    parser = argparse.ArgumentParser(
        description='Add USB device exception rules to a policy',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--policy-id', type=int, required=True, 
                       help='Policy ID to add exception rules to')
    parser.add_argument('--region', type=str, default='us', choices=REGION_HOSTS.keys(),
                       help=region_help)
    
    try:
        args = parser.parse_args()
    except SystemExit:
        # When -h is used or argument error occurs, show help with regions
        print("\nAvailable regions:")
        for code, name in REGION_NAMES.items():
            print(f"  --region {code}: {name}")
        sys.exit(1)
    
    # Set configuration host based on region
    configuration.host = REGION_HOSTS[args.region]
    log_info(f"Using region: {REGION_NAMES[args.region]} ({args.region})")
    
    log_info(f"Starting USB device exception rule collection for policy {args.policy_id}")
    
    device_ids = set()
    for device_id in iterate_device_ids(configuration):
        device_ids.add(device_id)

    log_info(f"Creating exception rules for {len(device_ids)} unique devices")
    exception_rules = deepsecurity.ExceptionRules()
    exception_rules.exception_rules = []

    for i, device_id in enumerate(device_ids, 1):
        log_processing(f"Creating rule {i}/{len(device_ids)} for device {device_id}")
        rule = deepsecurity.ExceptionRule()
        rule.device_id = device_id
        rule.action = "full-access" 
        exception_rules.exception_rules.append(rule)

    result = add_exception_rule(configuration, args.policy_id, exception_rules)
    
    if result:
        log_success("Script completed successfully!")
    else:
        log_error("Script completed with errors!")
        sys.exit(1)

if __name__ == "__main__":
    main()


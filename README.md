# USB Device Exception Rules for Deep Security

![General Illustration](image.png)

This script automatically collects USB device exceptions from all computers in your Deep Security environment and adds them as exception rules to a specified policy.

## Features

- **Automated Device Discovery**: Scans all computers for existing USB device exceptions
- **Policy Management**: Adds collected device exceptions to any specified policy
- **Multi-Region Support**: Works with all Deep Security regions (US, AU, DE, SG, IN, JP, CA, GB)
- **Pretty Logging**: Colored, timestamped output with progress tracking
- **CLI Interface**: Easy-to-use command-line interface with helpful parameter validation

## Prerequisites

- Python 3.6+
- Deep Security API credentials
- Deep Security Python SDK

## Quick Start

For users who want to quickly use this script without git:

1. **Download the repository:**
   - Go to https://github.com/mpkondrashin/migrateusb
   - Click the green **Code** button
   - Select **Download ZIP**
   - Extract the ZIP file to a folder of your choice

2. **Open a terminal/Command Prompt:**
   - Navigate to the extracted folder using `cd path/to/migrateusb`

3. **Follow the Installation steps below**

## Installation

1. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   ```

2. **Activate the virtual environment:**
   
   - **On macOS/Linux:**
     ```bash
     source .venv/bin/activate
     ```
   
   - **On Windows:**
     ```bash
     .venv\Scripts\activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Copy the example environment file and add your API key:
   ```bash
   cp .venv.example .env
   ```
   Then edit the `.env` file and replace `your_api_key_here` with your actual API key.

5. **Get your API Key:**
   - Log into your Deep Security Manager
   - Go to **Administration** > **API Keys**
   - Create a new API key with appropriate permissions

## Usage

**Note:** Make sure your virtual environment is activated before running the script.

### Basic Usage

```bash
python main.py --policy-id 42
```

### Specify Region

```bash
python main.py --policy-id 42 --region sg
```

### Show Help

```bash
python main.py -h
```

## Parameters

### Required Parameters

- `--policy-id`: Policy ID to add exception rules to
  - Type: Integer
  - Must be a valid Deep Security policy ID

#### How to Find Your Policy ID

To get the policy ID from the Deep Security/Workload Security console:

1. **Open the Deep Security/Workload Security console**
2. **Navigate to Policies** in the top navigation menu
3. **Double-click on your target policy** to open it
4. **Look at the URL** in the pop-up window's address bar
5. **Find the `securityProfileID` parameter** in the URL

Example URL:
```
https://cloudone.trendmicro.com/trend-us-1/PolicyEditor.screen?securityProfileID=123&theme=dark```

In this example, **123** is your policy ID that you would use with `--policy-id 123`

### Optional Parameters

- `--region`: Deep Security region
  - Type: String
  - Default: `us`
  - Choices: `us`, `au`, `de`, `sg`, `in`, `jp`, `ca`, `gb`

### Available Regions

| Code | Country | API Endpoint |
|------|---------|--------------|
| `us` | United States | https://workload.us-1.cloudone.trendmicro.com/api |
| `au` | Australia | https://workload.au-1.cloudone.trendmicro.com/api |
| `de` | Germany (EU) | https://workload.de-1.cloudone.trendmicro.com/api |
| `sg` | Singapore | https://workload.sg-1.cloudone.trendmicro.com/api |
| `in` | India | https://workload.in-1.cloudone.trendmicro.com/api |
| `jp` | Japan | https://workload.jp-1.cloudone.trendmicro.com/api |
| `ca` | Canada | https://workload.ca-1.cloudone.trendmicro.com/api |
| `gb` | United Kingdom | https://workload.gb-1.cloudone.trendmicro.com/api |

## Examples

### Example 1: Add exceptions to policy in US region
```bash
python main.py --policy-id 123
```

### Example 2: Add exceptions to policy in Singapore region
```bash
python main.py --policy-id 456 --region sg
```

### Example 3: Add exceptions to policy in Germany
```bash
python main.py --policy-id 789 --region de
```

## What the Script Does

1. **Connects to Deep Security** using your API credentials
2. **Discovers all computers** in your environment
3. **Scans each computer** for existing USB device exceptions
4. **Collects unique device IDs** from all exceptions found
5. **Creates exception rules** for each unique device with "full-access" action
6. **Adds all rules** to the specified policy in a single API call

## Output

The script provides detailed, colored logging output:

```
[2024-03-24 14:30:15] [INFO] Using region: United States (us)
[2024-03-24 14:30:15] [INFO] Starting USB device exception rule collection for policy 123
[2024-03-24 14:30:16] [INFO] ⏳ Fetching computers from Deep Security...
[2024-03-24 14:30:18] [INFO] ✅ Found 25 computers
[2024-03-24 14:30:18] [INFO] ⏳ Processing computer 1001
[2024-03-24 14:30:19] [INFO] 🔍 Found 2 device exceptions on computer 1001
[2024-03-24 14:30:19] [INFO] ⏳ Processing computer 1002
...
[2024-03-24 14:30:45] [INFO] ✅ Total unique device IDs found: 8
[2024-03-24 14:30:45] [INFO] Creating exception rules for 8 unique devices
[2024-03-24 14:30:46] [INFO] ⏳ Creating rule 1/8 for device USB\VID_0781&PID_5567
...
[2024-03-24 14:30:50] [INFO] ⏳ Adding 8 exception rules to policy 123
[2024-03-24 14:30:52] [INFO] ✅ Successfully added 8 exception rules to policy 123
[2024-03-24 14:30:52] [INFO] ✅ Script completed successfully!
```

## Error Handling

The script includes comprehensive error handling:

- **API Connection Errors**: Logs connection issues and exits gracefully
- **Invalid Parameters**: Shows helpful error messages and usage information
- **Policy Not Found**: Reports if the specified policy doesn't exist
- **Permission Issues**: Reports API permission problems

## Security Considerations

- Store your API key securely in the `.env` file
- Never commit API keys to version control
- Use API keys with minimal required permissions
- Consider using different API keys for different environments

## Troubleshooting

### Common Issues

1. **"API Key not found" error**
   - Ensure your `.env` file exists and contains `V1WS_API_KEY`
   - Check that the API key is valid and not expired

2. **"Policy not found" error**
   - Verify the policy ID exists in your Deep Security environment
   - Use the Deep Security console to find the correct policy ID

3. **"Connection timeout" error**
   - Check your network connectivity
   - Verify you're using the correct region code
   - Ensure firewall allows access to Deep Security endpoints

4. **"Permission denied" error**
   - Ensure your API key has permissions to:
     - Read computers
     - Read device control exceptions
     - Modify policies

### Debug Mode

For additional debugging, you can modify the script to enable DEBUG level logging:

```python
logger.setLevel(logging.DEBUG)
```

## License

This script is provided as-is for use with Trend Micro Deep Security. Please ensure you have appropriate permissions and follow your organization's security policies when using this script.

## Support

For issues related to:
- **Deep Security API**: Contact Trend Micro support
- **Script functionality**: Check the script logs and troubleshooting section above
- **API key issues**: Contact your Deep Security administrator

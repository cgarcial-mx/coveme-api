# Amazon SP API Authentication Monitor

This script continuously monitors the Amazon SP API authentication by running tests every minute for 90 minutes (1.5 hours).

## Features

- ✅ Runs authentication tests every minute
- ✅ Continues for exactly 90 minutes (1.5 hours)
- ✅ Logs all results to a file
- ✅ Shows real-time progress and statistics
- ✅ Can be interrupted with Ctrl+C
- ✅ Provides detailed final summary

## Files

- `amazon_auth_monitor.py` - Main Python script
- `run_auth_monitor.sh` - Shell script to run with virtual environment
- `README_auth_monitor.md` - This documentation

## Requirements

- Python 3.7+
- Django project set up
- Virtual environment with required packages
- `python-amazon-sp-api` package installed

## Usage

### Option 1: Using the shell script (Recommended)

```bash
# Make sure you're in the project root directory
cd /path/to/your/project

# Run the monitor
./scripts/run_auth_monitor.sh
```

### Option 2: Direct Python execution

```bash
# Activate virtual environment first
source venv/bin/activate

# Run the monitor
python scripts/amazon_auth_monitor.py
```

## What the script does

1. **Initialization**: Sets up Django and creates a log file
2. **Continuous Testing**: Runs the Amazon API authentication test every minute
3. **Progress Tracking**: Shows real-time progress and success rate
4. **Logging**: Saves all test results to `amazon_auth_monitor.log`
5. **Summary**: Provides final statistics when complete

## Output

### Console Output
```
🔐 Amazon SP API Authentication Monitor
==================================================
This script will run authentication tests every minute for 90 minutes
Results will be logged to 'amazon_auth_monitor.log'
==================================================

📊 Will run 90 tests with 60 second intervals
📝 Log file: /path/to/project/amazon_auth_monitor.log
⏰ Total duration: 90 minutes

🚀 Starting at: 2024-01-15 10:30:00
⏹️  Will stop at: 2024-01-15 12:00:00

🔄 Test #1/90 - 10:30:00
✅ Test #1 PASSED
📊 Progress: 1/90 | Success Rate: 100.0%
   ✅ Success: 1 | ❌ Failed: 0
⏳ Waiting 60 seconds until next test...
```

### Log File
The script creates `amazon_auth_monitor.log` in the project root with detailed results:

```
Amazon SP API Authentication Monitor Log
Started at: 2024-01-15 10:30:00
================================================================================

================================================================================
Timestamp: 2024-01-15 10:30:00
Status: ✅ SUCCESS
================================================================================
Output:
🔐 Testing Amazon SP API Authentication...
==================================================
📋 Creating SP API configuration...
✅ SP API configuration created successfully

🔑 Testing API connection...
✅ API connection established successfully!
   Client created with marketplace: MX

==================================================
🎉 Authentication test completed successfully!
✅ Your Amazon SP API credentials are working correctly
================================================================================
```

## Configuration

You can modify the script to change:

- **Duration**: Edit `total_minutes = 90` in the script
- **Interval**: Edit `interval_seconds = 60` in the script
- **Timeout**: Edit `timeout=60` in the `run_auth_test()` function

## Stopping the Monitor

- **Automatic**: The script stops after 90 minutes
- **Manual**: Press `Ctrl+C` to stop early
- **Time-based**: The script checks the current time and stops if it reaches the end time

## Troubleshooting

### Virtual Environment Issues
```bash
# Create virtual environment if it doesn't exist
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Missing Packages
```bash
# Install required packages
pip install python-amazon-sp-api
pip install django
```

### Permission Issues
```bash
# Make scripts executable
chmod +x scripts/amazon_auth_monitor.py
chmod +x scripts/run_auth_monitor.sh
```

### Django Settings Issues
Make sure your Django project is properly configured and the `api.settings` module exists.

## Monitoring Results

After running the monitor, check:

1. **Console output** for real-time results
2. **Log file** (`amazon_auth_monitor.log`) for detailed results
3. **Final summary** for overall statistics

The log file contains all test results and can be used for:
- Analyzing authentication stability
- Identifying patterns in failures
- Debugging authentication issues
- Generating reports

## Example Use Cases

- **Testing API stability** during development
- **Monitoring authentication** after credential changes
- **Performance testing** of the Amazon SP API
- **Debugging authentication issues**
- **Generating authentication reports** 
# Complete User Guide

## Table of Contents

1. [Framework Overview](#framework-overview)
2. [Getting Started](#getting-started)
3. [Core Components](#core-components)
4. [Generic Test Classes](#generic-test-classes)
5. [Business Logic Tests](#business-logic-tests)
6. [Email Alerting System](#email-alerting-system)
7. [Acknowledgment System](#acknowledgment-system)
8. [Configuration Management](#configuration-management)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)
11. [Advanced Usage](#advanced-usage)

## Framework Overview

The Locaria Integrated Testing Framework is a comprehensive testing system designed specifically for data pipelines and business logic validation. It provides a unified approach to testing data quality, business rules, and operational sanity across multiple pipelines.

### Key Benefits

- **Unified Testing Approach**: Consistent testing patterns across all pipelines
- **Business Logic Focus**: Tests that validate actual business rules, not just data structure
- **Smart Alerting**: Intelligent email system that prevents spam through acknowledgments
- **Persistent Logging**: All test results stored in Google Sheets for historical analysis
- **Dynamic Configuration**: Firestore-based configuration for easy threshold updates
- **Pipeline Integration**: Seamless integration with existing data pipelines

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Data Pipeline                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   TestKit Core                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │   Logging   │ │   Config    │ │  Acknowledgment     │   │
│  │   System    │ │  Manager    │ │     Manager         │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Test Classes                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │   Generic   │ │  Business   │ │    Custom Tests     │   │
│  │    Tests    │ │ Logic Tests │ │                     │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              External Integrations                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │Sheet Logger │ │Email Manager│ │    Firestore        │   │
│  │             │ │             │ │   Configuration     │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Getting Started

### Environment Setup

The framework automatically integrates with the existing `locate_2_pulls` configuration store. No additional environment variables are required for basic functionality.

#### Optional Environment Variables

For advanced usage or when running outside the `locate_2_pulls` environment:

```bash
# Email API configuration (fallback)
export EMAIL_API_URL="https://your-app.appspot.com/api/tools/send_email_direct"

# Sheet Logger configuration (fallback)
export TEST_LOGS_SPREADSHEET_ID="your-google-sheets-id"
export GOOGLE_CREDENTIALS_PATH="/path/to/credentials.json"
```

#### Automatic Configuration

The framework automatically uses:
- **Firestore Project**: `locaria-dev-config-store` (from config store)
- **Sheet Logger**: Existing sheet logger instance from config store
- **Email API**: Tool URL from config store (`tool_URL + api/tools/send_email_direct`)

### Basic Pipeline Integration

#### Step 1: Import Required Modules

```python
from modules.integrated_tests import create_testkit, DataQualityTests, FreshnessTests, RowCountTests, DuplicateTests
```

#### Step 2: Initialize TestKit

```python
class YourPipeline:
    def __init__(self):
        # Initialize testing framework
        self.testkit = create_testkit("your_repo", "your_pipeline")
        
        # Initialize test classes
        self.data_quality_tests = DataQualityTests(self.testkit)
        self.freshness_tests = FreshnessTests(self.testkit)
        self.row_count_tests = RowCountTests(self.testkit)
        self.duplicate_tests = DuplicateTests(self.testkit)
```

#### Step 3: Add Tests to Your Pipeline

```python
def run_pipeline(self):
    try:
        # Load your data
        df = self.load_data()
        
        # Stage 1: Data quality tests
        self.data_quality_tests.check_numeric_ranges(df, {"hours": (0, 24)})
        self.duplicate_tests.check_duplicate_records(df, ["employee_id", "date"])
        
        # Stage 2: Transform and load
        df_transformed = self.transform_data(df)
        self.row_count_tests.check_row_count_change(df_transformed, "table_name", "append")
        
        # Stage 3: Freshness checks
        self.load_to_bq(df_transformed, table="finance.time_splits")
        self.freshness_tests.check_data_freshness(df_transformed, "timestamp")
        
    finally:
        # Always finalize the test run
        test_summary = self.testkit.finalize_run()
        print(f"Pipeline completed. Test summary: {test_summary}")
```

## Core Components

### TestKit

The TestKit is the core orchestration component that manages test execution, logging, and alerting.

#### Key Features

- **Test Result Aggregation**: Collects and organizes all test results
- **Sheet Logger Integration**: Persistent storage of test results
- **Email Alerting**: Smart email notifications with acknowledgment filtering
- **Configuration Management**: Dynamic configuration from Firestore (`locaria-dev-config-store`)
- **Acknowledgment Integration**: Prevents email spam for known issues

#### Initialization

```python
# Basic initialization
testkit = create_testkit("repository_name", "pipeline_name")

# With custom settings
testkit = create_testkit(
    repository_name="locate_2_pulls",
    pipeline_name="daily_updates",
    fail_on_error=False  # Continue pipeline on test failures
)
```

#### Core Methods

```python
# Logging methods
testkit.log_pass(test_name, message, metrics=None)
testkit.log_warn(test_name, message, metrics=None, acknowledgeable=True)
testkit.log_fail(test_name, message, metrics=None, acknowledgeable=True)

# Configuration
testkit.is_test_enabled(test_name)  # Check if test is enabled
testkit.get_config_value(key, default=None)  # Get configuration value

# Finalization
testkit.finalize_run()  # Send emails and finalize run
```

### Test Result Types

#### PASS
- Test completed successfully
- No issues detected
- Logged for historical tracking

#### WARN
- Test detected potential issues
- Pipeline continues execution
- May trigger warning digest emails
- Can be acknowledged to prevent future emails

#### FAIL
- Test detected critical issues
- May stop pipeline execution (if `fail_on_error=True`)
- Triggers immediate failure alert emails
- Can be acknowledged to prevent future emails

## Generic Test Classes

### DataQualityTests

Data quality tests for common validation scenarios.

#### Available Methods

```python
# Numeric range validation
data_quality_tests.check_numeric_ranges(
    df, 
    {"hours": (0, 24), "percentage": (0, 100)}
)

# Data completeness checks
data_quality_tests.check_data_completeness(
    df, 
    required_columns=["employee_id", "date", "hours"],
    completeness_threshold=0.95
)

# Date range validation
data_quality_tests.check_date_ranges(
    df,
    date_columns={"start_date": ("2020-01-01", "2025-12-31")}
)
```

#### Example Usage

```python
def validate_timesheet_data(self, df):
    """Validate timesheet data quality."""
    
    # Check numeric ranges
    self.data_quality_tests.check_numeric_ranges(
        df, 
        {
            "hours": (0, 24),  # Hours should be 0-24
            "overtime": (0, 20)  # Overtime should be 0-20
        }
    )
    
    # Check data completeness
    self.data_quality_tests.check_data_completeness(
        df,
        required_columns=["employee_id", "date", "hours", "project_code"],
        completeness_threshold=0.98  # 98% completeness required
    )
    
    # Check date ranges
    self.data_quality_tests.check_date_ranges(
        df,
        date_columns={
            "date": ("2020-01-01", "2025-12-31"),
            "submission_date": ("2020-01-01", "2025-12-31")
        }
    )
```

### FreshnessTests

Data freshness tests for ensuring data is up-to-date.

#### Available Methods

```python
# Data freshness validation
freshness_tests.check_data_freshness(
    df, 
    timestamp_column="updated_at",
    max_age_hours=24
)

# Timestamp progression checks
freshness_tests.check_timestamp_progression(
    df,
    timestamp_column="created_at"
)

# Data consistency validation
freshness_tests.check_data_consistency(
    df,
    timestamp_column="date",
    expected_frequency="daily"
)
```

#### Example Usage

```python
def validate_data_freshness(self, df):
    """Validate data freshness and consistency."""
    
    # Check data freshness
    self.freshness_tests.check_data_freshness(
        df,
        timestamp_column="last_updated",
        max_age_hours=6  # Data should be no older than 6 hours
    )
    
    # Check timestamp progression
    self.freshness_tests.check_timestamp_progression(
        df,
        timestamp_column="created_at"
    )
    
    # Check data consistency
    self.freshness_tests.check_data_consistency(
        df,
        timestamp_column="date",
        expected_frequency="daily"
    )
```

### RowCountTests

Row count tracking tests for monitoring data volume changes.

#### Available Methods

```python
# Row count change validation
row_count_tests.check_row_count_change(
    df, 
    table_name="employees",
    operation_type="append"  # or "truncate"
)

# Row count threshold validation
row_count_tests.check_row_count_threshold(
    df,
    table_name="transactions",
    min_rows=1000,
    max_rows=10000
)
```

#### Example Usage

```python
def validate_data_volume(self, df):
    """Validate data volume changes."""
    
    # Check row count changes for append operations
    self.row_count_tests.check_row_count_change(
        df,
        table_name="daily_transactions",
        operation_type="append"
    )
    
    # Check row count thresholds
    self.row_count_tests.check_row_count_threshold(
        df,
        table_name="user_activity",
        min_rows=500,  # Minimum expected rows
        max_rows=5000  # Maximum expected rows
    )
```

### DuplicateTests

Duplicate detection tests for data integrity validation.

#### Available Methods

```python
# Duplicate record detection
duplicate_tests.check_duplicate_records(
    df, 
    key_columns=["employee_id", "date"]
)

# Business key validation
duplicate_tests.check_business_key_uniqueness(
    df,
    business_key_columns=["customer_id", "order_date", "product_id"]
)
```

#### Example Usage

```python
def validate_data_integrity(self, df):
    """Validate data integrity and uniqueness."""
    
    # Check for duplicate records
    self.duplicate_tests.check_duplicate_records(
        df,
        key_columns=["employee_id", "date", "project_code"]
    )
    
    # Check business key uniqueness
    self.duplicate_tests.check_business_key_uniqueness(
        df,
        business_key_columns=["customer_id", "order_date", "product_id"]
    )
```

## Business Logic Tests

Business logic tests validate domain-specific rules and requirements. These tests are typically custom-built for specific pipelines and business domains.

### Creating Business Logic Tests

#### Step 1: Create Test Class

```python
from modules.integrated_tests import create_testkit

class YourBusinessTests:
    """Business logic tests for your specific domain."""
    
    def __init__(self, testkit=None):
        if testkit is None:
            self.testkit = create_testkit("your_repo", "your_pipeline")
        else:
            self.testkit = testkit
```

#### Step 2: Implement Business Rules

```python
def check_financial_ratios(self, financial_data):
    """Check that financial ratios are within acceptable bounds."""
    
    try:
        for _, row in financial_data.iterrows():
            # Calculate ratio
            ratio = row['revenue'] / row['costs'] if row['costs'] > 0 else 0
            
            # Check if ratio is within acceptable range
            if ratio < 1.2 or ratio > 3.0:
                self.testkit.log_warn(
                    "check_financial_ratios",
                    f"Financial ratio out of bounds: {row['company']} - {ratio:.2f} (expected 1.2-3.0)",
                    {
                        "company": row['company'],
                        "ratio": ratio,
                        "revenue": row['revenue'],
                        "costs": row['costs']
                    }
                )
            else:
                self.testkit.log_pass(
                    "check_financial_ratios",
                    f"Financial ratio acceptable: {row['company']} - {ratio:.2f}"
                )
                
    except Exception as e:
        self.testkit.log_fail(
            "check_financial_ratios",
            f"Error checking financial ratios: {str(e)}"
        )
```

#### Step 3: Integrate with Pipeline

```python
class YourPipeline:
    def __init__(self):
        self.testkit = create_testkit("your_repo", "your_pipeline")
        self.business_tests = YourBusinessTests(self.testkit)
    
    def run_pipeline(self):
        try:
            # Load data
            financial_data = self.load_financial_data()
            
            # Run business logic tests
            self.business_tests.check_financial_ratios(financial_data)
            
            # Continue with pipeline...
            
        finally:
            test_summary = self.testkit.finalize_run()
```

### Example: Capacity Tracker Tests

The capacity tracker pipeline includes comprehensive business logic tests:

```python
from modules.integrated_tests.pipeline_specific.capacity_tracker_linguists_days_off import CapacityTrackerBusinessTests

class YourPipeline:
    def __init__(self):
        self.testkit = create_testkit("locate_2_pulls", "capacity_tracker")
        self.capacity_tests = CapacityTrackerBusinessTests(self.testkit)
    
    def run_pipeline(self):
        try:
            # Load timesheet data
            timesheet_df = self.load_timesheet_data()
            
            # Run capacity tracker business tests
            self.capacity_tests.check_consistent_daily_hours_per_person(timesheet_df)
            self.capacity_tests.check_absent_time_thresholds(timesheet_df)
            
            # Continue with pipeline...
            
        finally:
            test_summary = self.testkit.finalize_run()
```

## Email Alerting System

The framework includes a sophisticated email alerting system that provides intelligent notifications while preventing email spam.

### Alert Types

#### Failure Alerts
- **Trigger**: FAIL test results
- **Timing**: Immediate notification
- **Content**: Detailed error information, stack traces, context
- **Recipients**: Pipeline owners, data team

#### Warning Digests
- **Trigger**: WARN test results
- **Timing**: End of pipeline run
- **Content**: Grouped warnings, summary statistics
- **Recipients**: Pipeline owners, stakeholders

### Email Templates

The framework uses pre-configured email templates:

#### Test Failure Alert Template
```
🚨 Test Failure Alert

Repository: {repository}
Pipeline: {pipeline}
Run ID: {run_id}

FAILURE SUMMARY:
{detailed_failure_information}

Run Duration: {duration}
Timestamp: {timestamp}

Please review and take appropriate action.
```

#### Test Warning Digest Template
```
⚠️ Test Warning Digest

Repository: {repository}
Pipeline: {pipeline}
Run ID: {run_id}

WARNING SUMMARY:
Total Warnings: {warning_count}

Warning Details:
{detailed_warning_information}

Run Duration: {duration}
Timestamp: {timestamp}

Please review these warnings and take appropriate action if needed.
```

### Smart Filtering

The email system includes intelligent filtering to prevent spam:

- **Acknowledgment Filtering**: Excludes acknowledged issues from emails
- **Rate Limiting**: Limits emails per day per pipeline
- **Context Preservation**: Shows acknowledged issues in context
- **Team Coordination**: Clear visibility of who acknowledged what

## Acknowledgment System

The acknowledgment system prevents email spam by allowing users to acknowledge known issues, which mutes them for a configurable period.

### How It Works

1. **Issue Detection**: Tests detect issues and log them with acknowledgment metadata
2. **Email Filtering**: Email system checks acknowledgment status before sending
3. **User Acknowledgment**: Users can acknowledge issues through web interface
4. **Mute Period**: Acknowledged issues are muted for 7 days (configurable)
5. **Automatic Expiry**: Mute periods expire automatically

### Acknowledgment Metadata

When logging issues that can be acknowledged, include these metadata fields:

```python
self.testkit.log_warn(
    test_name="check_data_quality",
    message="Data quality issue detected",
    metrics={
        # Required for acknowledgment
        "person_email": "user@example.com",
        "issue_type": "data_quality",
        "issue_key": "table_name",
        
        # Optional but recommended
        "person_name": "User Name",
        "issue_percentage": 85.2,
        "expected_value": 100,
        "actual_value": 85.2
    },
    acknowledgeable=True  # This is the default
)
```

### Web Interface

The acknowledgment system includes a modern web interface accessible at `/tools/acknowledgment-manager` in the [Analytics Hub](https://locaria-dev-finance-reports.ew.r.appspot.com/tools/acknowledgment-manager).

#### Features
- **Real-time Filtering**: Filter by repository, pipeline, test type
- **Issue Management**: Acknowledge/unacknowledge issues
- **Search and Navigation**: Find specific issues quickly
- **Team Coordination**: See who acknowledged what
- **Bulk Operations**: Handle multiple issues at once

#### Usage
1. **Access Interface**: Navigate to the web interface
2. **Filter Issues**: Use dropdowns and buttons to find relevant issues
3. **Review Details**: Click on issues to see detailed information
4. **Acknowledge Issues**: Click acknowledge button to mute issues
5. **Monitor Status**: Use summary statistics to track acknowledgment rates

## Configuration Management

The framework uses Firestore for dynamic configuration management (`locaria-dev-config-store` project), allowing thresholds and settings to be updated without code changes.

### Configuration Structure

```json
{
  "test_config": {
    "check_data_quality": {
      "enabled": true,
      "thresholds": {
        "completeness_threshold": 0.95,
        "max_null_percentage": 0.05
      }
    },
    "check_financial_ratios": {
      "enabled": true,
      "thresholds": {
        "min_ratio": 1.2,
        "max_ratio": 3.0
      }
    }
  },
  "email_config": {
    "enabled": true,
    "max_emails_per_day": 1,
    "recipients": ["data-team@company.com"]
  },
  "acknowledgment_config": {
    "default_mute_days": 7,
    "max_mute_days": 30
  }
}
```

### Accessing Configuration

```python
# Check if test is enabled
if testkit.is_test_enabled("check_data_quality"):
    # Run test
    
# Get configuration value
threshold = testkit.get_config_value("test_config.check_data_quality.thresholds.completeness_threshold", 0.95)

# Update configuration
testkit.update_config_in_firestore({
    "test_config.check_data_quality.thresholds.completeness_threshold": 0.98
})
```

### Configuration Best Practices

- **Use Sensible Defaults**: Provide fallback values for all configuration
- **Document Thresholds**: Clearly document what each threshold controls
- **Version Control**: Track configuration changes
- **Test Changes**: Validate configuration changes before deployment

## Best Practices

### Test Design

#### Focus on Business Logic
- Test actual business rules, not just data structure
- Use descriptive test names that explain the business rule
- Include both positive and negative test cases
- Test at multiple stages: intake, transform, load, post-load

#### Error Handling
- Always use try/finally blocks to ensure test finalization
- Handle missing data gracefully
- Provide meaningful error messages
- Log sufficient context for debugging

#### Performance
- Batch test operations when possible
- Use efficient pandas operations
- Avoid unnecessary data copies
- Cache configuration when appropriate

### Pipeline Integration

#### Test Placement
- **Intake Tests**: Validate incoming data quality
- **Transform Tests**: Check business logic during transformation
- **Load Tests**: Validate data after loading
- **Post-Load Tests**: Check final data state

#### Error Handling
```python
def run_pipeline(self):
    try:
        # Your pipeline logic
        data = self.load_data()
        self.run_tests(data)
        self.process_data(data)
        
    except Exception as e:
        # Log the error
        self.testkit.log_fail("pipeline_execution", f"Pipeline failed: {str(e)}")
        raise
        
    finally:
        # Always finalize
        test_summary = self.testkit.finalize_run()
```

### Acknowledgment Management

#### For Users
- **Regular Review**: Check for new issues regularly
- **Meaningful Acknowledgments**: Only acknowledge issues you understand
- **Documentation**: Use the reason field when acknowledging
- **Team Coordination**: Coordinate with team members on acknowledgments

#### For Developers
- **Consistent Metadata**: Use consistent field names and values
- **Meaningful Context**: Include enough information for debugging
- **Error Handling**: Handle acknowledgment failures gracefully
- **Testing**: Test acknowledgment functionality thoroughly

## Troubleshooting

### Common Issues

#### Tests Not Running
**Symptoms**: Tests are not executing or logging results

**Causes**:
- Test not enabled in configuration
- Missing test initialization
- Configuration not loaded

**Solutions**:
1. Check test configuration in Firestore
2. Verify test initialization in pipeline
3. Check configuration loading

```python
# Debug test configuration
print(f"Test enabled: {testkit.is_test_enabled('your_test_name')}")
print(f"Configuration: {testkit.get_config_value('test_config.your_test_name')}")
```

#### Emails Not Sending
**Symptoms**: No email notifications for test failures or warnings

**Causes**:
- Email configuration missing
- API endpoint not accessible
- All issues acknowledged

**Solutions**:
1. Check email configuration
2. Verify API endpoint accessibility
3. Check acknowledgment status

```python
# Debug email configuration
email_config = testkit.get_config_value('email_config')
print(f"Email config: {email_config}")

# Check if issues are acknowledged
filtered_results = testkit.acknowledge_manager.filter_acknowledged_issues(testkit.failures)
print(f"New issues: {len(filtered_results['new_issues'])}")
print(f"Acknowledged issues: {len(filtered_results['acknowledged_issues'])}")
```

#### Acknowledgment Not Working
**Symptoms**: Issues remain in emails after acknowledgment

**Causes**:
- Missing acknowledgment metadata
- Issue key mismatch
- Acknowledgment not saved

**Solutions**:
1. Verify acknowledgment metadata
2. Check issue key consistency
3. Verify Firestore permissions

```python
# Debug acknowledgment metadata
testkit.log_warn(
    "test_name",
    "Test message",
    {
        "person_email": "user@example.com",  # Required
        "issue_type": "test_type",           # Required
        "issue_key": "unique_key"            # Required
    }
)
```

### Debug Commands

#### Check Test Configuration
```python
# Check if test is enabled
enabled = testkit.is_test_enabled("your_test_name")
print(f"Test enabled: {enabled}")

# Get test configuration
config = testkit.get_config_value("test_config.your_test_name")
print(f"Test config: {config}")
```

#### Check Acknowledgment Status
```python
# Check if issue is acknowledged
is_acknowledged = testkit.acknowledge_manager.check_issue_acknowledged(
    test_name="your_test",
    issue_identifier="user@example.com",
    issue_type="your_issue_type",
    issue_key="your_key"
)
print(f"Issue acknowledged: {is_acknowledged}")
```

#### Check Email Configuration
```python
# Check email configuration
email_config = testkit.get_config_value("email_config")
print(f"Email config: {email_config}")

# Check email API URL
email_api_url = testkit.get_config_value("api_config.email_api_url")
print(f"Email API URL: {email_api_url}")
```

## Advanced Usage

### Custom Test Classes

#### Creating Custom Test Classes
```python
from modules.integrated_tests import create_testkit

class CustomBusinessTests:
    """Custom business logic tests for your domain."""
    
    def __init__(self, testkit=None):
        if testkit is None:
            self.testkit = create_testkit("your_repo", "your_pipeline")
        else:
            self.testkit = testkit
    
    def check_custom_business_rule(self, data):
        """Check custom business rule with acknowledgment support."""
        
        try:
            for item in data:
                if not self._validate_business_rule(item):
                    self.testkit.log_warn(
                        "check_custom_business_rule",
                        f"Business rule violation: {item['id']} - {item['details']}",
                        {
                            "person_email": item['owner_email'],
                            "issue_type": "business_rule_violation",
                            "issue_key": item['rule_id'],
                            "person_name": item['owner_name'],
                            "rule_name": item['rule_name'],
                            "violation_details": item['details']
                        }
                    )
                else:
                    self.testkit.log_pass(
                        "check_custom_business_rule",
                        f"Business rule satisfied: {item['id']}"
                    )
                    
        except Exception as e:
            self.testkit.log_fail(
                "check_custom_business_rule",
                f"Error checking business rule: {str(e)}"
            )
    
    def _validate_business_rule(self, item):
        """Validate individual business rule."""
        # Your business logic here
        return True  # or False
```

### Batch Operations

#### Batch Test Execution
```python
def run_batch_tests(self, data_batches):
    """Run tests on multiple data batches."""
    
    for batch_name, batch_data in data_batches.items():
        try:
            # Run tests on this batch
            self.data_quality_tests.check_numeric_ranges(batch_data, {"value": (0, 100)})
            self.duplicate_tests.check_duplicate_records(batch_data, ["id"])
            
        except Exception as e:
            self.testkit.log_fail(
                f"batch_test_{batch_name}",
                f"Batch test failed for {batch_name}: {str(e)}"
            )
```

### Performance Optimization

#### Efficient Test Execution
```python
def run_optimized_tests(self, df):
    """Run tests efficiently on large datasets."""
    
    # Use vectorized operations when possible
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    
    # Batch numeric range checks
    for column in numeric_columns:
        if column in self.expected_ranges:
            min_val, max_val = self.expected_ranges[column]
            invalid_mask = (df[column] < min_val) | (df[column] > max_val)
            
            if invalid_mask.any():
                invalid_rows = df[invalid_mask]
                for _, row in invalid_rows.iterrows():
                    self.testkit.log_warn(
                        "check_numeric_ranges",
                        f"Value out of range: {column} = {row[column]} (expected {min_val}-{max_val})",
                        {
                            "column": column,
                            "value": row[column],
                            "min_expected": min_val,
                            "max_expected": max_val
                        }
                    )
```

### Integration with External Systems

#### Custom Logging Integration
```python
def custom_logging_integration(self, testkit):
    """Integrate with external logging systems."""
    
    # Override the default logging method
    original_log = testkit._log_to_sheet
    
    def enhanced_log(result):
        # Call original logging
        original_log(result)
        
        # Add custom logging
        self.log_to_external_system(result)
    
    testkit._log_to_sheet = enhanced_log

def log_to_external_system(self, result):
    """Log to external system."""
    # Your custom logging logic here
    pass
```

---

This comprehensive user guide covers all aspects of the Locaria Integrated Testing Framework. For specific implementation details, refer to the API Reference and Test Classes guides. For questions or support, contact the development team.


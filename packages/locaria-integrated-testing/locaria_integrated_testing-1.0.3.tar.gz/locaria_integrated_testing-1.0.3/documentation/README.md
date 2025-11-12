# Locaria Integrated Testing Framework

## Overview

The Locaria Integrated Testing Framework is a comprehensive, lightweight testing system designed for data pipelines and business logic validation. It focuses on business-logic validation, data quality checks, and operational sanity tests rather than UI or cosmetic testing.

## Key Features

- **Business Logic Validation** - Test time splits sum to 100%, financial ratios are within bounds, etc.
- **Data Quality Checks** - Schema validation, null checks, row count sanity, data freshness
- **Configurable Thresholds** - Firestore-based configuration for easy threshold updates
- **Integrated Logging** - Sheet Logger integration for persistent test result storage
- **Smart Email Alerts** - Real-time failure notifications with acknowledgment system
- **Pipeline-Specific Tests** - Custom business logic validation for different data domains
- **Acknowledgment System** - Prevent email spam by acknowledging known issues

## Quick Start

### Basic Usage

```python
from modules.integrated_tests import create_testkit, DataQualityTests, FreshnessTests, RowCountTests, DuplicateTests

# Initialize testing framework
testkit = create_testkit("locate_2_pulls", "daily_updates")

# Initialize test classes
data_quality_tests = DataQualityTests(testkit)
freshness_tests = FreshnessTests(testkit)
row_count_tests = RowCountTests(testkit)
duplicate_tests = DuplicateTests(testkit)

try:
    # Your data pipeline code
    df = extract_data()
    
    # Stage 1: Data quality tests
    data_quality_tests.check_numeric_ranges(df, {"hours": (0, 24)})
    duplicate_tests.check_duplicate_records(df, ["employee_id", "date"])
    
    # Stage 2: Transform and load
    df_transformed = transform_data(df)
    row_count_tests.check_row_count_change(df_transformed, "table_name", "append")
    
    # Stage 3: Freshness checks
    load_to_bq(df_transformed, table="finance.time_splits")
    freshness_tests.check_data_freshness(df_transformed, "timestamp")
    
finally:
    # Always finalize the test run
    testkit.finalize_run()
```

## Documentation Structure

### 📖 [Complete User Guide](user_guide.md)
**Comprehensive guide covering everything from basic usage to advanced patterns**
- Framework overview and architecture
- Test class usage with examples
- Pipeline integration patterns
- Business logic test development
- Email alerting and acknowledgment system
- Configuration and customization
- Troubleshooting and best practices

### 🏗️ [Architecture Guide](architecture.md)
**System architecture and design principles**

- Framework components and relationships
- Test execution flow
- Integration with external systems
- Configuration management
- Performance considerations

### 🔧 [API Reference](api_reference.md)
**Complete API documentation for all components**
- TestKit core methods
- Generic test classes
- Pipeline-specific test patterns
- Configuration management
- Error handling and exceptions

### 📊 [Test Classes Guide](test_classes.md)
**Detailed guide to all available test classes**
- DataQualityTests - Numeric ranges, completeness, validation
- FreshnessTests - Data freshness and timestamp validation
- RowCountTests - Row count tracking and change detection
- DuplicateTests - Duplicate record detection
- Custom business logic tests

### 🚀 [Getting Started](getting_started.md)
**Step-by-step guide for new users**
- Environment setup
- First pipeline integration
- Basic test implementation
- Common patterns and examples

## Framework Components

### Core Components

#### TestKit
- **Location**: `main/testkit.py`
- **Purpose**: Core orchestration, logging, and alerting
- **Features**: Sheet Logger integration, email alerts, configuration management

#### Generic Test Classes
- **Location**: `generic_tests/`
- **Purpose**: Reusable tests for common data quality scenarios
- **Classes**: DataQualityTests, FreshnessTests, RowCountTests, DuplicateTests

#### Pipeline-Specific Tests
- **Location**: `pipeline_specific/`
- **Purpose**: Business logic tests for specific domains
- **Examples**: Capacity tracker tests, financial validation tests

#### Acknowledgment System
- **Location**: `main/acknowledge_manager.py`
- **Purpose**: Prevent email spam by acknowledging known issues
- **Features**: Web UI, Firestore storage, smart email filtering

### Integration Points

#### Sheet Logger
- Persistent test result storage
- Historical test tracking
- Performance monitoring

#### Email Manager
- Real-time failure notifications
- Warning digests
- Acknowledgment-aware filtering

#### Firestore Configuration
- Dynamic threshold configuration
- Test enable/disable switches
- Acknowledgment storage

## Test Types

### Generic Tests

#### Data Quality Tests
- Numeric range validation
- Data completeness checks
- Value set validation
- Null constraint checking

#### Freshness Tests
- Data age validation
- Timestamp progression checks
- Partition freshness monitoring
- Data consistency validation

#### Row Count Tests
- Volume change detection
- Append/truncate operation validation
- Historical comparison
- Threshold-based alerts

#### Duplicate Tests
- Single/multi-column duplicate detection
- Business key validation
- Data integrity checks

### Business Logic Tests

#### Capacity Tracker Tests
- Weekly hours consistency validation
- Absent time threshold monitoring
- Employee status validation
- Time tracking accuracy

#### Financial Tests
- Ratio validation
- Balance checks
- Transaction integrity
- Compliance validation

## Email Alerting System

### Alert Types

#### Failure Alerts
- Immediate notification for FAIL results
- Pipeline-stopping critical issues
- Detailed error information

#### Warning Digests
- Grouped notification for WARN results
- Acknowledgment-aware filtering
- Summary statistics

### Acknowledgment System

#### Web Interface
- Modern UI for managing acknowledgments
- Real-time filtering and search
- Bulk operations support

#### Smart Filtering
- Automatically excludes acknowledged issues
- Configurable mute periods
- Team coordination features

## Configuration

### Firestore Configuration
- Dynamic threshold updates
- Test enable/disable switches
- Email template customization
- Acknowledgment settings

### Environment Variables
```bash
# Email API configuration (fallback)
export EMAIL_API_URL="https://your-app.appspot.com/api/tools/send_email_direct"

# Sheet Logger configuration (fallback)
export TEST_LOGS_SPREADSHEET_ID="your-google-sheets-id"
export GOOGLE_CREDENTIALS_PATH="/path/to/credentials.json"
```

## Best Practices

### Test Design
- Focus on business logic and data quality
- Use descriptive test names that explain the business rule
- Test at multiple stages: intake, transform, load, post-load
- Include both positive and negative test cases

### Error Handling
- Always use try/finally blocks to ensure test finalization
- Handle missing data gracefully
- Provide meaningful error messages
- Log sufficient context for debugging

### Performance
- Batch test operations when possible
- Use efficient pandas operations
- Avoid unnecessary data copies
- Cache configuration when appropriate

### Acknowledgment Management
- Only acknowledge issues you understand
- Use meaningful acknowledgment reasons
- Coordinate with team members
- Regular review of acknowledgment patterns

## Examples

### Complete Pipeline Example
```python
from modules.integrated_tests import create_testkit, DataQualityTests, FreshnessTests
from modules.integrated_tests.pipeline_specific.capacity_tracker_linguists_days_off import CapacityTrackerBusinessTests

class YourPipeline:
    def __init__(self):
        # Initialize testing framework
        self.testkit = create_testkit("your_repo", "your_pipeline")
        
        # Initialize test classes
        self.data_quality_tests = DataQualityTests(self.testkit)
        self.freshness_tests = FreshnessTests(self.testkit)
        self.business_tests = CapacityTrackerBusinessTests(self.testkit)
    
    def run_pipeline(self):
        try:
            # Load your data
            data = self.load_data()
            
            # Run generic tests
            self.data_quality_tests.check_numeric_ranges(data, {"hours": (0, 24)})
            self.freshness_tests.check_data_freshness(data, "timestamp")
            
            # Run business logic tests
            self.business_tests.check_consistent_daily_hours_per_person(data)
            self.business_tests.check_absent_time_thresholds(data)
            
            # Process data
            self.process_data(data)
            
            # Finalize testing (sends filtered emails)
            test_summary = self.testkit.finalize_run()
            print(f"Pipeline completed. Test summary: {test_summary}")
            
        except Exception as e:
            print(f"Pipeline error: {e}")
            test_summary = self.testkit.finalize_run()
            raise
```

## Getting Help

### Documentation
- Start with the [User Guide](user_guide.md) for comprehensive coverage
- Use the [API Reference](api_reference.md) for technical details
- Check [Test Classes Guide](test_classes.md) for specific test implementations

### Support
- Check the troubleshooting sections in the guides
- Use the debug commands and tools provided
- Contact the development team with specific error details

### Contributing
- Follow the established patterns and conventions
- Add comprehensive tests for new features
- Update documentation for any changes
- Use the existing code review process

## Version History

### Current Version: 1.0.0
- Complete integrated testing framework
- Generic test classes for common scenarios
- Business logic test examples
- Acknowledgment system with web UI
- Comprehensive documentation

### Future Enhancements
- Additional generic test classes
- Enhanced business logic test templates
- Advanced acknowledgment features
- Performance optimizations
- Integration with additional external systems

---

## Quick Links

- **🚀 [Getting Started](getting_started.md)** - Start here for new users
- **📖 [User Guide](user_guide.md)** - Complete framework documentation
- **🏗️ [Architecture](architecture.md)** - System design and components
- **🔧 [API Reference](api_reference.md)** - Technical API documentation
- **📊 [Test Classes](test_classes.md)** - Available test implementations

For questions or support, refer to the documentation or contact the development team.


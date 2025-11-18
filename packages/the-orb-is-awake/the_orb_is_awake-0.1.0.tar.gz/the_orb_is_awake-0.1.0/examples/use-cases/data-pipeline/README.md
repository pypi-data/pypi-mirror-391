# Data Pipeline Use Case

Integrate the Amp SDK into data processing and transformation workflows.

## Overview

This example demonstrates how to use Amp as an intelligent component in data pipelines. The agent can analyze data files, identify quality issues, and transform data between formats - all programmatically.

## What You'll Learn

- Integrating Amp into automated workflows
- Using the agent to analyze data files
- Transforming data with natural language instructions
- Handling agent results programmatically
- Error handling in pipeline contexts

## Requirements

```bash
pip install amp-sdk
```

## Usage

### Quick Start

```bash
python data_pipeline.py
```

### What It Does

The example demonstrates a complete data pipeline:

1. **Creates sample data** - Generates a CSV file with sample records
2. **Analyzes the data** - Uses Amp to extract insights:
   - Record counts
   - Column types
   - Data quality issues
   - Summary statistics
3. **Transforms the data** - Converts CSV to JSON with:
   - Missing data removal
   - Timestamp addition
   - Format conversion
4. **Processes results** - Shows how to handle agent output in your code

## Key Concepts

### Analysis Function

```python
async def analyze_data_with_amp(data_file: Path) -> dict:
    """Use Amp to analyze a data file and extract insights"""
    prompt = f"""
    Analyze the data file at {data_file}.
    
    Please provide:
    1. Number of records
    2. Column names and types
    3. Any data quality issues
    4. Summary statistics
    """
    
    # Collect analysis from agent
    async for message in execute(prompt, options=options):
        if message.type == 'assistant':
            # Extract text responses
            ...
```

### Transformation Function

```python
async def transform_data_with_amp(input_file: Path, output_file: Path):
    """Use Amp to transform data from one format to another"""
    prompt = f"""
    Transform the data from {input_file} to {output_file}.
    
    Requirements:
    - Convert to JSON format
    - Remove any rows with missing critical fields
    - Add a 'processed_at' timestamp to each record
    """
```

## Customization Ideas

- **Different data formats**: CSV, JSON, Parquet, Excel
- **Complex transformations**: Aggregations, joins, pivots
- **Quality checks**: Validation rules, schema enforcement
- **Integration**: Connect to databases, APIs, cloud storage
- **Scheduling**: Run with cron, Airflow, or other orchestrators

## Error Handling

The example shows proper error handling:

```python
async for message in execute(prompt, options=options):
    if message.type == 'result':
        if message.is_error:
            raise RuntimeError(f"Analysis failed: {message.error}")
```

## Best Practices

1. **Use `dangerously_allow_all=True`** for pipeline contexts where file access is needed
2. **Collect results programmatically** - Extract specific information from agent responses
3. **Handle errors gracefully** - Check for failures and log appropriately
4. **Clean up resources** - Remove temporary files after processing

## Real-World Applications

- ETL (Extract, Transform, Load) processes
- Data quality monitoring
- Automated reporting
- Data migration between systems
- Log file analysis
- Dataset preparation for ML

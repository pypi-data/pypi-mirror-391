# Interactive Data Analysis Use Case

Use Amp as an intelligent data analysis assistant.

## Overview

This example demonstrates how to use the Amp SDK for interactive data analysis tasks. Perfect for data scientists and analysts who want to leverage AI for exploratory analysis, code generation, and insights extraction.

## What You'll Learn

- Using Amp for file and project analysis
- Analyzing datasets with controlled permissions
- Generating visualization code
- Building interactive development assistants
- Combining Amp with pandas and other data tools

## Requirements

```bash
pip install amp-sdk pandas
```

Optional for visualizations:
```bash
pip install matplotlib seaborn
```

## Usage

### Run All Examples

```bash
python interactive_data_analysis.py
```

### Run Individual Examples

The script contains four distinct examples you can run separately by modifying the `main()` function:

1. **Project Analysis** - Analyze Python files in the current directory
2. **Data Analysis** - Analyze CSV data with controlled permissions
3. **Code Generation** - Generate visualization code
4. **Interactive Assistant** - Ask development questions

## Key Concepts

### Example 1: Project File Analysis

```python
async def analyze_project():
    """Analyze Python files in the current directory"""
    prompt = "List all Python files in the current directory and summarize what each one does."
    
    options = AmpOptions(dangerously_allow_all=True)
    
    async for message in execute(prompt, options=options):
        # Process responses
        ...
```

### Example 2: Controlled Data Analysis

```python
async def analyze_data():
    """Analyze data with read-only permissions"""
    # Create sample data
    df = pd.DataFrame(data)
    df.to_csv('sample_data.csv')
    
    # Allow only read operations
    permissions = [
        create_permission('Read', 'allow'),
        create_permission('Bash', 'allow'),
        create_permission('edit_file', 'reject'),
        create_permission('create_file', 'reject'),
    ]
    
    options = AmpOptions(permissions=permissions)
```

**Key insight**: Use permissions to prevent the agent from modifying data during analysis.

### Example 3: Code Generation

```python
async def generate_visualization_code():
    """Generate Python code for visualizations"""
    prompt = """
    Generate Python code to create a bar chart showing average salary by city
    using the data from sample_data.csv. Use matplotlib.
    
    Only provide the code, don't execute it.
    """
```

**Use case**: Get code snippets without executing them, perfect for learning or documentation.

### Example 4: Interactive Assistant

```python
async def ask_amp(question: str):
    """Ask development questions"""
    response = ""
    async for message in execute(question, options=options):
        # Collect responses
        ...
    return response
```

## Permission Strategies

### Read-Only Analysis
```python
permissions = [
    create_permission('Read', 'allow'),
    create_permission('edit_file', 'reject'),
    create_permission('create_file', 'reject'),
]
```
Safe for analyzing existing data without modifications.

### Code Generation Only
```python
permissions = [
    create_permission('Read', 'allow'),
    create_permission('Bash', 'reject'),
    create_permission('edit_file', 'reject'),
]
```
Agent can read files and generate code but not execute or modify.

### Full Access
```python
options = AmpOptions(dangerously_allow_all=True)
```
Use when you want the agent to execute code and modify files (use with caution).

## Customization Ideas

- **Custom datasets**: Replace sample data with your own CSV/JSON files
- **Specific analyses**: Request correlation analysis, outlier detection, etc.
- **Visualization generation**: Create plots, charts, and dashboards
- **Data cleaning**: Ask agent to identify and handle missing values
- **Statistical tests**: Request hypothesis testing, regression analysis
- **Report generation**: Create markdown or HTML reports

## Common Analysis Tasks

### Exploratory Data Analysis
```python
prompt = """
Analyze dataset.csv and provide:
1. Summary statistics for all numerical columns
2. Distribution of categorical variables
3. Missing value analysis
4. Correlation between variables
5. Any notable patterns or outliers
"""
```

### Data Cleaning
```python
prompt = """
Examine dataset.csv for data quality issues:
1. Identify missing values and suggest handling strategies
2. Find duplicate records
3. Detect outliers in numerical columns
4. Check for inconsistent formatting
"""
```

### Visualization Code
```python
prompt = """
Generate Python code using matplotlib to create:
1. Histogram of age distribution
2. Bar chart of category counts
3. Scatter plot of variable1 vs variable2
4. Box plot to show salary by department
"""
```

## Best Practices

1. **Start with read-only permissions** when exploring new datasets
2. **Collect responses** into variables for further processing
3. **Clean up temporary files** after analysis
4. **Combine with pandas** for powerful data manipulation
5. **Generate code first** before executing to review what will run

## Real-World Applications

- Exploratory data analysis (EDA)
- Data quality assessment
- Quick statistical analysis
- Visualization code generation
- Data cleaning automation
- Report generation
- Dataset documentation
- Feature engineering assistance

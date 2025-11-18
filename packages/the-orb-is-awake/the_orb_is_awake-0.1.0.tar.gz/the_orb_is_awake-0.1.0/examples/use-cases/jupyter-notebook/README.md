# Jupyter Notebook Use Case

Interactive notebook examples for exploration and prototyping with the Amp SDK.

## Overview

This example demonstrates how to use the Amp SDK in Jupyter notebooks for interactive development, data analysis, and experimentation. Perfect for data scientists and researchers who prefer notebook-based workflows.

## What You'll Learn

- Using Amp SDK in Jupyter/IPython environments
- Interactive exploration with the agent
- Combining Amp with data science libraries
- Iterative analysis and code generation
- Building reusable notebook workflows

## Requirements

```bash
pip install amp-sdk jupyter pandas matplotlib
```

## Usage

### Start Jupyter

```bash
jupyter notebook
```

Then open `jupyter_notebook.ipynb` in your browser.

### Alternative: JupyterLab

```bash
pip install jupyterlab
jupyter lab
```

## Key Features

### Interactive Execution

Run cells interactively to:
- Explore data step by step
- Iterate on analysis tasks
- Generate and test code snippets
- Document findings alongside code

### Rich Output

Notebooks display:
- Agent responses in formatted markdown
- Data visualizations
- Code execution results
- Error messages and debugging info

### Reproducible Workflows

- Save complete analysis workflows
- Share notebooks with colleagues
- Document methodology and findings
- Rerun analysis with new data

## Common Notebook Patterns

### Setup Cell

```python
import asyncio
from amp_sdk import execute, AmpOptions, create_permission
import pandas as pd
import matplotlib.pyplot as plt

# Configure notebook for async
%matplotlib inline
```

### Quick Analysis

```python
# Analyze a dataset
prompt = "Analyze sales_data.csv and show summary statistics"
options = AmpOptions(dangerously_allow_all=True)

async for message in execute(prompt, options=options):
    if message.type == 'assistant':
        for content in message.message.content:
            if content.type == 'text':
                print(content.text)
```

### Code Generation

```python
# Generate visualization code
prompt = """
Create a matplotlib visualization showing:
1. Sales trends over time
2. Top 10 products by revenue
3. Regional sales distribution
"""

# Collect generated code
code = ""
async for message in execute(prompt, options=options):
    if message.type == 'assistant':
        for content in message.message.content:
            if content.type == 'text':
                code += content.text

# Display the code
print(code)

# Execute it (optional)
# exec(code)
```

### Iterative Refinement

```python
# First analysis
await ask_amp("What are the top 5 selling products?")

# Dig deeper based on results
await ask_amp("Show me sales trends for product XYZ")

# Generate follow-up visualization
await ask_amp("Create a chart comparing XYZ to similar products")
```

## Notebook Best Practices

1. **Use async properly**: Wrap execute calls in async functions or use `asyncio.run()`
2. **Clear outputs**: Clear cell outputs before sharing notebooks
3. **Document as you go**: Add markdown cells explaining your analysis
4. **Separate concerns**: Use different cells for different tasks
5. **Save regularly**: Notebooks can lose state if kernel crashes

## Integration with Data Science Stack

### Pandas Integration

```python
# Load data with pandas
df = pd.read_csv('data.csv')

# Ask Amp to analyze it
prompt = f"""
I have a DataFrame with columns: {df.columns.tolist()}
Suggest interesting analyses and visualizations for this data.
"""
```

### Matplotlib/Seaborn

```python
# Generate plotting code
prompt = "Create a seaborn pairplot for these numerical columns"

# Agent generates code using your preferred viz library
```

### NumPy/SciPy

```python
# Statistical analysis
prompt = """
Perform statistical analysis on this dataset:
- Normality tests
- Correlation analysis
- Hypothesis testing
"""
```

## Example Workflows

### Exploratory Data Analysis

1. Load dataset with pandas
2. Ask Amp for initial insights
3. Generate summary statistics
4. Create visualizations
5. Identify patterns and anomalies
6. Document findings

### Code Learning

1. Ask Amp to explain a concept
2. Request example code
3. Run and modify examples
4. Ask follow-up questions
5. Build your own implementations

### Data Cleaning

1. Load messy dataset
2. Ask Amp to identify issues
3. Generate cleaning code
4. Review and execute
5. Validate cleaned data
6. Save results

## Comparison to Python Script

**Notebook Advantages:**
- Interactive exploration
- Visual feedback
- Easy iteration
- Rich documentation
- Share findings with visualizations

**Script Advantages:**
- Production deployment
- Automated workflows
- Version control friendly
- Easier testing
- Better for CI/CD

Choose notebooks for **exploration** and scripts for **automation**.

## Tips for Success

1. **Start simple**: Begin with basic queries and build complexity
2. **Inspect outputs**: Review agent responses before executing generated code
3. **Use permissions**: Control what the agent can modify
4. **Save checkpoints**: Save notebook state before risky operations
5. **Combine approaches**: Use notebooks for exploration, scripts for production

## Real-World Applications

- Data exploration and EDA
- Prototyping ML pipelines
- Teaching and education
- Research documentation
- Quick analysis and reporting
- Code learning and experimentation
- Collaborative data science
- Presentation preparation

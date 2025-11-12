# Code Analyzer

[![PyPI version](https://badge.fury.io/py/code_analyzer.svg)](https://badge.fury.io/py/code-analyzer)
[![Python Support](https://img.shields.io/pypi/pyversions/code_analyzer.svg)](https://pypi.org/project/code_analyzer/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Enterprise-grade code complexity analyzer supporting ** mutiple programming languages** with standardized metrics and intelligent language detection.

## Key Features

- **14 Language Support**: SQL (Oracle, SQL Server, MySQL, PostgreSQL, BigQuery, Snowflake, Spark SQL, Redshift, SQLite, Sybase, DB2), Python, PySpark, SAS
- **Standardized Scoring**: Unified 0-100 complexity scale across all languages
- **Enterprise Metrics**: 10-dimension analysis framework with business-friendly thresholds
- **Intelligent Detection**: Automatic language detection with content-based analysis
- **CLI Interface**: Modern Click-based command-line interface
- **Extensible Architecture**: Plugin-based system for easy language additions

## 📦 Installation

```bash
pip install pyspcodeanalyzer
```

## 🛠️ Quick Start

### CLI Usage

Analyze a single file:
```bash
code_analyzer analyze examples/sample.py
```

Analyze entire directory:
```bash
code_analyzer analyze src/ --recursive
```

Analyze code directly:
```bash
code_analyzer analyze-code "SELECT * FROM users WHERE active = 1" --language oracle
```

List supported languages:
```bash
code_analyzer languages
```

View metrics information:
```bash
code_analyzer metrics
```

### Python API

```python
from code_analyzer.core.registry import get_analyzer

# Analyze Python code
analyzer = get_analyzer("python")
result = analyzer.analyze_source("""
    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
""")

print(f"Complexity Score: {result.total_score}/100")
print(f"Complexity Level: {result.classification}")
```

## 📊 Supported Languages

| Language | Extensions | Key Features |
|----------|------------|--------------|
| **Python** | `.py` | Functions, classes, async/await, decorators, comprehensions |
| **PySpark** | `.py` | DataFrame operations, RDD transformations, Spark SQL |
| **SAS** | `.sas` | DATA steps, PROC procedures, macro programming |
| **Oracle** | `.sql`, `.pkb`, `.pks` | PL/SQL packages, procedures, functions, triggers |
| **SQL Server** | `.sql` | T-SQL stored procedures, functions, triggers, SSIS |
| **MySQL** | `.sql` | Stored procedures, functions, triggers, events |
| **PostgreSQL** | `.sql` | PL/pgSQL, extensions, custom types, table inheritance |
| **BigQuery** | `.sql` | Standard SQL, UDFs, ML functions, nested data |
| **Snowflake** | `.sql` | JavaScript UDFs, streams, tasks, time travel |
| **Spark SQL** | `.sql` | DataFrames, Catalyst optimizer, bucketing |
| **Redshift** | `.sql` | Stored procedures, external tables, Spectrum |
| **SQLite** | `.sql` | Triggers, views, CTEs, JSON functions |
| **Sybase** | `.sql`, `.db` | ASE procedures, functions, triggers |
| **DB2** | `.sql` | Stored procedures, UDFs, XML support |

## 📈 Complexity Scoring System

### 10-Dimension Analysis Framework

Each language is analyzed across these standardized dimensions:

1. **SQL Logic Complexity** - Query complexity, joins, subqueries
2. **Utility Complexity** - Procedures, functions, stored logic
3. **Data Operations** - CRUD operations, data transformations
4. **Control Flow** - Conditional logic, loops, branching
5. **Error Handling** - Exception handling, validation
6. **File I/O & External Integration** - External data sources, APIs
7. **Performance & Optimization** - Indexing, partitioning, caching
8. **Security & Access Control** - Authentication, authorization, encryption
9. **ODS Output Delivery** - Reporting, output generation
10. **Execution Control** - Transaction management, concurrency

### Scoring Scale

- **0-30**: 🟢 **Simple** - Basic operations, minimal complexity
- **31-60**: 🟡 **Medium** - Moderate complexity, some advanced features
- **61-80**: 🟠 **Complex** - Advanced operations, multiple integrations
- **81-100**: 🔴 **Very Complex** - Highly sophisticated, enterprise-grade code

## 🔧 Configuration

### Custom Weights

Create `config.yaml` to customize dimension weights:

```yaml
weights:
  script_size_structure: 10
  dependency_footprint: 10
  analytics_depth: 10
  sql_reporting_logic: 10
  transformation_logic: 10
  utility_complexity: 10
  execution_control: 10
  file_io_external_integration: 10
  ods_output_delivery: 10
  error_handling_optimization: 10

include_cyclomatic: false

classification_thresholds:
  simple: 30
  medium: 60
  complex: 80
  very_complex: 100
```

### Environment Variables

```bash
export CODE_ANALYZER_CONFIG=/path/to/config.yaml
export CODE_ANALYZER_LOG_LEVEL=INFO
```

## 📋 CLI Commands

### analyze
Analyze files or directories for code complexity.

```bash
code_analyzer analyze [PATH] [OPTIONS]

Options:
  --recursive, -r    Analyze directories recursively
  --language, -l     Force specific language detection
  --output, -o       Output format (text, json, csv)
  --threshold, -t    Minimum complexity threshold to report
  --config, -c       Custom configuration file path
```

### analyze-code
Analyze code directly from command line.

```bash
code_analyzer analyze-code [CODE] --language [LANG]

Options:
  --language, -l     Programming language (required)
  --output, -o       Output format (text, json)
```

### languages
List all supported programming languages.

```bash
code_analyzer languages

Options:
  --verbose, -v      Show detailed language information
```

### metrics
Show information about complexity metrics and scoring.

```bash
code_analyzer metrics

Options:
  --language, -l     Show metrics for specific language
  --weights, -w      Display current weight configuration
```

### version
Display version information.

```bash
code_analyzer version
```

## 🏗️ Architecture

The Code Analyzer follows a modular, enterprise-grade architecture:

```
code_analyzer/
├── core/                   # Core analysis engine
│   ├── analyzer_base.py    # Base analyzer interface
│   ├── registry.py         # Language registry & detection
│   ├── metrics.py          # Centralized metrics system
│   └── exception.py        # Exception hierarchy
├── analyzers/      # Language-specific analyzers
│   ├── python_analyzer.py
│   ├── oracle_analyzer.py
│   ├── sas_analyzer.py
│   └── ...
├── config/                 # Configuration management
│   ├── loader.py           # Configuration loader
│   └── defaults/
│       └── config.yaml     # Default configuration
├── reporters/              # Output formatting[TBD]
│   ├── __init__.py
│  
└── cli.py          # Command-line interface
```
## 🔌 Extending the Analyzer

Add support for new languages by implementing the `AnalyzerBase` interface:

```python
from code_analyzer.core.analyzer_base import AnalyzerBase
from code_analyzer.core.registry import analyzer_registry

class CustomAnalyzer(AnalyzerBase):
    language = "custom"
    
    def analyze_code(self, code: str) -> AnalysisResult:
        # Implement your analysis logic
        pass
    
    def _calculate_metrics(self, code: str) -> Dict[str, int]:
        # Calculate complexity metrics
        pass

# Register your analyzer
analyzer_registry.register_analyzer("custom", CustomAnalyzer)
```

## 🧪 Testing

Run the test suite:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=code_analyzer --cov-report=html

# Run specific test
pytest tests/test_sas_metrics.py -v
```

## 📝 Examples

### Enterprise SAS Analysis
```bash
code_analyzer analyze examples/sample.sas
```

```
📊  Code Complexity Analysis Results
============================================================

📊 Summary:
   Total Files: 1
   Average Score: 35.0/100
   Complexity Distribution:
     Medium: 1 files (100.0%)

📁 Individual Results:
----------------------------------------
File: examples/sample_sas_test.sas
Language: sas
Score: 35/100 (Medium)
Cyclomatic: 2
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by enterprise code analysis needs
- Built with modern Python packaging standards
- Designed for scalable, multi-language analysis

## 📞 Support

- **Documentation**: [Read the Docs](https://code_analyzer.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/code_analyzer/code-analyzer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/code_analyzer/code_analyzer/discussions)

---

**Made with ❤️ for the developer community**

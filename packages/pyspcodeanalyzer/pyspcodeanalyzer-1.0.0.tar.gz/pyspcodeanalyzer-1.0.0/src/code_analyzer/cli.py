#!/usr/bin/env python3
"""
Enterprise Code Analyzer CLI

A comprehensive command-line interface for analyzing code complexity across
13 programming languages with enterprise-grade features.

Features:
- Auto language detection
- Configurable weights and thresholds
- Multiple output formats (JSON, CSV, detailed report)
- Batch processing
- Enterprise metrics validation
- 0-100 intuitive scoring system

Author: Code Analyzer Team
Version: 2.0.0
Date: 2025-11-11
"""

import click
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from code_analyzer.__version__ import get_full_version_info, SUPPORTED_LANGUAGES

from .core.registry import analyzer_registry
from .core.exception import (
    UnsupportedLanguageError, 
    InvalidCodeError, 
    AnalysisError,
    FileProcessingError
)
from .config.loader import load_config
from .core.metrics import get_standard_metrics


class AnalyzerConfig:
    """Configuration context for CLI operations."""
    
    def __init__(self):
        self.config = {}
        self.quiet_mode = False
        self.verbose_mode = False

    def load_configuration(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        try:
            if config_path:
                if not os.path.exists(config_path):
                    raise FileProcessingError(f"Configuration file not found: {config_path}")
                self.config = load_config(config_path)
            else:
                # Load default configuration
                self.config = load_config()
            
            return self.config
            
        except Exception as e:
            raise FileProcessingError(f"Failed to load configuration: {str(e)}")

    def detect_language(self, file_path: str) -> Optional[str]:
        """Auto-detect programming language from file extension and content."""
        extension_map = {
            '.sas': 'sas',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.scala': 'scala',
            '.kt': 'kotlin'
        }
        
        extension = Path(file_path).suffix.lower()
        
        # Special handling for Python files - check if it's PySpark
        if extension == '.py':
            return self._detect_python_variant(file_path)
        
        # Handle SQL files and .db files - detect dialect from filename and content
        if extension in ['.sql', '.db', '.ddl', '.dml']:
            return self._detect_sql_dialect(file_path)
        
        return extension_map.get(extension)

    def _detect_python_variant(self, file_path: str) -> str:
        """Detect if Python file is regular Python or PySpark."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
            
            # PySpark-specific patterns
            pyspark_patterns = [
                'from pyspark', 'import pyspark', 'sparkcontext', 'sparksession', 
                'sparkconf', 'spark.sql', 'pyspark.sql', 'pyspark.pandas',
                'rdd.', 'dataframe.', '.rdd', '.df', 'spark_context',
                'spark_session', 'to_pandas', 'from_pandas', 'spark.read',
                'spark.write', 'pyspark.streaming', 'pyspark.mllib'
            ]
            
            # Need at least one strong PySpark indicator
            if any(pattern in content for pattern in pyspark_patterns):
                return 'pyspark'
                
        except Exception:
            # If content analysis fails, fall back to python
            pass
            
        return 'python'

    def _detect_sql_dialect(self, file_path: str) -> str:
        """Detect SQL dialect from filename and content analysis."""
        filename = Path(file_path).name.lower()
        
        # Check filename for hints first
        filename_patterns = {
            'oracle': ['oracle', 'plsql'],
            'mysql': ['mysql'],
            'postgresql': ['postgresql', 'pgsql', 'postgres'],
            'sqlserver': ['sqlserver', 'tsql', 'mssql'],
            'sybase': ['sybase', 'ase'],
            'bigquery': ['bigquery', 'bq'],
            'snowflake': ['snowflake', 'snowsql'],
            'sparksql': ['spark', 'sparksql'],
            'db2': ['db2'],
            'redshift': ['redshift'],
            'sqlite': ['sqlite']
        }
        
        for dialect, patterns in filename_patterns.items():
            if any(pattern in filename for pattern in patterns):
                return dialect
        
        # Analyze file content for dialect-specific keywords
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(10000).upper()  # Read first 10KB
                
            # SQL dialect detection patterns (case-insensitive)
            dialect_signatures = {
                'sybase': [
                    'CONVERT(', 'PATINDEX(', 'CHARINDEX(', 'PARSENAME(',
                    'RAISERROR', 'WAITFOR', '@@IDENTITY', '@@ROWCOUNT',
                    'DECLARE @', 'SET @', 'WHILE @@FETCH_STATUS',
                    'PRINT ', 'SYBASE', 'ASE'
                ],
                'oracle': [
                    'DUAL', 'SYSDATE', 'ROWNUM', 'DECODE(', 'NVL(',
                    'CONNECT BY', 'START WITH', 'PRIOR', 'PRAGMA',
                    'DBMS_', 'UTL_', 'PL/SQL', 'PACKAGE', 'PROCEDURE',
                    'FUNCTION', 'BEGIN', 'END;', 'EXCEPTION'
                ],
                'sqlserver': [
                    'GETDATE()', 'ISNULL(', 'LEN(', 'SUBSTRING(',
                    'CHARINDEX(', 'PATINDEX(', 'STUFF(', 'REPLACE(',
                    'WITH (NOLOCK)', 'IDENTITY(', 'NEWID()',
                    'TOP (', 'CROSS APPLY', 'OUTER APPLY'
                ],
                'mysql': [
                    'AUTO_INCREMENT', 'LIMIT ', 'CONCAT(', 'IFNULL(',
                    'DATE_FORMAT(', 'STR_TO_DATE(', 'NOW()',
                    'UNIX_TIMESTAMP(', 'REPLACE(', 'SUBSTRING(',
                    'ENGINE=', 'CHARSET=', 'COLLATE='
                ],
                'postgresql': [
                    'SERIAL', 'BIGSERIAL', 'GENERATE_SERIES(',
                    'EXTRACT(', 'DATE_TRUNC(', 'COALESCE(',
                    'ARRAY[', 'JSONB', 'RETURNING', 'CONFLICT',
                    'UPSERT', 'LATERAL', 'ORDINALITY'
                ],
                'bigquery': [
                    'SELECT AS STRUCT', 'SELECT AS VALUE', 'UNNEST(',
                    'ARRAY_AGG(', 'STRING_AGG(', 'EXTRACT(',
                    'TIMESTAMP(', 'DATE(', 'DATETIME(',
                    'GENERATE_', 'ML.', 'SAFE_'
                ],
                'snowflake': [
                    'WAREHOUSE', 'VARIANT', 'FLATTEN(',
                    'PARSE_JSON(', 'TRY_PARSE_JSON(',
                    'OBJECT_CONSTRUCT(', 'ARRAY_CONSTRUCT(',
                    'GENERATOR(', 'SAMPLE(', 'QUALIFY'
                ],
                'sparksql': [
                    'DELTA', 'PARQUET', 'COLLECT_LIST(',
                    'COLLECT_SET(', 'EXPLODE(', 'POSEXPLODE(',
                    'LATERAL VIEW', 'RLIKE', 'REGEXP_EXTRACT('
                ],
                'db2': [
                    'CURRENT TIMESTAMP', 'CURRENT DATE',
                    'DECLARE CURSOR', 'FETCH FROM', 'VALUES',
                    'XMLEXISTS(', 'XMLQUERY(', 'XMLTABLE('
                ],
                'redshift': [
                    'DISTKEY', 'SORTKEY', 'ENCODE', 'DISTSTYLE',
                    'COPY', 'UNLOAD', 'ANALYZE COMPRESSION',
                    'VACUUM', 'APPROXIMATE'
                ],
                'sqlite': [
                    'AUTOINCREMENT', 'PRAGMA', 'SQLITE_',
                    'ROWID', 'WITHOUT ROWID', 'STRICT'
                ]
            }
            
            # Score each dialect based on keyword matches
            scores = {}
            for dialect, keywords in dialect_signatures.items():
                score = sum(1 for keyword in keywords if keyword in content)
                if score > 0:
                    scores[dialect] = score
            
            # Return dialect with highest score
            if scores:
                return max(scores.items(), key=lambda x: x[1])[0]
                
        except Exception:
            # If content analysis fails, fall through to default
            pass
        
        # Default fallback - return oracle for generic SQL
        return 'oracle'

    def get_analyzer(self, language: str):
        """Get analyzer instance for specified language."""
        try:
            return analyzer_registry.get_analyzer(language)
        except UnsupportedLanguageError:
            # List available languages for better error message
            available = analyzer_registry.list_supported_languages()
            raise UnsupportedLanguageError(
                f"Language '{language}' not supported. Available languages: {', '.join(available)}"
            )

    def analyze_file(self, file_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Analyze a single file."""
        if not os.path.exists(file_path):
            raise FileProcessingError(f"File not found: {file_path}")
        
        # Auto-detect language if not specified
        if not language:
            language = self.detect_language(file_path)
            if not language:
                raise UnsupportedLanguageError(f"Could not detect language for file: {file_path}")
        
        # Get analyzer
        analyzer = self.get_analyzer(language)
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            raise FileProcessingError(f"Failed to read file {file_path}: {str(e)}")
        
        # Analyze code
        try:
            result = analyzer.analyze_source(code, file_path)
            
            # Convert to dictionary for JSON serialization
            return {
                'file_path': result.path,
                'language': result.language,
                'total_score': result.total_score,
                'classification': result.classification,
                'cyclomatic_complexity': result.cyclomatic,
                'metrics': dict(result.metrics),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise AnalysisError(f"Failed to analyze {file_path}: {str(e)}")

    def analyze_directory(self, dir_path: str, language: Optional[str] = None, recursive: bool = False) -> List[Dict[str, Any]]:
        """Analyze all supported files in a directory."""
        if not os.path.isdir(dir_path):
            raise FileProcessingError(f"Directory not found: {dir_path}")
        
        results = []
        path_obj = Path(dir_path)
        
        # Define file patterns to search for
        patterns = ['*.sas', '*.sql', '*.py', '*.js', '*.ts', '*.java', '*.c', '*.cpp', '*.cs', '*.go', '*.rs', '*.rb', '*.php']
        
        # Search for files
        files = []
        if recursive:
            for pattern in patterns:
                files.extend(path_obj.rglob(pattern))
        else:
            for pattern in patterns:
                files.extend(path_obj.glob(pattern))
        
        # Analyze each file
        for file_path in files:
            try:
                result = self.analyze_file(str(file_path), language)
                results.append(result)
            except Exception as e:
                if not self.quiet_mode:
                    click.echo(f"⚠️  Warning: Skipped {file_path}: {str(e)}", err=True)
                continue
        
        return results

    def format_text_output(self, results: List[Dict[str, Any]]) -> str:
        """Format results as human-readable text."""
        if not results:
            return "No files analyzed."
        
        output = []
        output.append("🔍 Code Complexity Analysis Results")
        output.append("=" * 60)
        output.append("")
        
        # Summary statistics
        total_files = len(results)
        avg_score = sum(r['total_score'] for r in results) / total_files
        complexity_counts = {}
        
        for result in results:
            classification = result['classification']
            complexity_counts[classification] = complexity_counts.get(classification, 0) + 1
        
        output.append("📊 Summary:")
        output.append(f"   Total Files: {total_files}")
        output.append(f"   Average Score: {avg_score:.1f}/100")
        output.append("   Complexity Distribution:")
        for level, count in complexity_counts.items():
            percentage = (count / total_files) * 100
            output.append(f"     {level}: {count} files ({percentage:.1f}%)")
        output.append("")
        
        # Individual file results
        output.append("📁 Individual Results:")
        output.append("-" * 40)
        
        for result in results:
            output.append(f"File: {result['file_path']}")
            output.append(f"Language: {result['language']}")
            output.append(f"Score: {result['total_score']}/100 ({result['classification']})")
            output.append(f"Cyclomatic: {result['cyclomatic_complexity']}")
            
            if self.verbose_mode:
                output.append("Metrics breakdown:")
                for metric, value in result['metrics'].items():
                    output.append(f"  {metric}: {value}")
            
            output.append("")
        
        return "\n".join(output)

    def format_json_output(self, results: List[Dict[str, Any]]) -> str:
        """Format results as JSON."""
        return json.dumps(results, indent=2)

    def format_csv_output(self, results: List[Dict[str, Any]]) -> str:
        """Format results as CSV."""
        if not results:
            return ""
        
        # Collect all metric names
        all_metrics = set()
        for result in results:
            all_metrics.update(result['metrics'].keys())
        
        # CSV headers
        headers = ['file_path', 'language', 'total_score', 'classification', 'cyclomatic_complexity']
        headers.extend(sorted(all_metrics))
        headers.append('analysis_timestamp')
        
        # Generate CSV content
        output = []
        output.append(','.join(headers))
        
        for result in results:
            row = [
                result['file_path'],
                result['language'],
                str(result['total_score']),
                result['classification'],
                str(result['cyclomatic_complexity'])
            ]
            
            # Add metric values
            for metric in sorted(all_metrics):
                row.append(str(result['metrics'].get(metric, '')))
            
            row.append(result['analysis_timestamp'])
            output.append(','.join(row))
        
        return '\n'.join(output)

    def write_output(self, content: str, output_path: Optional[str] = None):
        """Write output to file or stdout."""
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                if not self.quiet_mode:
                    click.echo(f"✅ Results written to {output_path}")
            except Exception as e:
                raise FileProcessingError(f"Failed to write output file {output_path}: {str(e)}")
        else:
            click.echo(content)


# Global configuration object for Click context
analyzer_config = AnalyzerConfig()


@click.group()
@click.option('--config', '-c', help='Path to custom configuration file')
@click.option('--quiet', '-q', is_flag=True, help='Quiet mode - minimal output')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output with detailed metrics')
@click.pass_context
def cli(ctx, config, quiet, verbose):
    """
    🔍 Enterprise Code Analyzer
    
    A comprehensive tool for analyzing code complexity across 13 programming languages
    with enterprise-grade features and 0-100 scoring system.
    
    Supported Languages: sas, oracle, sqlserver, mysql, postgresql, python, bigquery,
    snowflake, sparksql, pyspark, db2, redshift, sqlite
    """
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Set global configuration
    analyzer_config.quiet_mode = quiet
    analyzer_config.verbose_mode = verbose
    
    try:
        analyzer_config.load_configuration(config)
    except Exception as e:
        click.echo(f"❌ Configuration error: {str(e)}", err=True)
        ctx.exit(1)


@cli.command()
@click.argument('files', nargs=-1, required=True, type=click.Path(exists=True))
@click.option('--language', '-l', help='Force specific language (auto-detect if not specified)')
@click.option('--recursive', '-r', is_flag=True, help='Recursively analyze directories')
@click.option('--output-format', '-f', 
              type=click.Choice(['text', 'json', 'csv']), 
              default='text', 
              help='Output format')
@click.option('--output', '-o', 
              type=click.Path(),
              help='Output file path (stdout if not specified)')
@click.option('--include-cyclomatic', is_flag=True, 
              help='Include cyclomatic complexity bonus')
def analyze(files, language, recursive, output_format, output, include_cyclomatic):
    """
    Analyze code complexity for files or directories.
    
    Examples:
    
        # Analyze single file with auto-detection
        code-analyzer analyze myfile.py
        
        # Analyze with specific language
        code-analyzer analyze --language python myfile.py
        
        # Analyze directory recursively  
        code-analyzer analyze --recursive ./src/
        
        # Custom output format
        code-analyzer analyze --output-format json --output results.json myfile.sas
    """
    try:
        # Set cyclomatic flag in config
        if include_cyclomatic:
            analyzer_config.config['include_cyclomatic'] = True
        
        # Analyze files
        results = []
        for file_or_dir in files:
            if os.path.isfile(file_or_dir):
                result = analyzer_config.analyze_file(file_or_dir, language)
                results.append(result)
            elif os.path.isdir(file_or_dir):
                dir_results = analyzer_config.analyze_directory(file_or_dir, language, recursive)
                results.extend(dir_results)
            else:
                raise FileProcessingError(f"Path not found: {file_or_dir}")
        
        if not results:
            click.echo("No files were analyzed.", err=True)
            return
        
        # Format and output results
        if output_format == 'json':
            content = analyzer_config.format_json_output(results)
        elif output_format == 'csv':
            content = analyzer_config.format_csv_output(results)
        else:
            content = analyzer_config.format_text_output(results)
        
        analyzer_config.write_output(content, output)
        
    except (UnsupportedLanguageError, InvalidCodeError, AnalysisError, FileProcessingError) as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        raise click.ClickException(str(e))
    except Exception as e:
        if not analyzer_config.quiet_mode:
            click.echo(f"💥 Unexpected error: {str(e)}", err=True)
        raise click.ClickException(f"Unexpected error: {str(e)}")


@cli.command()
def languages():
    """List all supported programming languages with details."""
    try:
        available_languages = analyzer_registry.list_supported_languages()
        
        click.echo("🌍 Supported Programming Languages")
        click.echo("=" * 50)
        click.echo()
        
        for language in sorted(available_languages):
            try:
                analyzer = analyzer_registry.get_analyzer(language)
                doc_desc = analyzer.__class__.__doc__.split('.')[0] if analyzer.__class__.__doc__ else 'Code complexity analyzer'
                click.echo(f"✅ {language.upper():<12} - {doc_desc}")
            except Exception:
                click.echo(f"⚠️  {language.upper():<12} - Analyzer not available")
        
        click.echo()
        click.echo(f"Total: {len(available_languages)} languages supported")
        click.echo()
        click.echo("💡 Use --language parameter to force specific language detection")
        click.echo("💡 Without --language, auto-detection is used based on file extension")
        
    except Exception as e:
        click.echo(f"❌ Error listing languages: {str(e)}", err=True)
        raise click.ClickException(str(e))


@cli.command()
def metrics():
    """Show information about standard complexity metrics."""
    try:
        standard_metrics = get_standard_metrics()
        
        click.echo("📏 Standard Complexity Metrics")
        click.echo("=" * 50)
        click.echo()
        click.echo("The code analyzer evaluates complexity across 10 dimensions:")
        click.echo()
        
        metric_descriptions = {
            "script_size_structure": "Code size, functions, nesting depth, structural complexity",
            "dependency_footprint": "External dependencies, database connections, integration complexity",
            "analytics_depth": "Advanced analytics, statistical functions, analytical processing",
            "sql_reporting_logic": "SQL query complexity, joins, subqueries, reporting logic",
            "transformation_logic": "Data transformation operations, DML complexity, manipulation",
            "utility_complexity": "Stored procedures, functions, parameters, utility code",
            "execution_control": "Transaction management, control flow, process orchestration",
            "file_io_external_integration": "File operations, external system integration, APIs",
            "ods_output_delivery": "Output generation, result sets, reporting delivery",
            "error_handling_optimization": "Exception handling, performance optimization, quality"
        }
        
        for i, metric in enumerate(standard_metrics, 1):
            desc = metric_descriptions.get(metric, "Complexity metric")
            click.echo(f"{i:2}. {metric}")
            click.echo(f"    {desc}")
            click.echo()
        
        click.echo("📊 Scoring System:")
        click.echo("   • Each metric scored 1-4 (Simple → Very Complex)")
        click.echo("   • Each dimension contributes 0-10 points to total score")
        click.echo("   • Total score range: 0-100 points")
        click.echo("   • Classifications: 0-25 Simple, 26-50 Medium, 51-75 Complex, 76-100 Very Complex")
        click.echo()
        click.echo("⚙️  Weights and thresholds are configurable via config.yaml")
        
    except Exception as e:
        click.echo(f"❌ Error showing metrics: {str(e)}", err=True)
        raise click.ClickException(str(e))


@cli.command()
def version():
    """Show version and feature information."""
    version_info = get_full_version_info()
    
    click.echo("🔧 Enterprise Code Analyzer")
    click.echo("=" * 30)
    click.echo(f"Version: {version_info['version']}")
    click.echo(f"Build Date: {version_info['build_date']}")
    click.echo(f"Author: {version_info['author']}")
    click.echo(f"License: {version_info['license']}")
    click.echo(f"Python Requires: {version_info['python_requires']}")
    click.echo()
    click.echo("📋 Features:")
    for feature, enabled in version_info['features'].items():
        status = "✅" if enabled else "❌"
        feature_name = feature.replace('_', ' ').title()
        click.echo(f"  {status} {feature_name}")
    
    click.echo()
    click.echo(f"🌐 Supported Languages ({len(version_info['supported_languages'])}):")
    
    # Group languages for better display
    languages = version_info['supported_languages']
    sql_dialects = [lang for lang in languages if lang not in ['python', 'pyspark', 'sas']]
    other_languages = [lang for lang in languages if lang in ['python', 'pyspark', 'sas']]
    
    click.echo(f"  SQL Dialects ({len(sql_dialects)}): {', '.join(sorted(sql_dialects))}")
    click.echo(f"  Other Languages: {', '.join(sorted(other_languages))}")
    
    click.echo()
    click.echo("📊 Analysis Capabilities:")
    click.echo("• 10-dimension standardized metrics")
    click.echo("• 0-100 intuitive scoring system")
    click.echo("• Configurable weights and thresholds") 
    click.echo("• Enterprise-grade exception handling")
    click.echo("• Automatic language detection")
    click.echo("• Batch processing with directory scanning")
    click.echo("• Multiple output formats (text, JSON, CSV)")
    click.echo("• Real-time code analysis")
    
    click.echo()
    click.echo("🔗 Links:")
    click.echo(f"  Homepage: {version_info['url']}")
    click.echo("  Documentation: https://code-analyzer.readthedocs.io")
    click.echo("  Issues: https://github.com/codeanalyzer/code-analyzer/issues")


@cli.command()
@click.argument('code', type=click.STRING)
@click.option('--language', '-l', required=True, help='Programming language of the code')
@click.option('--output-format', '-f', 
              type=click.Choice(['text', 'json']), 
              default='text', 
              help='Output format')
def analyze_code(code, language, output_format):
    """
    Analyze code snippet directly from command line.
    
    Examples:
    
        # Analyze SAS code snippet
        code-analyzer analyze-code --language sas "proc print data=test;"
        
        # Analyze Python code with JSON output
        code-analyzer analyze-code --language python --output-format json "def test(): pass"
    """
    try:
        # Get analyzer
        analyzer = analyzer_config.get_analyzer(language)
        
        # Analyze code
        result = analyzer.analyze_source(code, "<stdin>")
        
        # Convert to dictionary for output
        result_dict = {
            'file_path': result.path,
            'language': result.language,
            'total_score': result.total_score,
            'classification': result.classification,
            'cyclomatic_complexity': result.cyclomatic,
            'metrics': dict(result.metrics),
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        # Format and output results
        if output_format == 'json':
            content = json.dumps(result_dict, indent=2)
        else:
            content = analyzer_config.format_text_output([result_dict])
        
        click.echo(content)
        
    except (UnsupportedLanguageError, InvalidCodeError, AnalysisError) as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        raise click.ClickException(str(e))
    except Exception as e:
        if not analyzer_config.quiet_mode:
            click.echo(f"💥 Unexpected error: {str(e)}", err=True)
        raise click.ClickException(f"Unexpected error: {str(e)}")


def main():
    """Entry point for the CLI application."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n⏹️  Analysis interrupted by user", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

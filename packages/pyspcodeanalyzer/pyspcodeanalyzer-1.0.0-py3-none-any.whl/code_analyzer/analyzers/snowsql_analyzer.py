# src/code_analyzer/analyzers/snowsql_analyzer.py
from ..core.analyzer_base import AnalyzerBase, AnalysisResult
from ..core.metrics import (
    metric_validator, 
    get_registry_weights, 
    get_registry_thresholds, 
    classify_complexity,
)
from ..core.exception import AnalysisError
from ..utils import read_file_if_exists

import re
from typing import Dict


class SnowSQLAnalyzer(AnalyzerBase):
    """
    SnowSQL code complexity analyzer with enterprise metrics integration.
    
    Evaluates SnowSQL scripts across 10 dimensions, each scored 1-4:
    - 1: Simple
    - 2: Medium
    - 3: Complex
    - 4: Very Complex
    
    Uses hybrid approach:
    - Config weights override registry defaults
    - Enterprise validation via metrics module
    - Standardized 0-100 scoring system
    """
    language = "snowsql"
    
    def __init__(self, config: dict = None):
        super().__init__(config=config or {})
        
        # Get registry defaults, then apply config overrides (consistent pattern)
        registry_weights = get_registry_weights()
        config_weights = self.config.get("weights") or {}
        self.weights = {**registry_weights, **config_weights}
        
        registry_thresholds = get_registry_thresholds()
        config_thresholds = self.config.get("classification_thresholds") or {}
        self.thresholds = {**registry_thresholds, **config_thresholds}
    
    def _calculate_cyclomatic_bonus(self, cyclomatic: int) -> int:
        """Calculate cyclomatic complexity bonus points (max +10)."""
        if cyclomatic <= 10:
            return 2
        elif cyclomatic <= 20:
            return 4
        elif cyclomatic <= 30:
            return 6
        elif cyclomatic <= 50:
            return 8
        else:
            return 10

    def analyze_source(self, code: str, path: str = "<string>") -> AnalysisResult:
        """Analyze SnowSQL source code and return complexity metrics."""
        include_cyclomatic = self.config.get("include_cyclomatic", False)
        
        # If code is None or empty, try to read from file path
        if not code and path and path != "<string>":
            file_content = read_file_if_exists(path)
            if file_content:
                code = file_content
        
        # Run complexity analysis
        analyzer = SnowSQLComplexity()
        analyzer.analyze(code)
        
        # Collect metrics (each 1-4)
        metrics = {
            "script_size_structure": analyzer.script_size_structure,
            "dependency_footprint": analyzer.dependency_footprint,
            "analytics_depth": analyzer.analytics_depth,
            "sql_reporting_logic": analyzer.sql_reporting_logic,
            "transformation_logic": analyzer.transformation_logic,
            "utility_complexity": analyzer.utility_complexity,
            "execution_control": analyzer.execution_control,
            "file_io_external_integration": analyzer.file_io_external_integration,
            "ods_output_delivery": analyzer.ods_output_delivery,
            "error_handling_optimization": analyzer.error_handling_optimization
        }
        
        # Use enterprise metrics module for validation and calculation
        try:
            # Validate metrics using enterprise validation
            validated_metrics = metric_validator.validate_all_metrics(metrics)
            
            # Calculate total score using config weights (0-100 scale)
            total_score = metric_validator.calculate_total_score(validated_metrics, self.weights)
            
            # Apply cyclomatic complexity bonus if enabled
            if include_cyclomatic:
                cyclomatic_bonus = self._calculate_cyclomatic_bonus(analyzer.cyclomatic)
                total_score = min(100, total_score + cyclomatic_bonus)
            
            # Use enterprise classification from metrics module
            complexity_level = classify_complexity(total_score).value
            
        except Exception as e:
            # Raise appropriate analysis error instead of fallback calculation
            raise AnalysisError(
                f"Failed to analyze {self.language} code: {str(e)}",
                language=self.language,
                file_path=path,
                original_error=e
            )

        return AnalysisResult(
            language=self.language,
            path=path,
            metrics=metrics,
            total_score=total_score,
            classification=complexity_level,
            cyclomatic=analyzer.cyclomatic,
        )
    
    
class SnowSQLComplexity:
    """
    Enterprise-grade SnowSQL complexity analyzer with comprehensive pattern detection.
    Each metric is scored 1 (Simple) to 4 (Very Complex) based on SnowSQL-specific patterns.
    """
    def __init__(self):
        # Initialize all metrics to minimum (Simple)
        self.script_size_structure = 1
        self.dependency_footprint = 1
        self.analytics_depth = 1
        self.sql_reporting_logic = 1          
        self.transformation_logic = 1
        self.utility_complexity = 1           
        self.execution_control = 1            
        self.file_io_external_integration = 1 
        self.ods_output_delivery = 1          
        self.error_handling_optimization = 1
        self.cyclomatic = 1
    
    def analyze(self, code: str) -> AnalysisResult:
        """
        Analyze SnowSQL source code and return complexity metrics.
        """
        if not code or not code.strip():
            return
    
        # Remove comments for accurate pattern matching
        code_no_comments = self._remove_comments(code)
        
        # Calculate nesting depth
        nesting_level = self._get_nesting_level(code_no_comments)

        # --- 1. SCRIPT SIZE & STRUCTURE ---
        # Enhanced: lines, procedures, functions, tasks, streams, dynamic tables
        lines = len([line for line in code.split('\n') if line.strip()])
        
        # Snowflake objects
        procedures = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?procedure\b', code_no_comments, re.IGNORECASE))
        functions = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?(function|secure\s+function)\b', code_no_comments, re.IGNORECASE))
        views = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?(view|secure\s+view|materialized\s+view)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Core Snowflake objects
        streams = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?stream\b', code_no_comments, re.IGNORECASE))
        tasks = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?task\b', code_no_comments, re.IGNORECASE))
        sequences = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?sequence\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Enterprise objects
        pipes = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?pipe\b', code_no_comments, re.IGNORECASE))
        stages = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?stage\b', code_no_comments, re.IGNORECASE))
        file_formats = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?file\s+format\b', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Advanced objects
        dynamic_tables = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?dynamic\s+table\b', code_no_comments, re.IGNORECASE))
        external_functions = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?external\s+function\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: small script
        if lines > 100 or procedures > 0 or functions > 0 or nesting_level > 1:
            score = 2  # Medium: moderate size, procedures, or basic nesting
        if lines > 500 or (procedures + functions) > 3 or views > 2 or streams > 0 or tasks > 0 or nesting_level > 3:
            score = 3  # Complex: large, multiple objects, streams/tasks, or deep nesting
        if lines > 2000 or (procedures + functions + views) > 8 or pipes > 0 or dynamic_tables > 0 or external_functions > 0 or nesting_level > 5:
            score = 4  # Very Complex: very large, many objects, pipes, dynamic tables, external functions, very deep nesting
        
        self.script_size_structure = score

        # --- 2. DEPENDENCY FOOTPRINT ---
        # Enhanced: databases, schemas, tables, views, shares, data exchanges
        databases = len(re.findall(r'\buse\s+database\s+\w+|\bfrom\s+\w+\.\w+\.\w+', code_no_comments, re.IGNORECASE))
        schemas = len(re.findall(r'\buse\s+schema\s+\w+|\bfrom\s+\w+\.\w+', code_no_comments, re.IGNORECASE))
        
        # Table references
        table_refs = len(re.findall(r'\bfrom\s+[\w\.]+|\bjoin\s+[\w\.]+|\binto\s+[\w\.]+', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Data sharing
        shares = len(re.findall(r'\bcreate\s+share|\bfrom\s+share\s+\w+', code_no_comments, re.IGNORECASE))
        data_exchanges = len(re.findall(r'\bdata\s+exchange\s+\w+', code_no_comments, re.IGNORECASE))
        
        # External references
        external_tables = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?external\s+table\b', code_no_comments, re.IGNORECASE))
        
        # Cross-database queries
        cross_db = len(re.findall(r'\w+\.\w+\.\w+', code_no_comments))
        
        score = 1  # Simple: single database/schema
        if databases > 0 or schemas > 0 or table_refs > 3:
            score = 2  # Medium: multiple schemas, several tables
        if table_refs > 10 or cross_db > 3 or external_tables > 0:
            score = 3  # Complex: many tables, cross-database, external tables
        if table_refs > 20 or cross_db > 8 or shares > 0 or data_exchanges > 0:
            score = 4  # Very Complex: extensive dependencies, data sharing, exchanges
        
        self.dependency_footprint = score

        # --- 3. ANALYTICS DEPTH ---
        # Enhanced: aggregations, window functions, semi-structured data, machine learning
        basic_agg = len(re.findall(r'\b(count|sum|avg|min|max|group\s+by)\b', code_no_comments, re.IGNORECASE))
        
        # Advanced aggregations
        advanced_agg = len(re.findall(r'\b(stddev|variance|median|percentile|listagg|array_agg)\b', code_no_comments, re.IGNORECASE))
        
        # Window functions
        window_funcs = len(re.findall(r'\b(row_number|rank|dense_rank|lead|lag|first_value|last_value|over\s*\()\b', code_no_comments, re.IGNORECASE))
        
        # Pivoting
        pivot_ops = len(re.findall(r'\bpivot\s*\(|\bunpivot\s*\(', code_no_comments, re.IGNORECASE))
        
        # CTEs and subqueries
        cte = len(re.findall(r'\bwith\s+\w+\s+as\s*\(', code_no_comments, re.IGNORECASE))
        recursive_cte = len(re.findall(r'\bwith\s+recursive\s+\w+', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Semi-structured data
        variant_ops = len(re.findall(r'\bvariant|\bobject|\barray\b', code_no_comments, re.IGNORECASE))
        json_ops = len(re.findall(r'\bparse_json|\bget|\bget_path|\bflatten\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Advanced analytics
        qualify = len(re.findall(r'\bqualify\b', code_no_comments, re.IGNORECASE))
        match_recognize = len(re.findall(r'\bmatch_recognize\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic queries
        if basic_agg > 0 or cte > 0 or variant_ops > 0:
            score = 2  # Medium: aggregations, CTEs, semi-structured data
        if window_funcs > 0 or advanced_agg > 0 or pivot_ops > 0 or json_ops > 3 or qualify > 0:
            score = 3  # Complex: window functions, pivots, complex JSON operations
        if recursive_cte > 0 or match_recognize > 0 or (window_funcs > 5 and json_ops > 5):
            score = 4  # Very Complex: recursive CTEs, pattern matching, heavy analytics
        
        self.analytics_depth = score

        # --- 4. SQL & REPORTING LOGIC ---
        # Enhanced: query complexity, joins, unions, result sets
        joins = len(re.findall(r'\b(inner\s+join|left\s+join|right\s+join|full\s+join|cross\s+join|join)\b', code_no_comments, re.IGNORECASE))
        unions = len(re.findall(r'\bunion\s+(all\s+)?', code_no_comments, re.IGNORECASE))
        
        # Query optimization hints and features
        hints = len(re.findall(r'\b(sample|tablesample)\b', code_no_comments, re.IGNORECASE))
        
        # Complex WHERE clauses
        complex_where = len(re.findall(r'\bwhere\s+.*\b(and|or)\b.*\b(and|or)\b', code_no_comments, re.IGNORECASE))
        
        # CASE statements
        case_stmt = len(re.findall(r'\bcase\s+when\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Snowflake-specific SQL features
        lateral_joins = len(re.findall(r'\blateral\s+flatten\b', code_no_comments, re.IGNORECASE))
        table_functions = len(re.findall(r'\btable\s*\(\s*\w+\s*\(', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic SELECT
        if joins >= 1 or case_stmt > 0 or unions > 0:
            score = 2  # Medium: joins, CASE statements
        if joins > 3 or unions > 1 or hints > 0 or complex_where > 0 or lateral_joins > 0:
            score = 3  # Complex: multiple joins, hints, lateral operations
        if joins > 8 or unions > 3 or table_functions > 0 or (lateral_joins > 0 and joins > 5):
            score = 4  # Very Complex: many joins, table functions, complex lateral operations
        
        self.sql_reporting_logic = score

        # --- 5. TRANSFORMATION LOGIC ---
        # Enhanced: DML, MERGE, data transformations, ELT patterns
        updates = len(re.findall(r'\bupdate\s+\w+', code_no_comments, re.IGNORECASE))
        inserts = len(re.findall(r'\binsert\s+into\b', code_no_comments, re.IGNORECASE))
        deletes = len(re.findall(r'\bdelete\s+from\b', code_no_comments, re.IGNORECASE))
        
        # Data type conversions
        conversions = len(re.findall(r'\b(cast|convert|try_cast|to_number|to_date|to_timestamp)\b', code_no_comments, re.IGNORECASE))
        
        # String operations
        string_ops = len(re.findall(r'\b(substr|substring|left|right|trim|ltrim|rtrim|upper|lower|replace|split|regexp_replace)\b', code_no_comments, re.IGNORECASE))
        
        # Date/time functions
        date_funcs = len(re.findall(r'\b(current_timestamp|dateadd|datediff|date_part|date_trunc|to_date|year|month|day)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Advanced transformations
        merge = len(re.findall(r'\bmerge\s+into\b', code_no_comments, re.IGNORECASE))
        copy_into = len(re.findall(r'\bcopy\s+into\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: ELT patterns
        create_table_as = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?table\s+\w+\s+as\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic SELECT
        if updates > 0 or inserts > 0 or conversions > 2 or date_funcs > 0:
            score = 2  # Medium: basic DML, conversions
        if merge > 0 or copy_into > 0 or string_ops > 5 or create_table_as > 0:
            score = 3  # Complex: MERGE, COPY INTO, extensive transformations, CTAS
        if merge > 2 or copy_into > 3 or (string_ops > 10 and conversions > 8):
            score = 4  # Very Complex: complex MERGE operations, heavy COPY INTO, extensive transformations
        
        self.transformation_logic = score

        # --- 6. UTILITY COMPLEXITY ---
        # Enhanced: procedures, functions, JavaScript UDFs, tasks, parameters
        # Parameters and variables
        params = len(re.findall(r'\$\w+|\?\w*', code_no_comments))
        declares = len(re.findall(r'\bdeclare\s+\w+', code_no_comments, re.IGNORECASE))
        
        # Control flow
        if_stmt = len(re.findall(r'\bif\s*\(', code_no_comments, re.IGNORECASE))
        while_loop = len(re.findall(r'\bwhile\s*\(', code_no_comments, re.IGNORECASE))
        for_loop = len(re.findall(r'\bfor\s*\(', code_no_comments, re.IGNORECASE))
        
        # TIER 2: JavaScript UDFs
        javascript_udfs = len(re.findall(r'\blanguage\s+javascript\b', code_no_comments, re.IGNORECASE))
        js_code = len(re.findall(r'\bas\s+\$\$.*?\$\$', code_no_comments, re.IGNORECASE | re.DOTALL))
        
        # Task scheduling
        task_schedule = len(re.findall(r'\bschedule\s*=\s*\'', code_no_comments, re.IGNORECASE))
        task_when = len(re.findall(r'\bwhen\s+system\$stream_has_data', code_no_comments, re.IGNORECASE))
        
        # Stored procedure complexity
        exception_handling = len(re.findall(r'\bexception\s+when\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic scripts
        if params > 0 or declares > 0 or if_stmt > 0:
            score = 2  # Medium: parameters, variables, basic control flow
        if (while_loop + for_loop) > 0 or javascript_udfs > 0 or task_schedule > 0 or exception_handling > 0:
            score = 3  # Complex: loops, JavaScript UDFs, scheduled tasks, exception handling
        if js_code > 0 or task_when > 0 or (javascript_udfs > 1 and exception_handling > 2):
            score = 4  # Very Complex: JavaScript code blocks, stream-triggered tasks, complex UDFs
        
        self.utility_complexity = score

        # --- 7. EXECUTION CONTROL ---
        # Enhanced: transactions, error handling, task execution
        begin_tran = len(re.findall(r'\bbegin\s+(transaction|work)\b', code_no_comments, re.IGNORECASE))
        commit = len(re.findall(r'\bcommit\s+(transaction|work)?\b', code_no_comments, re.IGNORECASE))
        rollback = len(re.findall(r'\brollback\s+(transaction|work)?\b', code_no_comments, re.IGNORECASE))
        
        # Session management
        session_vars = len(re.findall(r'\bset\s+\w+\s*=', code_no_comments, re.IGNORECASE))
        use_warehouse = len(re.findall(r'\buse\s+warehouse\s+\w+', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Task control
        task_suspend = len(re.findall(r'\balter\s+task\s+\w+\s+(suspend|resume)\b', code_no_comments, re.IGNORECASE))
        task_execute = len(re.findall(r'\bexecute\s+task\s+\w+', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Resource management
        warehouse_control = len(re.findall(r'\balter\s+warehouse\s+\w+\s+(suspend|resume|resize)\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no explicit control
        if session_vars > 0 or use_warehouse > 0:
            score = 2  # Medium: session management, warehouse usage
        if begin_tran > 0 or task_suspend > 0 or warehouse_control > 0:
            score = 3  # Complex: transactions, task control, warehouse management
        if rollback > 0 or task_execute > 0 or (begin_tran > 2 and warehouse_control > 0):
            score = 4  # Very Complex: error recovery, task execution, advanced resource control
        
        self.execution_control = score

        # --- 8. FILE I/O & EXTERNAL INTEGRATION ---
        # Enhanced: stages, pipes, external functions, data sharing
        # TIER 1: Stages and file operations
        stage_refs = len(re.findall(r'@\w+|@~', code_no_comments))
        put_files = len(re.findall(r'\bput\s+file://', code_no_comments, re.IGNORECASE))
        get_files = len(re.findall(r'\bget\s+@\w+', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Pipes and streaming
        auto_ingest = len(re.findall(r'\bauto_ingest\s*=\s*true\b', code_no_comments, re.IGNORECASE))
        copy_from_stage = len(re.findall(r'\bcopy\s+into\s+\w+\s+from\s+@', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Data sharing
        share_usage = len(re.findall(r'\bfrom\s+share\s+\w+', code_no_comments, re.IGNORECASE))
        data_exchange_usage = len(re.findall(r'\bfrom\s+data_exchange\s+\w+', code_no_comments, re.IGNORECASE))
        
        # TIER 3: External integrations
        external_function_calls = len(re.findall(r'\bselect\s+\w+\s*\(\s*.*\s*\)\s+as\s+\w+', code_no_comments, re.IGNORECASE))
        api_integration = len(re.findall(r'\bapi_integration\s*=\s*\w+', code_no_comments, re.IGNORECASE))
        
        # Snowpark integration
        snowpark_calls = len(re.findall(r'\bsystem\$\w+', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no external integration
        if stage_refs > 0 or put_files > 0 or get_files > 0:
            score = 2  # Medium: basic stage operations
        if copy_from_stage > 0 or auto_ingest > 0 or share_usage > 0 or snowpark_calls > 0:
            score = 3  # Complex: pipes, data sharing, Snowpark
        if api_integration > 0 or data_exchange_usage > 0 or (external_function_calls > 0 and stage_refs > 3):
            score = 4  # Very Complex: API integration, data exchanges, extensive external operations
        
        self.file_io_external_integration = score

        # --- 9. ODS OUTPUT DELIVERY ---
        # Enhanced: result sets, views, streams, materialized views
        select_stmt = len(re.findall(r'\bselect\b', code_no_comments, re.IGNORECASE))
        
        # Output mechanisms
        create_view = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?(view|secure\s+view)\b', code_no_comments, re.IGNORECASE))
        materialized_view = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?materialized\s+view\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Streams for CDC
        stream_creation = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?stream\s+\w+\s+on\s+table\b', code_no_comments, re.IGNORECASE))
        stream_usage = len(re.findall(r'\bfrom\s+\w+_stream\b|\bmetadata\$', code_no_comments, re.IGNORECASE))
        
        # Result caching
        result_cache = len(re.findall(r'\buse_cached_result\s*=\s*false\b', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Dynamic tables
        dynamic_table_creation = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?dynamic\s+table\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic SELECT
        if select_stmt > 1 or create_view > 0:
            score = 2  # Medium: multiple queries, views
        if materialized_view > 0 or stream_creation > 0 or result_cache > 0:
            score = 3  # Complex: materialized views, streams, result optimization
        if dynamic_table_creation > 0 or (stream_usage > 0 and materialized_view > 0):
            score = 4  # Very Complex: dynamic tables, complex stream usage with materialized views
        
        self.ods_output_delivery = score

        # --- 10. ERROR HANDLING & OPTIMIZATION ---
        # Enhanced: exception handling, query optimization, clustering
        try_catch = len(re.findall(r'\btry\s*{|\bexception\s+when\b', code_no_comments, re.IGNORECASE))
        
        # Performance optimization
        clustering_keys = len(re.findall(r'\bcluster\s+by\s*\(', code_no_comments, re.IGNORECASE))
        query_tags = len(re.findall(r'\bquery_tag\s*=', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Advanced optimization
        search_optimization = len(re.findall(r'\bsearch\s+optimization\s+on\b', code_no_comments, re.IGNORECASE))
        result_caching_control = len(re.findall(r'\buse_cached_result\b', code_no_comments, re.IGNORECASE))
        
        # Resource monitoring
        warehouse_size = len(re.findall(r'\bwarehouse_size\s*=', code_no_comments, re.IGNORECASE))
        auto_suspend = len(re.findall(r'\bauto_suspend\s*=', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Time travel and fail-safe
        time_travel = len(re.findall(r'\bat\s*\(\s*(timestamp|offset|statement|stream)\s*=>', code_no_comments, re.IGNORECASE))
        undrop = len(re.findall(r'\bundrop\s+(table|schema|database)\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no optimization
        if query_tags > 0 or time_travel > 0 or result_caching_control > 0:
            score = 2  # Medium: basic optimization, time travel
        if clustering_keys > 0 or search_optimization > 0 or try_catch > 0 or warehouse_size > 0:
            score = 3  # Complex: clustering, search optimization, exception handling, resource control
        if undrop > 0 or (clustering_keys > 0 and search_optimization > 0) or auto_suspend > 0:
            score = 4  # Very Complex: data recovery, comprehensive optimization, automated resource management
        
        self.error_handling_optimization = score

        # Calculate cyclomatic complexity
        self.cyclomatic = self._calculate_cyclomatic_complexity(code_no_comments)
        

    def _remove_comments(self, code: str) -> str:
        """Remove SQL comments from code for accurate analysis."""
        # Remove block comments /* ... */
        code_no_block = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        
        # Remove single-line comments --
        code_no_single = re.sub(r'--.*$', '', code_no_block, flags=re.MULTILINE)
        
        return code_no_single

    def _get_nesting_level(self, code: str) -> int:
        """
        Calculate the maximum nesting depth of control structures in Snowflake SQL code.
        """
        stack = []
        max_depth = 0

        # Regex patterns for opening and closing structures
        open_pattern = re.compile(r'\b(BEGIN|IF|WHILE|FOR|CASE|TRY)\b', re.IGNORECASE)
        close_pattern = re.compile(r'\b(END|END\s+IF|END\s+WHILE|END\s+FOR|END\s+CASE|EXCEPTION|CATCH)\b', re.IGNORECASE)

        for line in code.splitlines():
            # Ignore comments
            line = re.sub(r'--.*$', '', line).strip()
            if not line:
                continue

            # Check for openings
            if open_pattern.search(line):
                stack.append(1)
                max_depth = max(max_depth, len(stack))

            # Check for closings
            if close_pattern.search(line) and stack:
                stack.pop()

        return max_depth

    def _calculate_cyclomatic_complexity(self, code: str) -> int:
        """
        Calculate cyclomatic complexity for Snowflake SQL.
        
        Counts decision points: IF, CASE WHEN, WHILE, FOR, exception handlers
        Cyclomatic Complexity = decision points + 1
        """
        if_count = len(re.findall(r'\bif\s*\(', code, re.IGNORECASE))
        case_when = len(re.findall(r'\bwhen\b', code, re.IGNORECASE))
        while_count = len(re.findall(r'\bwhile\s*\(', code, re.IGNORECASE))
        for_count = len(re.findall(r'\bfor\s*\(', code, re.IGNORECASE))
        exception_when = len(re.findall(r'\bexception\s+when\b', code, re.IGNORECASE))
        
        decision_points = if_count + case_when + while_count + for_count + exception_when

        return max(1, decision_points + 1)
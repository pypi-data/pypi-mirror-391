# src/code_analyzer/analyzers/bigquery_analyzer.py
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


class BigQueryAnalyzer(AnalyzerBase):
    """
    BigQuery code complexity analyzer with enterprise metrics integration.
    
    Evaluates BigQuery scripts across 10 dimensions, each scored 1-4:
    - 1: Simple
    - 2: Medium
    - 3: Complex
    - 4: Very Complex
    
    Uses hybrid approach:
    - Config weights override registry defaults
    - Enterprise validation via metrics module
    - Standardized 0-100 scoring system
    """
    language = "bigquery"
    
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
        """Analyze BigQuery source code and return complexity metrics."""
        include_cyclomatic = self.config.get("include_cyclomatic", False)
        
        # If code is None or empty, try to read from file path
        if not code and path and path != "<string>":
            file_content = read_file_if_exists(path)
            if file_content:
                code = file_content
        
        # Run complexity analysis
        analyzer = BigQueryComplexity()
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
    
class BigQueryComplexity:
    """
    Enterprise-grade BigQuery complexity analyzer with comprehensive pattern detection.
    Each metric is scored 1 (Simple) to 4 (Very Complex) based on BigQuery-specific patterns.
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
        Analyze BigQuery source code and return complexity metrics.
        """
        if not code or not code.strip():
            return
        
        # Remove comments for accurate pattern matching
        code_no_comments = self._remove_comments(code)
        
        # Calculate nesting depth
        nesting_level = self._get_nesting_level(code_no_comments)

        # --- 1. SCRIPT SIZE & STRUCTURE ---
        # Enhanced: lines, procedures, functions, modules, table functions
        lines = len([line for line in code.split('\n') if line.strip()])
        
        # BigQuery objects
        procedures = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?procedure\b', code_no_comments, re.IGNORECASE))
        functions = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?function\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Table functions
        table_functions = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?table\s+function\b', code_no_comments, re.IGNORECASE))
        
        # TIER 3: JavaScript UDFs
        js_udfs = len(re.findall(r'\blanguage\s+js\b', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Remote functions
        remote_functions = len(re.findall(r'\bremote_function_endpoint\b', code_no_comments, re.IGNORECASE))
        
        # Modules and imports
        modules = len(re.findall(r'\bcreate\s+module\b', code_no_comments, re.IGNORECASE))
        imports = len(re.findall(r'\bimport\s+module\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: small script
        if lines > 100 or procedures > 0 or functions > 0 or nesting_level > 1:
            score = 2  # Medium: moderate size, procedures, or basic nesting
        if lines > 500 or (procedures + functions) > 3 or table_functions > 0 or modules > 0 or nesting_level > 3:
            score = 3  # Complex: large, multiple objects, table functions, modules, or deep nesting
        if lines > 2000 or (procedures + functions + modules) > 8 or js_udfs > 0 or remote_functions > 0 or nesting_level > 5:
            score = 4  # Very Complex: very large, many objects, JavaScript UDFs, remote functions, or very deep nesting
        
        self.script_size_structure = score

        # --- 2. DEPENDENCY FOOTPRINT ---
        # Enhanced: datasets, tables, views, external sources, federated queries
        datasets = len(re.findall(r'\b\w+\.\w+\.\w+\b', code_no_comments))  # project.dataset.table
        tables = len(re.findall(r'\bfrom\s+[\w\.\`]+|\bjoin\s+[\w\.\`]+|\binto\s+[\w\.\`]+', code_no_comments, re.IGNORECASE))
        
        # Views and materialized views
        views = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?view\b', code_no_comments, re.IGNORECASE))
        materialized_views = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?materialized\s+view\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: External tables and data sources
        external_tables = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?external\s+table\b', code_no_comments, re.IGNORECASE))
        cloud_storage = len(re.findall(r'\bgs://|\buris\s*=', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Federated queries
        federated_queries = len(re.findall(r'\bexternal_query\b', code_no_comments, re.IGNORECASE))
        
        # Cross-project queries
        cross_project = len(re.findall(r'\b\w+-\w+\.\w+\.\w+\b', code_no_comments))  # project-name.dataset.table
        
        # Temporary tables and variables
        temp_tables = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?temp\s+table\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: few dependencies
        if tables > 3 or datasets > 1 or temp_tables > 0:
            score = 2  # Medium: multiple tables or datasets
        if tables > 10 or views > 0 or external_tables > 0 or cross_project > 0 or cloud_storage > 0:
            score = 3  # Complex: many tables, views, external sources, cross-project
        if tables > 20 or materialized_views > 0 or federated_queries > 0 or (external_tables > 1 and cloud_storage > 1):
            score = 4  # Very Complex: many dependencies, materialized views, federated queries
        
        self.dependency_footprint = score

        # --- 3. ANALYTICS DEPTH ---
        # Enhanced: aggregations, window functions, analytical operations, ML functions, STRUCT/ARRAY
        basic_agg = len(re.findall(r'\b(count|sum|avg|min|max|group\s+by)\b', code_no_comments, re.IGNORECASE))
        
        # Advanced aggregations
        advanced_agg = len(re.findall(r'\b(stddev|variance|approx_count_distinct|approx_quantiles|array_agg|string_agg)\b', code_no_comments, re.IGNORECASE))
        
        # Window functions
        window_funcs = len(re.findall(r'\b(row_number|rank|dense_rank|lead|lag|first_value|last_value|nth_value|over\s*\()\b', code_no_comments, re.IGNORECASE))
        
        # CTEs and subqueries
        cte = len(re.findall(r'\bwith\s+\w+\s+as\s*\(', code_no_comments, re.IGNORECASE))
        subqueries = len(re.findall(r'\(\s*select\s+', code_no_comments, re.IGNORECASE))
        
        # TIER 1: STRUCT and ARRAY operations
        struct_ops = len(re.findall(r'\bstruct\s*\(|\bunflatten|\bflatten', code_no_comments, re.IGNORECASE))
        array_ops = len(re.findall(r'\barray\s*\[|\barray_length|\barray_concat|\bunpivot', code_no_comments, re.IGNORECASE))
        
        # TIER 2: ML functions
        ml_functions = len(re.findall(r'\bml\.\w+|\bcreate\s+(or\s+replace\s+)?model\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Statistical and mathematical functions
        stat_funcs = len(re.findall(r'\b(corr|covar_pop|covar_samp|percentile_cont|percentile_disc)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Geospatial functions
        geo_funcs = len(re.findall(r'\bst_\w+|\bgeography\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic queries
        if basic_agg > 0 or cte > 0 or struct_ops > 0:
            score = 2  # Medium: aggregations, CTEs, STRUCT operations
        if window_funcs > 0 or advanced_agg > 0 or array_ops > 2 or ml_functions > 0 or geo_funcs > 0:
            score = 3  # Complex: window functions, ML, geospatial, complex ARRAY operations
        if window_funcs > 3 or ml_functions > 2 or (cte > 2 and subqueries > 3) or stat_funcs > 2 or geo_funcs > 3:
            score = 4  # Very Complex: heavy analytics, advanced ML, complex statistical operations
        
        self.analytics_depth = score

        # --- 4. SQL REPORTING LOGIC ---
        # Enhanced: query complexity, joins, unions, exports
        joins = len(re.findall(r'\b(inner\s+join|left\s+join|right\s+join|full\s+join|cross\s+join|join)\b', code_no_comments, re.IGNORECASE))
        unions = len(re.findall(r'\bunion\s+(all\s+|distinct\s+)?', code_no_comments, re.IGNORECASE))
        
        # Complex WHERE clauses
        complex_where = len(re.findall(r'\bwhere\s+.*\b(and|or)\b.*\b(and|or)\b', code_no_comments, re.IGNORECASE))
        
        # CASE statements
        case_stmt = len(re.findall(r'\bcase\s+when\b', code_no_comments, re.IGNORECASE))
        
        # QUALIFY clause (BigQuery specific)
        qualify = len(re.findall(r'\bqualify\b', code_no_comments, re.IGNORECASE))
        
        # Pivot operations
        pivot_ops = len(re.findall(r'\bpivot\s*\(|\bunpivot\s*\(', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Search and full-text
        search_funcs = len(re.findall(r'\bsearch\s*\(|\bvector_search\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic SELECT
        if joins >= 1 or case_stmt > 0 or unions > 0:
            score = 2  # Medium: joins, CASE statements
        if joins > 3 or unions > 1 or complex_where > 0 or qualify > 0 or pivot_ops > 0:
            score = 3  # Complex: multiple joins, complex WHERE, QUALIFY, PIVOT
        if joins > 6 or unions > 3 or qualify > 2 or pivot_ops > 2 or search_funcs > 0:
            score = 4  # Very Complex: many joins/unions, advanced QUALIFY usage, search functions
        
        self.sql_reporting_logic = score

        # --- 5. TRANSFORMATION LOGIC ---
        # Enhanced: data manipulation, DML operations, data transformations
        updates = len(re.findall(r'\bupdate\s+\w+', code_no_comments, re.IGNORECASE))
        inserts = len(re.findall(r'\binsert\s+into\b', code_no_comments, re.IGNORECASE))
        deletes = len(re.findall(r'\bdelete\s+from\b', code_no_comments, re.IGNORECASE))
        
        # MERGE operations
        merge = len(re.findall(r'\bmerge\s+', code_no_comments, re.IGNORECASE))
        
        # Data type operations and transformations
        cast_ops = len(re.findall(r'\b(cast|safe_cast|extract|parse_date|parse_timestamp|format_date|format_timestamp)\b', code_no_comments, re.IGNORECASE))
        
        # String operations
        string_ops = len(re.findall(r'\b(substr|concat|split|regexp_extract|regexp_replace|lower|upper|trim|ltrim|rtrim)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: JSON operations
        json_ops = len(re.findall(r'\bjson_extract|\bjson_query|\bto_json_string|\bparse_json', code_no_comments, re.IGNORECASE))
        
        # Data generation and sampling
        sample_ops = len(re.findall(r'\btablesample\b|\bgenerate_array|\bgenerate_date_array|\bgenerate_timestamp_array', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic SELECT
        if updates > 0 or inserts > 0 or cast_ops > 2:
            score = 2  # Medium: basic DML, type conversions
        if merge > 0 or (updates > 2 and inserts > 2) or string_ops > 3 or json_ops > 0:
            score = 3  # Complex: MERGE, multiple DML, string operations, JSON
        if merge > 1 or (updates > 5 and deletes > 2) or json_ops > 3 or sample_ops > 0:
            score = 4  # Very Complex: complex MERGE, heavy DML, advanced JSON, sampling
        
        self.transformation_logic = score

        # --- 6. UTILITY COMPLEXITY ---
        # Enhanced: procedures, functions, UDFs, parameters, control flow
        # Parameters and variables
        params = len(re.findall(r'@\w+|declare\s+\w+', code_no_comments, re.IGNORECASE))
        
        # Control flow (in procedures)
        if_stmt = len(re.findall(r'\bif\b', code_no_comments, re.IGNORECASE))
        while_loop = len(re.findall(r'\bwhile\b', code_no_comments, re.IGNORECASE))
        loop_stmt = len(re.findall(r'\bloop\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: SQL UDFs and table functions (already counted above)
        sql_udfs = functions + table_functions
        
        # TIER 3: JavaScript UDFs (already counted above)
        # TIER 3: Remote functions (already counted above)
        
        # Exception handling
        exception_handling = len(re.findall(r'\bbegin\s+.*\bexception\s+when\b', code_no_comments, re.IGNORECASE | re.DOTALL))
        
        # Nested function calls
        nested_calls = len(re.findall(r'\bcall\s+\w+', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no procedures
        if params > 0 or if_stmt > 1 or sql_udfs > 0:
            score = 2  # Medium: parameters, basic control flow, SQL UDFs
        if (params > 5 or while_loop > 0 or loop_stmt > 0 or nested_calls > 0 or 
            table_functions > 0):
            score = 3  # Complex: many params, loops, nested calls, table functions
        if (js_udfs > 0 or remote_functions > 0 or exception_handling > 0 or 
            (params > 10 and while_loop > 2)):
            score = 4  # Very Complex: JavaScript/remote UDFs, exception handling
        
        self.utility_complexity = score

        # --- 7. EXECUTION CONTROL ---
        # Enhanced: transactions, error handling, scheduling, concurrency
        # BigQuery has limited transaction support
        begin_trans = len(re.findall(r'\bbegin\s+transaction\b', code_no_comments, re.IGNORECASE))
        commit = len(re.findall(r'\bcommit\s+transaction\b', code_no_comments, re.IGNORECASE))
        rollback = len(re.findall(r'\brollback\s+transaction\b', code_no_comments, re.IGNORECASE))
        
        # Error handling
        assert_stmt = len(re.findall(r'\bassert\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Scheduled queries and jobs
        schedule = len(re.findall(r'\bschedule\s+options\b', code_no_comments, re.IGNORECASE))
        
        # Batch operations
        batch_ops = len(re.findall(r'\bbatch\b|\bbulk\b', code_no_comments, re.IGNORECASE))
        
        # DML and DDL statements that affect execution
        ddl_statements = len(re.findall(r'\b(create|alter|drop)\s+', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no explicit control
        if assert_stmt > 0 or ddl_statements > 0:
            score = 2  # Medium: basic assertions, DDL
        if begin_trans > 0 or exception_handling > 0 or batch_ops > 0:
            score = 3  # Complex: transactions, exception handling, batch operations
        if (begin_trans > 0 and rollback > 0) or schedule > 0 or (ddl_statements > 5 and batch_ops > 1):
            score = 4  # Very Complex: transaction control, scheduling, complex batch operations
        
        self.execution_control = score

        # --- 8. FILE I/O & EXTERNAL INTEGRATION ---
        # Enhanced: external tables, Cloud Storage, federated queries, exports
        # External data sources (already counted above)
        # Cloud Storage integration (already counted above)
        # Federated queries (already counted above)
        
        # TIER 2: Data exports
        export_data = len(re.findall(r'\bexport\s+data\b', code_no_comments, re.IGNORECASE))
        
        # TIER 3: BigQuery ML model exports
        model_export = len(re.findall(r'\bexport\s+model\b', code_no_comments, re.IGNORECASE))
        
        # TIER 3: External connections
        external_conn = len(re.findall(r'\bconnection\b.*\bexternal\b', code_no_comments, re.IGNORECASE))
        
        # Data loading operations
        load_data = len(re.findall(r'\bload\s+data\b|\bcopy\s+into\b', code_no_comments, re.IGNORECASE))
        
        # Cloud Functions integration
        cloud_functions = len(re.findall(r'\bcloud_function\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no external integration
        if external_tables > 0 or cloud_storage > 0 or load_data > 0:
            score = 2  # Medium: basic external sources, data loading
        if export_data > 0 or federated_queries > 0 or (external_tables > 1 and cloud_storage > 1):
            score = 3  # Complex: data exports, federated queries, multiple external sources
        if (model_export > 0 or external_conn > 0 or cloud_functions > 0 or 
            (federated_queries > 1 and export_data > 1)):
            score = 4  # Very Complex: model exports, external connections, cloud functions
        
        self.file_io_external_integration = score

        # --- 9. ODS OUTPUT DELIVERY ---
        # Enhanced: result sets, exports, materialized views, streaming
        select_stmt = len(re.findall(r'\bselect\b', code_no_comments, re.IGNORECASE))
        
        # Output operations
        create_table_as = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?table\s+.*\bas\s+select\b', code_no_comments, re.IGNORECASE))
        
        # Materialized views (already counted above)
        
        # TIER 2: Scheduled deliveries and exports (already counted above)
        
        # Result table creation
        temp_result_tables = temp_tables
        
        # TIER 3: Streaming and real-time outputs
        streaming = len(re.findall(r'\bstreaming\b|\bpubsub\b', code_no_comments, re.IGNORECASE))
        
        # Multiple result sets
        result_complexity = 0
        if select_stmt > 3:
            result_complexity = 1
        if create_table_as > 0 or export_data > 0:
            result_complexity = 2
        if materialized_views > 0 or streaming > 0:
            result_complexity = 3
        
        score = 1  # Simple: single SELECT
        if select_stmt > 1 or create_table_as > 0:
            score = 2  # Medium: multiple SELECTs, table creation
        if select_stmt > 3 or temp_result_tables > 2 or export_data > 0 or materialized_views > 0:
            score = 3  # Complex: many result sets, exports, materialized views
        if select_stmt > 6 or streaming > 0 or (materialized_views > 1 and export_data > 1):
            score = 4  # Very Complex: many result sets, streaming, complex output delivery
        
        self.ods_output_delivery = score

        # --- 10. ERROR HANDLING & OPTIMIZATION ---
        # Enhanced: error handling, performance optimization, query hints
        # Error handling (already counted above)
        
        # Query optimization and performance hints
        hints = len(re.findall(r'\bhint\s*\(|\bpartition\s+by\b|\bcluster\s+by\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Performance features
        partitioning = len(re.findall(r'\bpartition\s+by\b', code_no_comments, re.IGNORECASE))
        clustering = len(re.findall(r'\bcluster\s+by\b', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Advanced optimization
        search_indexes = len(re.findall(r'\bcreate\s+search\s+index\b', code_no_comments, re.IGNORECASE))
        
        # Query complexity indicators
        explain_stmt = len(re.findall(r'\bexplain\b', code_no_comments, re.IGNORECASE))
        
        # Performance monitoring
        information_schema = len(re.findall(r'\binformation_schema\b', code_no_comments, re.IGNORECASE))
        
        # Resource optimization
        labels = len(re.findall(r'\blabels\s*=\s*\[', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no optimization
        if assert_stmt > 0 or hints > 0 or partitioning > 0:
            score = 2  # Medium: basic assertions, hints, partitioning
        if clustering > 0 or exception_handling > 0 or information_schema > 0:
            score = 3  # Complex: clustering, exception handling, performance monitoring
        if (search_indexes > 0 or (partitioning > 1 and clustering > 1) or 
            (exception_handling > 1 and information_schema > 1)):
            score = 4  # Very Complex: search indexes, comprehensive optimization
        
        self.error_handling_optimization = score

        # Calculate cyclomatic complexity
        self.cyclomatic = self._calculate_cyclomatic_complexity(code_no_comments)

    def _remove_comments(self, code: str) -> str:
        """Remove SQL comments from code for accurate analysis."""
        # Remove block comments /* ... */
        code_no_block = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        
        # Remove single-line comments --
        code_no_single = re.sub(r'--.*$', '', code_no_block, flags=re.MULTILINE)
        
        # Remove hash comments #
        code_no_hash = re.sub(r'#.*$', '', code_no_single, flags=re.MULTILINE)
        
        return code_no_hash

    def _get_nesting_level(self, code: str) -> int:
        """
        Calculate the maximum nesting depth of control structures in BigQuery SQL.
        """
        stack = []
        max_depth = 0

        # Regex patterns for opening and closing structures
        open_pattern = re.compile(r'\b(BEGIN|IF|WHILE|LOOP|CASE|WITH)\b', re.IGNORECASE)
        close_pattern = re.compile(r'\b(END(\s+IF|\s+WHILE|\s+LOOP|\s+CASE)?)\b', re.IGNORECASE)

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
        Calculate cyclomatic complexity for BigQuery SQL.
        
        Counts decision points: IF, CASE WHEN, WHILE, LOOP, AND, OR
        Cyclomatic Complexity = decision points + 1
        """
        if_count = len(re.findall(r'\bif\b', code, re.IGNORECASE))
        case_when = len(re.findall(r'\bwhen\b', code, re.IGNORECASE))
        loop_count = len(re.findall(r'\b(while|loop)\b', code, re.IGNORECASE))
        logical_ops = len(re.findall(r'\b(and|or)\b', code, re.IGNORECASE))
        
        decision_points = if_count + case_when + loop_count + logical_ops
        
        return max(1, decision_points + 1)
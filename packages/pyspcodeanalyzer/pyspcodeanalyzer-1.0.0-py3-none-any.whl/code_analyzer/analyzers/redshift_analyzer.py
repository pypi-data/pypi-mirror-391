# src/code_analyzer/analyzers/redshift_analyzer.py
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


class RedshiftAnalyzer(AnalyzerBase):
    """
    Redshift code complexity analyzer with enterprise metrics integration.
    
    Evaluates Redshift scripts across 10 dimensions, each scored 1-4:
    - 1: Simple
    - 2: Medium
    - 3: Complex
    - 4: Very Complex
    
    Uses hybrid approach:
    - Config weights override registry defaults
    - Enterprise validation via metrics module
    - Standardized 0-100 scoring system
    """
    language = "redshift"
    
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
        """Analyze Redshift source code and return complexity metrics."""
        include_cyclomatic = self.config.get("include_cyclomatic", False)
        
        # If code is None or empty, try to read from file path
        if not code and path and path != "<string>":
            file_content = read_file_if_exists(path)
            if file_content:
                code = file_content
        
        # Run complexity analysis
        analyzer = RedshiftComplexity()
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
    

class RedshiftComplexity:
    """
    Enterprise-grade Redshift complexity analyzer with comprehensive pattern detection.
    Each metric is scored 1 (Simple) to 4 (Very Complex) based on Redshift-specific patterns.
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
        Analyze Redshift source code and return complexity metrics.
        """
        if not code or not code.strip():
            return

        # Remove comments for accurate pattern matching
        code_no_comments = self._remove_comments(code)
        
        # Calculate nesting depth
        nesting_level = self._get_nesting_level(code_no_comments)
        
        # --- 1. SCRIPT SIZE & STRUCTURE ---
        # Enhanced: lines, procedures, functions, external schemas, data shares
        lines = len([line for line in code.split('\n') if line.strip()])
        
        # Redshift objects
        procedures = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?procedure\b', code_no_comments, re.IGNORECASE))
        functions = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?function\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: External schemas (Spectrum, federated)
        external_schemas = len(re.findall(r'\bcreate\s+external\s+schema\b', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Data sharing
        data_shares = len(re.findall(r'\bcreate\s+datashare\b', code_no_comments, re.IGNORECASE))
        share_usage = len(re.findall(r'\bcreate\s+database\s+.*\bfrom\s+datashare\b', code_no_comments, re.IGNORECASE))
        
        # Batches and scripts
        batches = len(re.findall(r';\s*$', code_no_comments, re.MULTILINE))
        
        score = 1  # Simple: small script
        if lines > 100 or procedures > 0 or functions > 0 or nesting_level > 1:
            score = 2  # Medium: moderate size, procedures, or basic nesting
        if lines > 500 or (procedures + functions) > 3 or external_schemas > 0 or nesting_level > 3:
            score = 3  # Complex: large, multiple objects, external schemas, or deep nesting
        if lines > 2000 or (procedures + functions) > 8 or data_shares > 0 or share_usage > 0 or nesting_level > 5:
            score = 4  # Very Complex: very large, many objects, data sharing, or very deep nesting
        
        self.script_size_structure = score

        # --- 2. DEPENDENCY FOOTPRINT ---
        # Enhanced: tables, views, external tables, spectrum, cross-database queries
        tables = len(re.findall(r'\bfrom\s+(\w+\.)?(\w+)', code_no_comments, re.IGNORECASE))
        joins = len(re.findall(r'\b(inner\s+join|left\s+join|right\s+join|full\s+join|cross\s+join|join)\b', code_no_comments, re.IGNORECASE))
        
        # Views and materialized views
        views = len(re.findall(r'\bcreate\s+view\b', code_no_comments, re.IGNORECASE))
        materialized_views = len(re.findall(r'\bcreate\s+materialized\s+view\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: External tables (Spectrum)
        external_tables = len(re.findall(r'\bcreate\s+external\s+table\b', code_no_comments, re.IGNORECASE))
        spectrum_refs = len(re.findall(r'\bspectrum\.|external_schema\.', code_no_comments, re.IGNORECASE))
        
        # Cross-database and cross-schema queries
        cross_schema = len(re.findall(r'\w+\.\w+\.\w+', code_no_comments))
        
        # TIER 3: Federated queries
        federated_queries = len(re.findall(r'\bfederated\s+query\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: few table references
        if tables > 3 or joins > 1 or views > 0:
            score = 2  # Medium: multiple tables, joins, views
        if tables > 10 or joins > 5 or external_tables > 0 or spectrum_refs > 0 or materialized_views > 0:
            score = 3  # Complex: many tables, external tables, Spectrum, materialized views
        if tables > 20 or joins > 10 or cross_schema > 5 or federated_queries > 0 or (external_tables > 2 and spectrum_refs > 5):
            score = 4  # Very Complex: extensive dependencies, federated queries, heavy Spectrum usage
        
        self.dependency_footprint = score

        # --- 3. ANALYTICS DEPTH ---
        # Enhanced: aggregations, window functions, analytical queries, ML functions
        basic_agg = len(re.findall(r'\b(count|sum|avg|min|max|group\s+by)\b', code_no_comments, re.IGNORECASE))
        
        # Advanced aggregations
        advanced_agg = len(re.findall(r'\b(stddev|variance|median|percentile_cont|percentile_disc|listagg)\b', code_no_comments, re.IGNORECASE))
        
        # Window functions
        window_funcs = len(re.findall(r'\b(row_number|rank|dense_rank|lead|lag|first_value|last_value|over\s*\()\b', code_no_comments, re.IGNORECASE))
        
        # Analytical functions
        analytical_funcs = len(re.findall(r'\b(ntile|cume_dist|percent_rank|ratio_to_report)\b', code_no_comments, re.IGNORECASE))
        
        # CTEs and subqueries
        cte = len(re.findall(r'\bwith\s+\w+\s+as\s*\(', code_no_comments, re.IGNORECASE))
        subqueries = len(re.findall(r'\(\s*select\s+', code_no_comments, re.IGNORECASE))
        
        # TIER 3: ML functions
        ml_functions = len(re.findall(r'\b(create\s+model|predict|explain_model)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Spatial functions
        spatial_functions = len(re.findall(r'\b(st_|geometry|geography)\w*\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic queries
        if basic_agg > 0 or cte > 0:
            score = 2  # Medium: GROUP BY, COUNT, SUM, basic CTEs
        if window_funcs > 0 or advanced_agg > 0 or analytical_funcs > 0 or subqueries > 3:
            score = 3  # Complex: window functions, advanced analytics, nested subqueries
        if window_funcs > 5 or analytical_funcs > 3 or ml_functions > 0 or spatial_functions > 0 or (cte > 3 and subqueries > 5):
            score = 4  # Very Complex: heavy analytics, ML, spatial functions
        
        self.analytics_depth = score

        # --- 4. SQL & REPORTING LOGIC ---
        # Enhanced: query complexity, result sets, query hints
        select_stmt = len(re.findall(r'\bselect\b', code_no_comments, re.IGNORECASE))
        unions = len(re.findall(r'\bunion\s+(all\s+)?', code_no_comments, re.IGNORECASE))
        
        # Complex WHERE clauses
        complex_where = len(re.findall(r'\bwhere\s+.*\b(and|or)\b.*\b(and|or)\b', code_no_comments, re.IGNORECASE))
        
        # CASE statements
        case_stmt = len(re.findall(r'\bcase\s+when\b', code_no_comments, re.IGNORECASE))
        
        # Redshift-specific query hints
        query_hints = len(re.findall(r'\b(distkey|sortkey|diststyle|compound|interleaved)\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic SELECT
        if select_stmt > 1 or case_stmt > 0 or unions > 0:
            score = 2  # Medium: multiple SELECTs, CASE statements
        if select_stmt > 5 or unions > 2 or complex_where > 0 or query_hints > 0:
            score = 3  # Complex: many queries, unions, query hints
        if select_stmt > 10 or unions > 5 or complex_where > 3 or query_hints > 5:
            score = 4  # Very Complex: extensive querying, heavy optimization
        
        self.sql_reporting_logic = score

        # --- 5. TRANSFORMATION LOGIC ---
        # Enhanced: COPY/UNLOAD, data transformations, ELT patterns
        updates = len(re.findall(r'\bupdate\s+\w+', code_no_comments, re.IGNORECASE))
        inserts = len(re.findall(r'\binsert\s+into\b', code_no_comments, re.IGNORECASE))
        deletes = len(re.findall(r'\bdelete\s+from\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: COPY and UNLOAD operations
        copy_commands = len(re.findall(r'\bcopy\s+\w+\s+from\b', code_no_comments, re.IGNORECASE))
        unload_commands = len(re.findall(r'\bunload\s*\(', code_no_comments, re.IGNORECASE))
        
        # Data type conversions
        conversions = len(re.findall(r'\b(cast|convert|::|\bto_\w+)\b', code_no_comments, re.IGNORECASE))
        
        # String operations
        string_ops = len(re.findall(r'\b(substring|charindex|position|replace|ltrim|rtrim|upper|lower|concat|split_part)\b', code_no_comments, re.IGNORECASE))
        
        # Date/time functions
        date_funcs = len(re.findall(r'\b(current_date|getdate|dateadd|datediff|extract|date_part|date_trunc)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Advanced transformations
        json_ops = len(re.findall(r'\b(json_extract|json_parse|json_serialize)\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic operations
        if updates > 0 or inserts > 0 or copy_commands > 0 or conversions > 2:
            score = 2  # Medium: basic DML, COPY operations, conversions
        if copy_commands > 2 or unload_commands > 0 or string_ops > 5 or date_funcs > 3 or json_ops > 0:
            score = 3  # Complex: multiple COPY/UNLOAD, extensive transformations, JSON
        if copy_commands > 5 or unload_commands > 2 or (updates > 5 and deletes > 2) or json_ops > 3:
            score = 4  # Very Complex: heavy ETL operations, complex transformations
        
        self.transformation_logic = score

        # --- 6. UTILITY COMPLEXITY ---
        # Enhanced: stored procedures, UDFs, parameters, control flow
        params = len(re.findall(r'\$\d+|@\w+', code_no_comments))
        
        # Variables and declarations
        declares = len(re.findall(r'\bdeclare\s+\w+', code_no_comments, re.IGNORECASE))
        
        # Control flow
        if_stmt = len(re.findall(r'\bif\b', code_no_comments, re.IGNORECASE))
        while_loop = len(re.findall(r'\bwhile\b', code_no_comments, re.IGNORECASE))
        for_loop = len(re.findall(r'\bfor\s+\w+\s+in\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: UDFs (Python, SQL)
        python_udfs = len(re.findall(r'\bcreate\s+function\s+.*\blanguage\s+plpythonu\b', code_no_comments, re.IGNORECASE))
        sql_udfs = len(re.findall(r'\bcreate\s+function\s+.*\breturns\b', code_no_comments, re.IGNORECASE))
        
        # Dynamic SQL
        dynamic_sql = len(re.findall(r'\bexecute\s+.*\busing\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no procedures or simple queries
        if params > 0 or declares > 2 or if_stmt > 1 or sql_udfs > 0:
            score = 2  # Medium: parameters, basic control flow, SQL UDFs
        if params > 5 or while_loop > 0 or for_loop > 0 or python_udfs > 0 or procedures > 0:
            score = 3  # Complex: many params, loops, Python UDFs, stored procedures
        if params > 10 or dynamic_sql > 0 or python_udfs > 2 or (procedures > 1 and for_loop > 2):
            score = 4  # Very Complex: dynamic SQL, multiple Python UDFs, complex procedures
        
        self.utility_complexity = score

        # --- 7. EXECUTION CONTROL ---
        # Enhanced: transactions, workload management, query priorities
        begin_tran = len(re.findall(r'\bbegin\s*;?\s*$', code_no_comments, re.MULTILINE | re.IGNORECASE))
        commit = len(re.findall(r'\bcommit\s*;?\s*$', code_no_comments, re.MULTILINE | re.IGNORECASE))
        rollback = len(re.findall(r'\brollback\s*;?\s*$', code_no_comments, re.MULTILINE | re.IGNORECASE))
        
        # TIER 2: Workload Management
        wlm_settings = len(re.findall(r'\bset\s+(query_group|query_slot_count)\b', code_no_comments, re.IGNORECASE))
        
        # Query hints and optimization
        query_labels = len(re.findall(r'/\*\s*label\s*:', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Concurrency scaling
        concurrency_hints = len(re.findall(r'\bconcurrency\s+scaling\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no explicit transactions
        if begin_tran > 0 or commit > 0:
            score = 2  # Medium: basic transactions
        if rollback > 0 or wlm_settings > 0 or query_labels > 0:
            score = 3  # Complex: rollbacks, workload management, query labeling
        if wlm_settings > 3 or concurrency_hints > 0 or (begin_tran > 5 and rollback > 2):
            score = 4  # Very Complex: advanced WLM, concurrency scaling, complex transaction management
        
        self.execution_control = score

        # --- 8. FILE I/O & EXTERNAL INTEGRATION ---
        # Enhanced: S3 integration, Spectrum, federated queries, data sharing
        # TIER 1: S3 integration
        s3_operations = len(re.findall(r's3://|from\s+s3', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Spectrum operations
        spectrum_queries = spectrum_refs + external_tables
        
        # System functions
        system_funcs = len(re.findall(r'\bpg_\w+|stl_\w+|svl_\w+|stv_\w+', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Federated queries
        federated_ops = federated_queries
        
        # TIER 3: Data sharing
        data_share_ops = data_shares + share_usage
        
        # External functions
        external_funcs = len(re.findall(r'\bcreate\s+external\s+function\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no external integration
        if s3_operations > 0 or system_funcs > 0:
            score = 2  # Medium: basic S3 operations, system functions
        if spectrum_queries > 0 or s3_operations > 5 or external_funcs > 0:
            score = 3  # Complex: Spectrum queries, extensive S3 usage, external functions
        if federated_ops > 0 or data_share_ops > 0 or spectrum_queries > 5 or s3_operations > 10:
            score = 4  # Very Complex: federated queries, data sharing, heavy external integration
        
        self.file_io_external_integration = score

        # --- 9. ODS OUTPUT DELIVERY ---
        # Enhanced: result sets, UNLOAD operations, materialized views
        output_operations = unload_commands
        
        # Result set operations
        result_sets = select_stmt
        
        # Temporary tables and CTEs for staging
        temp_tables = len(re.findall(r'#\w+|temp\s+table', code_no_comments, re.IGNORECASE))
        staging_operations = cte + temp_tables
        
        # TIER 2: Materialized views
        mv_operations = materialized_views
        mv_refresh = len(re.findall(r'\brefresh\s+materialized\s+view\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic results
        if result_sets > 1 or staging_operations > 0:
            score = 2  # Medium: multiple result sets, staging operations
        if result_sets > 5 or output_operations > 0 or mv_operations > 0:
            score = 3  # Complex: many result sets, UNLOAD operations, materialized views
        if result_sets > 10 or output_operations > 3 or mv_refresh > 0 or (staging_operations > 5 and output_operations > 1):
            score = 4  # Very Complex: extensive output operations, MV management, complex staging
        
        self.ods_output_delivery = score

        # --- 10. ERROR HANDLING & OPTIMIZATION ---
        # Enhanced: error handling, performance optimization, compression, encoding
        try_catch = len(re.findall(r'\bbegin\s+.*\bexception\b', code_no_comments, re.IGNORECASE | re.DOTALL))
        
        # Performance optimization
        analyze_stats = len(re.findall(r'\banalyze\b', code_no_comments, re.IGNORECASE))
        vacuum_ops = len(re.findall(r'\bvacuum\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Compression and encoding
        compression = len(re.findall(r'\b(encode|compression|lzo|gzip|bzip2|zstd)\b', code_no_comments, re.IGNORECASE))
        
        # Distribution and sort keys
        dist_sort_keys = len(re.findall(r'\b(distkey|sortkey|diststyle)\b', code_no_comments, re.IGNORECASE))
        
        # Query monitoring
        query_monitoring = len(re.findall(r'\bsvl_query_summary|stl_query|pg_stat\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no optimization
        if analyze_stats > 0 or vacuum_ops > 0 or dist_sort_keys > 0:
            score = 2  # Medium: basic optimization, distribution/sort keys
        if compression > 0 or query_monitoring > 0 or dist_sort_keys > 5:
            score = 3  # Complex: compression, query monitoring, advanced optimization
        if try_catch > 0 or compression > 5 or query_monitoring > 3 or (analyze_stats > 5 and vacuum_ops > 3):
            score = 4  # Very Complex: error handling, extensive optimization, comprehensive monitoring
        
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
        Calculate the maximum nesting depth of control structures in Redshift SQL code.
        """
        stack = []
        max_depth = 0

        # Regex patterns for opening and closing structures
        open_pattern = re.compile(r'\b(BEGIN|IF|WHILE|FOR|CASE|LOOP)\b', re.IGNORECASE)
        close_pattern = re.compile(r'\b(END(\s+IF|\s+WHILE|\s+FOR|\s+CASE|\s+LOOP)?)\b', re.IGNORECASE)

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
        Calculate cyclomatic complexity for Redshift SQL.
        
        Counts decision points: IF, ELSIF, WHILE, FOR, CASE WHEN, EXCEPTION handlers
        Cyclomatic Complexity = decision points + 1
        """
        if_count = len(re.findall(r'\bif\b', code, re.IGNORECASE))
        elsif_count = len(re.findall(r'\belsif\b', code, re.IGNORECASE))
        loop_count = len(re.findall(r'\b(while|for)\b', code, re.IGNORECASE))
        case_when = len(re.findall(r'\bwhen\b', code, re.IGNORECASE))
        exception_when = len(re.findall(r'\bexception\s+when\b', code, re.IGNORECASE))
        decision_points = if_count + elsif_count + loop_count + case_when + exception_when

        return max(1, decision_points + 1)
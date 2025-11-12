# src/code_analyzer/analyzers/mysql_analyzer.py
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


class MySQLAnalyzer(AnalyzerBase):
    """
    MySQL code complexity analyzer with enterprise metrics integration.
    
    Evaluates MySQL scripts across 10 dimensions, each scored 1-4:
    - 1: Simple
    - 2: Medium
    - 3: Complex
    - 4: Very Complex
    
    Uses hybrid approach:
    - Config weights override registry defaults
    - Enterprise validation via metrics module
    - Standardized 0-100 scoring system
    """
    language = "mysql"
    
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
        """Analyze MySQL source code and return complexity metrics."""
        include_cyclomatic = self.config.get("include_cyclomatic", False)
        
        # If code is None or empty, try to read from file path
        if not code and path and path != "<string>":
            file_content = read_file_if_exists(path)
            if file_content:
                code = file_content
        
        # Run complexity analysis
        analyzer = MySQLComplexity()
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
    

class MySQLComplexity:

    """
    Enterprise-grade MySQL complexity analyzer with comprehensive pattern detection.
    Each metric is scored 1 (Simple) to 4 (Very Complex) based on MySQL-specific patterns.
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
        Analyze MySQL source code and return complexity metrics.
        """
        if not code or not code.strip():
            return

        # Remove comments for accurate pattern matching
        code_no_comments = self._remove_comments(code)
        
        # --- 1. SCRIPT SIZE & STRUCTURE ---
        # Enhanced: lines, procedures, functions, triggers, events
        lines = len([line for line in code.split('\n') if line.strip()])
        
        # Calculate nesting depth
        nesting_level = self._get_nesting_level(code_no_comments)
        
        # MySQL objects
        procedures = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?(procedure|proc)\b', code_no_comments, re.IGNORECASE))
        functions = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?function\b', code_no_comments, re.IGNORECASE))
        triggers = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?trigger\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Events (MySQL scheduler)
        events = len(re.findall(r'\bcreate\s+event\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Views and materialized views
        views = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?view\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: small script
        if lines > 100 or procedures > 0 or functions > 0 or nesting_level > 1:
            score = 2  # Medium: moderate size, procedures, or basic nesting
        if lines > 500 or (procedures + functions) > 3 or triggers > 0 or views > 2 or nesting_level > 3:
            score = 3  # Complex: large, multiple objects, triggers, many views, or deep nesting
        if lines > 2000 or (procedures + functions + triggers) > 8 or events > 0 or views > 5 or nesting_level > 5:
            score = 4  # Very Complex: very large, many objects, events, many views, or very deep nesting
        
        self.script_size_structure = score

        # --- 2. DEPENDENCY FOOTPRINT ---
        # Enhanced: databases, tables, views, storage engines, partitions
        use_database = len(re.findall(r'\buse\s+\w+', code_no_comments, re.IGNORECASE))
        table_refs = len(re.findall(r'\bfrom\s+[\w\.`]+|\bjoin\s+[\w\.`]+|\binto\s+[\w\.`]+', code_no_comments, re.IGNORECASE))
        
        # Storage engines
        engines = len(re.findall(r'\bengine\s*=\s*(innodb|myisam|memory|archive|federated|ndb|csv)\b', code_no_comments, re.IGNORECASE))
        
        # Cross-database queries
        cross_db = len(re.findall(r'\w+\.\w+', code_no_comments))
        
        # TIER 2: Partitioning
        partitions = len(re.findall(r'\bpartition\s+by\s+(range|hash|list|key)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 3: InnoDB Cluster / MySQL HeatWave references
        cluster_refs = len(re.findall(r'\bgroup_replication|mysql_innodb_cluster_metadata\b', code_no_comments, re.IGNORECASE))
        
        # Temporary tables
        temp_tables = len(re.findall(r'\bcreate\s+temporary\s+table\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: single database, few tables
        if use_database >= 1 or table_refs > 3 or temp_tables > 0:
            score = 2  # Medium: explicit database use, multiple tables, temp tables
        if table_refs > 10 or cross_db > 0 or engines > 0 or partitions > 0:
            score = 3  # Complex: many tables, cross-db queries, storage engines, partitioning
        if table_refs > 20 or cross_db > 5 or engines > 2 or partitions > 2 or cluster_refs > 0:
            score = 4  # Very Complex: extensive tables, heavy cross-db, multiple engines, cluster features
        
        self.dependency_footprint = score

        # --- 3. ANALYTICS DEPTH ---
        # Enhanced: aggregations, window functions, CTEs, JSON, spatial analytics
        basic_agg = len(re.findall(r'\b(count|sum|avg|min|max|group\s+by)\b', code_no_comments, re.IGNORECASE))
        
        # Window functions (MySQL 8.0+)
        window_funcs = len(re.findall(r'\b(row_number|rank|dense_rank|lead|lag|first_value|last_value|nth_value|ntile|over\s*\()\b', code_no_comments, re.IGNORECASE))
        
        # CTEs (MySQL 8.0+)
        cte = len(re.findall(r'\bwith\s+(recursive\s+)?\w+\s+as\s*\(', code_no_comments, re.IGNORECASE))
        recursive_cte = len(re.findall(r'\bwith\s+recursive\s+\w+', code_no_comments, re.IGNORECASE))
        
        # TIER 1: JSON functions (MySQL 5.7+, enhanced in 8.0+)
        json_funcs = len(re.findall(r'\b(json_extract|json_unquote|json_array|json_object|json_merge|json_search|json_contains|json_valid|json_arrayagg|json_objectagg|\-\>\>?)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Spatial/GIS functions
        spatial_funcs = len(re.findall(r'\b(st_distance|st_contains|st_intersects|st_buffer|st_area|st_length|geometry|point|polygon|linestring|geomfromtext|astext)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Full-text search
        fulltext = len(re.findall(r'\bmatch\s*\(.*\)\s+against\s*\(', code_no_comments, re.IGNORECASE))
        
        # Advanced aggregations
        advanced_agg = len(re.findall(r'\b(std|stddev|variance|bit_and|bit_or|bit_xor)\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic SELECT, no aggregations
        if basic_agg > 0 or json_funcs > 0:
            score = 2  # Medium: GROUP BY, COUNT, SUM, basic JSON
        if window_funcs > 0 or cte > 0 or advanced_agg > 0 or spatial_funcs > 0 or fulltext > 0:
            score = 3  # Complex: window functions, CTEs, spatial, full-text search
        if window_funcs > 3 or recursive_cte > 0 or json_funcs > 5 or spatial_funcs > 3 or fulltext > 2:
            score = 4  # Very Complex: heavy analytics, recursive CTEs, extensive JSON/spatial
        
        self.analytics_depth = score

        # --- 4. SQL & REPORTING LOGIC ---
        # Enhanced: query complexity, joins, unions, subqueries
        joins = len(re.findall(r'\b(inner\s+join|left\s+join|right\s+join|cross\s+join|natural\s+join|straight_join|join)\b', code_no_comments, re.IGNORECASE))
        unions = len(re.findall(r'\bunion\s+(all\s+|distinct\s+)?', code_no_comments, re.IGNORECASE))
        
        # Subqueries
        subqueries = len(re.findall(r'\(\s*select\s+', code_no_comments, re.IGNORECASE))
        
        # Complex WHERE clauses
        complex_where = len(re.findall(r'\bwhere\s+.*\b(and|or)\b.*\b(and|or)\b', code_no_comments, re.IGNORECASE))
        
        # CASE statements
        case_stmt = len(re.findall(r'\bcase\s+when\b', code_no_comments, re.IGNORECASE))
        
        # Query hints (MySQL 8.0+)
        hints = len(re.findall(r'/\*\+\s*(use_index|ignore_index|force_index|straight_join|sql_buffer_result|sql_cache|sql_no_cache)\s*\*/', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic SELECT, no joins
        if joins >= 1 or case_stmt > 0 or subqueries > 0:
            score = 2  # Medium: basic joins, CASE statements, subqueries
        if joins > 3 or unions > 0 or complex_where > 0 or hints > 0:
            score = 3  # Complex: multiple joins, unions, complex WHERE, query hints
        if joins > 6 or unions > 3 or subqueries > 5 or hints > 2:
            score = 4  # Very Complex: many joins/unions, nested subqueries, extensive hints
        
        self.sql_reporting_logic = score

        # --- 5. TRANSFORMATION LOGIC ---
        # Enhanced: data manipulation, JSON operations, string functions
        updates = len(re.findall(r'\bupdate\s+[\w\.`]+', code_no_comments, re.IGNORECASE))
        inserts = len(re.findall(r'\binsert\s+into\b', code_no_comments, re.IGNORECASE))
        deletes = len(re.findall(r'\bdelete\s+from\b', code_no_comments, re.IGNORECASE))
        
        # REPLACE and INSERT ... ON DUPLICATE KEY UPDATE
        replace_stmt = len(re.findall(r'\breplace\s+into\b', code_no_comments, re.IGNORECASE))
        on_duplicate = len(re.findall(r'\bon\s+duplicate\s+key\s+update\b', code_no_comments, re.IGNORECASE))
        
        # Data type conversions
        conversions = len(re.findall(r'\b(cast|convert|format|date_format|str_to_date|unix_timestamp|from_unixtime)\b', code_no_comments, re.IGNORECASE))
        
        # String operations
        string_ops = len(re.findall(r'\b(concat|concat_ws|substring|mid|left|right|trim|ltrim|rtrim|upper|lower|replace|locate|instr|length|char_length)\b', code_no_comments, re.IGNORECASE))
        
        # Date/time functions
        date_funcs = len(re.findall(r'\b(now|curdate|curtime|date|time|timestamp|year|month|day|hour|minute|second|date_add|date_sub|datediff|timestampdiff)\b', code_no_comments, re.IGNORECASE))
        
        # JSON modifications
        json_modify = len(re.findall(r'\b(json_insert|json_replace|json_set|json_remove|json_array_append|json_array_insert)\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic SELECT, no transformations
        if updates > 0 or inserts > 0 or conversions > 2 or string_ops > 0:
            score = 2  # Medium: basic DML, conversions, string operations
        if (updates > 2 and inserts > 2) or replace_stmt > 0 or on_duplicate > 0 or json_modify > 0:
            score = 3  # Complex: multiple DML, REPLACE, JSON modifications
        if (updates > 5 and deletes > 2) or conversions > 10 or string_ops > 8 or json_modify > 3:
            score = 4  # Very Complex: heavy DML operations, extensive transformations
        
        self.transformation_logic = score

        # --- 6. UTILITY COMPLEXITY ---
        # Enhanced: procedures, functions, parameters, cursors, loops
        params = len(re.findall(r'\bin\s+\w+|out\s+\w+|inout\s+\w+', code_no_comments, re.IGNORECASE))
        
        # Variables and declarations
        declares = len(re.findall(r'\bdeclare\s+\w+', code_no_comments, re.IGNORECASE))
        
        # Control flow
        if_stmt = len(re.findall(r'\bif\b', code_no_comments, re.IGNORECASE))
        case_control = len(re.findall(r'\bcase\s+\w+\s+when\b', code_no_comments, re.IGNORECASE))
        loops = len(re.findall(r'\b(while|repeat|loop|for)\b', code_no_comments, re.IGNORECASE))
        
        # Cursors
        cursors = len(re.findall(r'\bdeclare\s+\w+\s+cursor\b', code_no_comments, re.IGNORECASE))
        
        # Nested procedure calls
        call_stmt = len(re.findall(r'\bcall\s+\w+', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Prepared statements
        prepared_stmts = len(re.findall(r'\b(prepare|execute|deallocate)\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no procedures or simple procedures
        if params > 0 or declares > 2 or if_stmt > 1 or call_stmt > 0:
            score = 2  # Medium: procedures with params, basic control flow
        if params > 5 or loops > 0 or cursors > 0 or case_control > 0 or prepared_stmts > 0:
            score = 3  # Complex: many params, loops, cursors, prepared statements
        if cursors > 1 or loops > 2 or (params > 10 and loops > 1) or prepared_stmts > 3:
            score = 4  # Very Complex: multiple cursors, complex loops, extensive prepared statements
        
        self.utility_complexity = score

        # --- 7. EXECUTION CONTROL ---
        # Enhanced: transactions, savepoints, locks, isolation levels
        begin_tran = len(re.findall(r'\bstart\s+transaction|\bbegin\b', code_no_comments, re.IGNORECASE))
        commit = len(re.findall(r'\bcommit\b', code_no_comments, re.IGNORECASE))
        rollback = len(re.findall(r'\brollback\b', code_no_comments, re.IGNORECASE))
        
        # Savepoints
        savepoints = len(re.findall(r'\bsavepoint\s+\w+|\brollback\s+to\s+\w+', code_no_comments, re.IGNORECASE))
        
        # Isolation levels
        isolation = len(re.findall(r'\bset\s+(session\s+)?transaction\s+isolation\s+level\b', code_no_comments, re.IGNORECASE))
        
        # Locking
        locks = len(re.findall(r'\block\s+tables|\bunlock\s+tables|\bfor\s+update|\bshare\s+mode\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: MySQL-specific SET options
        set_options = len(re.findall(r'\bset\s+(autocommit|sql_mode|foreign_key_checks|unique_checks|sql_safe_updates)\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no explicit transactions
        if begin_tran > 0 or commit > 0 or set_options > 0:
            score = 2  # Medium: basic transactions, SET options
        if rollback > 0 or savepoints > 0 or locks > 0:
            score = 3  # Complex: rollbacks, savepoints, locking
        if isolation > 0 or savepoints > 2 or (begin_tran > 3 and rollback > 2):
            score = 4  # Very Complex: custom isolation, nested transactions
        
        self.execution_control = score

        # --- 8. FILE I/O & EXTERNAL INTEGRATION ---
        # Enhanced: file operations, external engines, federated tables
        
        # File operations
        file_ops = len(re.findall(r'\bload\s+data\s+infile|\bselect\s+.*\binto\s+outfile|\bselect\s+.*\binto\s+dumpfile', code_no_comments, re.IGNORECASE))
        
        # TIER 2: FEDERATED storage engine
        federated = len(re.findall(r'\bengine\s*=\s*federated|\bconnection\s*=\s*[\'"]mysql:', code_no_comments, re.IGNORECASE))
        
        # TIER 3: External plugins and UDFs
        plugins = len(re.findall(r'\binstall\s+plugin|\bcreate\s+function\s+\w+\s+returns\s+.*\bsoname\b', code_no_comments, re.IGNORECASE))
        
        # Information Schema / Performance Schema queries
        system_schemas = len(re.findall(r'\b(information_schema|performance_schema|sys)\.\w+', code_no_comments, re.IGNORECASE))
        
        # TIER 3: MySQL HeatWave ML functions
        ml_functions = len(re.findall(r'\bml_train|ml_predict|ml_score|ml_explain\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no external integration
        if system_schemas > 0 or file_ops > 0:
            score = 2  # Medium: system schema queries, basic file operations
        if federated > 0 or file_ops > 1 or system_schemas > 5:
            score = 3  # Complex: federated tables, multiple file ops, extensive system queries
        if plugins > 0 or ml_functions > 0 or federated > 2:
            score = 4  # Very Complex: external plugins, ML functions, multiple federated connections
        
        self.file_io_external_integration = score

        # --- 9. ODS OUTPUT DELIVERY ---
        # Enhanced: result sets, cursors, prepared statements
        select_stmt = len(re.findall(r'\bselect\b', code_no_comments, re.IGNORECASE))
        
        # Multiple result sets from procedures
        multiple_selects = len(re.findall(r'\bselect\b', code_no_comments, re.IGNORECASE))
        
        # Output parameters (OUT, INOUT)
        output_params = len(re.findall(r'\bout\s+\w+|\binout\s+\w+', code_no_comments, re.IGNORECASE))
        
        # Cursor operations
        cursor_ops = len(re.findall(r'\bopen\s+\w+|\bfetch\s+\w+|\bclose\s+\w+', code_no_comments, re.IGNORECASE))
        
        # Prepared statement execution
        prepared_exec = len(re.findall(r'\bexecute\s+\w+', code_no_comments, re.IGNORECASE))
        
        # INTO clauses for result capture
        into_vars = len(re.findall(r'\binto\s+@\w+|\binto\s+\w+', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: single SELECT or no results
        if select_stmt > 1 or output_params > 0 or into_vars > 0:
            score = 2  # Medium: multiple SELECTs, output params, variable capture
        if select_stmt > 3 or cursor_ops > 0 or prepared_exec > 0:
            score = 3  # Complex: many result sets, cursor operations, prepared statement execution
        if select_stmt > 6 or cursor_ops > 3 or (prepared_exec > 2 and output_params > 2):
            score = 4  # Very Complex: many result sets, complex cursor usage, extensive prepared statements
        
        self.ods_output_delivery = score

        # --- 10. ERROR HANDLING & OPTIMIZATION ---
        # Enhanced: error handling, indexes, query optimization, performance
        
        # Error handling
        handlers = len(re.findall(r'\bdeclare\s+.*\bhandler\b|\bdeclare\s+(continue|exit)\s+handler', code_no_comments, re.IGNORECASE))
        resignal = len(re.findall(r'\b(signal|resignal)\b', code_no_comments, re.IGNORECASE))
        
        # Performance optimization
        indexes = len(re.findall(r'\bcreate\s+(unique\s+)?index\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Advanced indexing features
        fulltext_index = len(re.findall(r'\bcreate\s+fulltext\s+index\b', code_no_comments, re.IGNORECASE))
        spatial_index = len(re.findall(r'\bcreate\s+spatial\s+index\b', code_no_comments, re.IGNORECASE))
        
        # Query optimization
        explain_stmt = len(re.findall(r'\bexplain\s+(format\s*=\s*json\s+)?select\b', code_no_comments, re.IGNORECASE))
        analyze_table = len(re.findall(r'\banalyze\s+table\b', code_no_comments, re.IGNORECASE))
        optimize_table = len(re.findall(r'\boptimize\s+table\b', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Performance Schema usage
        perf_schema = len(re.findall(r'\bperformance_schema\.\w+', code_no_comments, re.IGNORECASE))
        
        total_indexes = indexes + fulltext_index + spatial_index
        total_optimization = explain_stmt + analyze_table + optimize_table
        
        score = 1  # Simple: no error handling or optimization
        if handlers > 0 or indexes > 0 or total_optimization > 0:
            score = 2  # Medium: basic error handling, indexing, or optimization
        if resignal > 0 or total_indexes > 2 or perf_schema > 0:
            score = 3  # Complex: advanced error handling, multiple indexes, performance schema
        if handlers > 2 or resignal > 1 or total_indexes > 5 or perf_schema > 3:
            score = 4  # Very Complex: comprehensive error handling, extensive indexing, heavy performance monitoring
        
        self.error_handling_optimization = score

        # --- CYCLOMATIC COMPLEXITY ---
        self.cyclomatic = self._calculate_cyclomatic_complexity(code_no_comments)

    def _remove_comments(self, code: str) -> str:
        """Remove MySQL comments from code for accurate analysis."""
        # Remove C-style block comments /* ... */
        code_no_block = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        
        # Remove MySQL single-line comments -- and #
        code_no_single = re.sub(r'(--|#).*$', '', code_no_block, flags=re.MULTILINE)
        
        return code_no_single

    def _get_nesting_level(self, code: str) -> int:
        """
        Calculate the maximum nesting depth of control structures in MySQL code.
        """
        stack = []
        max_depth = 0

        # Regex patterns for opening and closing structures
        open_pattern = re.compile(r'\b(BEGIN|IF|CASE|WHILE|REPEAT|LOOP|FOR)\b', re.IGNORECASE)
        close_pattern = re.compile(r'\b(END(\s+IF|\s+CASE|\s+WHILE|\s+REPEAT|\s+LOOP|\s+FOR)?|UNTIL)\b', re.IGNORECASE)

        for line in code.splitlines():
            # Ignore comments
            line = re.sub(r'(--|#).*$', '', line).strip()
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
        Calculate cyclomatic complexity for MySQL.
        
        Counts decision points: IF, ELSEIF, CASE WHEN, WHILE, REPEAT, FOR, loops
        Cyclomatic Complexity = decision points + 1
        """
        if_count = len(re.findall(r'\bif\b', code, re.IGNORECASE))
        elseif_count = len(re.findall(r'\belseif\b', code, re.IGNORECASE))
        case_when = len(re.findall(r'\bwhen\b', code, re.IGNORECASE))
        loops = len(re.findall(r'\b(while|repeat|loop|for)\b', code, re.IGNORECASE))
        decision_points = if_count + elseif_count + case_when + loops

        return max(1, decision_points + 1)
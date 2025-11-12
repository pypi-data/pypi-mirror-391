# src/code_analyzer/analyzers/sqlite_analyzer.py
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


class SQLiteAnalyzer(AnalyzerBase):
    """
    SQLite code complexity analyzer with enterprise metrics integration.
    
    Evaluates SQLite scripts across 10 dimensions, each scored 1-4:
    - 1: Simple
    - 2: Medium
    - 3: Complex
    - 4: Very Complex
    
    Uses hybrid approach:
    - Config weights override registry defaults
    - Enterprise validation via metrics module
    - Standardized 0-100 scoring system
    """
    language = "sqlite"
    
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
        """Analyze SQLite source code and return complexity metrics."""
        include_cyclomatic = self.config.get("include_cyclomatic", False)
        
        # If code is None or empty, try to read from file path
        if not code and path and path != "<string>":
            file_content = read_file_if_exists(path)
            if file_content:
                code = file_content
        
        # Run complexity analysis
        analyzer = SQLiteComplexity()
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
    

class SQLiteComplexity:
    """
    Enterprise-grade SQLite complexity analyzer with comprehensive pattern detection.
    Each metric is scored 1 (Simple) to 4 (Very Complex) based on SQLite-specific patterns.
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
        Analyze SparkSQL source code and return complexity metrics.
        """
        if not code or not code.strip():
            return    
    
        # Remove comments for accurate pattern matching
        code_no_comments = self._remove_comments(code)
        
        # Calculate nesting depth
        nesting_level = self._get_nesting_level(code_no_comments)

        # --- 1. SCRIPT SIZE & STRUCTURE ---
        # Enhanced: lines, tables, views, indexes, triggers, virtual tables
        lines = len([line for line in code.split('\n') if line.strip()])
        
        # Database objects
        tables = len(re.findall(r'\bcreate\s+(temp\s+)?table\b', code_no_comments, re.IGNORECASE))
        views = len(re.findall(r'\bcreate\s+(temp\s+)?view\b', code_no_comments, re.IGNORECASE))
        indexes = len(re.findall(r'\bcreate\s+(unique\s+)?index\b', code_no_comments, re.IGNORECASE))
        triggers = len(re.findall(r'\bcreate\s+(temp\s+)?trigger\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Virtual Tables and Extensions
        virtual_tables = len(re.findall(r'\bcreate\s+virtual\s+table\b', code_no_comments, re.IGNORECASE))
        fts_tables = len(re.findall(r'\busing\s+fts[345]\b', code_no_comments, re.IGNORECASE))
        rtree_tables = len(re.findall(r'\busing\s+rtree\b', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Strict Tables (SQLite 3.37+)
        strict_tables = len(re.findall(r'\bstrict\s*\)', code_no_comments, re.IGNORECASE))
        
        # Generated Columns (SQLite 3.31+)
        generated_cols = len(re.findall(r'\bgenerated\s+always\s+as\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: small script
        if lines > 50 or tables > 0 or views > 0 or nesting_level > 1:
            score = 2  # Medium: moderate size, basic objects, basic nesting
        if lines > 200 or tables > 3 or indexes > 2 or triggers > 0 or virtual_tables > 0 or nesting_level > 3:
            score = 3  # Complex: large script, multiple objects, virtual tables, deep nesting
        if lines > 1000 or tables > 10 or triggers > 3 or fts_tables > 0 or rtree_tables > 0 or strict_tables > 0 or nesting_level > 5:
            score = 4  # Very Complex: very large script, many objects, FTS/R*Tree, strict tables, very deep nesting
        
        self.script_size_structure = score

        # --- 2. DEPENDENCY FOOTPRINT ---
        # Enhanced: table references, views, attached databases, foreign keys
        table_refs = len(re.findall(r'\bfrom\s+[\w\.]+|\bjoin\s+[\w\.]+|\binto\s+[\w\.]+', code_no_comments, re.IGNORECASE))
        
        # Attached databases
        attach_db = len(re.findall(r'\battach\s+(database\s+)?', code_no_comments, re.IGNORECASE))
        cross_db_refs = len(re.findall(r'\w+\.\w+\.\w+', code_no_comments))
        
        # Foreign key relationships
        foreign_keys = len(re.findall(r'\bforeign\s+key\b|\breferences\s+\w+', code_no_comments, re.IGNORECASE))
        
        # Temp objects
        temp_tables = len(re.findall(r'\bcreate\s+temp\s+(table|view)\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: few table references
        if table_refs > 3 or temp_tables > 0 or foreign_keys > 0:
            score = 2  # Medium: moderate references, temp objects, foreign keys
        if table_refs > 10 or views > 2 or cross_db_refs > 0 or foreign_keys > 3:
            score = 3  # Complex: many references, views, cross-database queries, many FKs
        if attach_db > 0 or cross_db_refs > 5 or table_refs > 20 or foreign_keys > 8:
            score = 4  # Very Complex: attached databases, many cross-db refs, extensive dependencies
        
        self.dependency_footprint = score

        # --- 3. ANALYTICS DEPTH ---
        # Enhanced: aggregations, window functions, JSON operations, CTEs
        basic_agg = len(re.findall(r'\b(count|sum|avg|min|max|group\s+by)\b', code_no_comments, re.IGNORECASE))
        
        # Advanced aggregations
        advanced_agg = len(re.findall(r'\b(group_concat|total|json_group_array|json_group_object)\b', code_no_comments, re.IGNORECASE))
        
        # Window functions (SQLite 3.25+)
        window_funcs = len(re.findall(r'\b(row_number|rank|dense_rank|lag|lead|first_value|last_value|nth_value|over\s*\()\b', code_no_comments, re.IGNORECASE))
        
        # CTEs (SQLite 3.8.3+)
        cte = len(re.findall(r'\bwith\s+(recursive\s+)?\w+\s+as\s*\(', code_no_comments, re.IGNORECASE))
        recursive_cte = len(re.findall(r'\bwith\s+recursive\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: JSON Functions (SQLite 3.38+)
        json_funcs = len(re.findall(r'\bjson_(extract|array|object|set|insert|replace|remove|patch|valid|type|array_length|each|tree|quote)\b', code_no_comments, re.IGNORECASE))
        
        # Math functions
        math_funcs = len(re.findall(r'\b(abs|round|random|sqrt|power|log|exp|sin|cos|tan|asin|acos|atan|atan2)\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic queries
        if basic_agg > 0 or cte > 0 or math_funcs > 2:
            score = 2  # Medium: aggregations, basic CTEs, math functions
        if advanced_agg > 0 or window_funcs > 0 or json_funcs > 0 or cte > 2:
            score = 3  # Complex: advanced aggregations, window functions, JSON operations, multiple CTEs
        if window_funcs > 3 or recursive_cte > 0 or json_funcs > 5 or (cte > 3 and window_funcs > 1):
            score = 4  # Very Complex: extensive window functions, recursive CTEs, heavy JSON processing
        
        self.analytics_depth = score

        # --- 4. SQL & REPORTING LOGIC ---
        # Enhanced: SELECT complexity, joins, subqueries, UNION operations
        selects = len(re.findall(r'\bselect\b', code_no_comments, re.IGNORECASE))
        joins = len(re.findall(r'\b(inner\s+join|left\s+join|right\s+join|full\s+join|cross\s+join|natural\s+join|join)\b', code_no_comments, re.IGNORECASE))
        unions = len(re.findall(r'\bunion\s+(all\s+)?', code_no_comments, re.IGNORECASE))
        subqueries = len(re.findall(r'\(\s*select\s+', code_no_comments, re.IGNORECASE))
        
        # Complex WHERE clauses
        complex_where = len(re.findall(r'\bwhere\s+.*\b(and|or)\b.*\b(and|or)\b', code_no_comments, re.IGNORECASE))
        
        # CASE expressions
        case_stmt = len(re.findall(r'\bcase\s+when\b', code_no_comments, re.IGNORECASE))
        
        # EXISTS/IN clauses
        exists_in = len(re.findall(r'\b(exists|not\s+exists|in|not\s+in)\s*\(', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic SELECT
        if joins > 0 or unions > 0 or case_stmt > 0 or selects > 3:
            score = 2  # Medium: joins, unions, CASE statements, multiple SELECTs
        if joins > 3 or subqueries > 2 or exists_in > 0 or complex_where > 0:
            score = 3  # Complex: multiple joins, subqueries, EXISTS/IN, complex WHERE
        if joins > 6 or subqueries > 5 or unions > 3 or (exists_in > 2 and subqueries > 3):
            score = 4  # Very Complex: many joins/subqueries, extensive logical complexity
        
        self.sql_reporting_logic = score

        # --- 5. TRANSFORMATION LOGIC ---
        # Enhanced: DML operations, data type conversions, string operations
        inserts = len(re.findall(r'\binsert\s+into\b', code_no_comments, re.IGNORECASE))
        updates = len(re.findall(r'\bupdate\s+\w+\s+set\b', code_no_comments, re.IGNORECASE))
        deletes = len(re.findall(r'\bdelete\s+from\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: UPSERT (SQLite 3.24+)
        upsert = len(re.findall(r'\bon\s+conflict\s+.*\bdo\s+(update|nothing)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 3: RETURNING clause (SQLite 3.35+)
        returning = len(re.findall(r'\breturning\b', code_no_comments, re.IGNORECASE))
        
        # Data conversions
        conversions = len(re.findall(r'\b(cast|typeof|length|coalesce|ifnull|nullif|iif)\b', code_no_comments, re.IGNORECASE))
        
        # String operations
        string_ops = len(re.findall(r'\b(substr|replace|trim|ltrim|rtrim|upper|lower|instr|like|glob|regexp)\b', code_no_comments, re.IGNORECASE))
        
        # Date/time functions
        date_funcs = len(re.findall(r'\b(date|time|datetime|julianday|strftime|unixepoch)\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic queries
        if inserts > 0 or updates > 0 or conversions > 2:
            score = 2  # Medium: basic DML, conversions
        if deletes > 0 or upsert > 0 or string_ops > 3 or date_funcs > 2:
            score = 3  # Complex: DELETE operations, UPSERT, extensive string/date functions
        if returning > 0 or upsert > 2 or (updates > 5 and deletes > 2) or string_ops > 8:
            score = 4  # Very Complex: RETURNING clause, complex UPSERT, heavy DML, extensive transformations
        
        self.transformation_logic = score

        # --- 6. UTILITY COMPLEXITY ---
        # Enhanced: user-defined functions, virtual tables, extensions, application functions
        
        # Application-defined functions (not built-in)
        app_functions = len(re.findall(r'\b(?!(?:abs|coalesce|ifnull|iif|instr|length|like|lower|ltrim|max|min|nullif|printf|quote|random|replace|round|rtrim|soundex|substr|trim|typeof|unicode|upper|zeroblob|date|time|datetime|julianday|strftime|unixepoch|count|sum|avg|group_concat|total|json_extract|json_array|json_object|json_set|json_insert|json_replace|json_remove|json_patch|json_valid|json_type|json_array_length|json_each|json_tree|json_quote)\b)\w+\s*\(', code_no_comments, re.IGNORECASE))
        
        # Virtual table usage
        virtual_table_queries = virtual_tables + len(re.findall(r'\bfrom\s+\w*fts\w*|\bfrom\s+\w*rtree\w*', code_no_comments, re.IGNORECASE))
        
        # Extension loading
        load_extension = len(re.findall(r'\bload_extension\b', code_no_comments, re.IGNORECASE))
        
        # Pragma statements
        pragmas = len(re.findall(r'\bpragma\s+\w+', code_no_comments, re.IGNORECASE))
        
        # Complex constraints
        constraints = len(re.findall(r'\b(check|unique|primary\s+key|foreign\s+key)\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic SQL
        if pragmas > 0 or constraints > 2 or app_functions > 0:
            score = 2  # Medium: pragma usage, constraints, application functions
        if virtual_table_queries > 0 or constraints > 5 or app_functions > 3:
            score = 3  # Complex: virtual tables, many constraints, multiple app functions
        if load_extension > 0 or virtual_table_queries > 2 or (app_functions > 5 and pragmas > 3):
            score = 4  # Very Complex: extension loading, extensive virtual table usage, many app functions
        
        self.utility_complexity = score

        # --- 7. EXECUTION CONTROL ---
        # Enhanced: transactions, savepoints, database locking
        begin_trans = len(re.findall(r'\bbegin\s+(transaction|immediate|exclusive|deferred)?\b', code_no_comments, re.IGNORECASE))
        commit = len(re.findall(r'\bcommit\b', code_no_comments, re.IGNORECASE))
        rollback = len(re.findall(r'\brollback\b', code_no_comments, re.IGNORECASE))
        
        # Savepoints (SQLite 3.6.8+)
        savepoints = len(re.findall(r'\bsavepoint\s+\w+|\brelease\s+savepoint\s+\w+|\brollback\s+to\s+savepoint\s+\w+', code_no_comments, re.IGNORECASE))
        
        # Pragma settings for transaction control
        trans_pragmas = len(re.findall(r'\bpragma\s+(journal_mode|synchronous|locking_mode|temp_store|cache_size)\b', code_no_comments, re.IGNORECASE))
        
        # WAL mode
        wal_mode = len(re.findall(r'\bwal\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no explicit transaction control
        if begin_trans > 0 or commit > 0 or trans_pragmas > 0:
            score = 2  # Medium: basic transactions, pragma settings
        if rollback > 0 or savepoints > 0 or wal_mode > 0:
            score = 3  # Complex: rollbacks, savepoints, WAL mode
        if savepoints > 2 or (begin_trans > 3 and rollback > 1) or trans_pragmas > 5:
            score = 4  # Very Complex: multiple savepoints, nested transactions, extensive pragma usage
        
        self.execution_control = score

        # --- 8. FILE I/O & EXTERNAL INTEGRATION ---
        # Enhanced: file operations, CSV imports, external databases, backups
        attach_database = attach_db
        detach_database = len(re.findall(r'\bdetach\s+(database\s+)?\w+', code_no_comments, re.IGNORECASE))
        
        # Import/export operations
        csv_imports = len(re.findall(r'\.import\s+.*\.csv', code_no_comments, re.IGNORECASE))
        csv_mode = len(re.findall(r'\.mode\s+csv', code_no_comments, re.IGNORECASE))
        
        # Backup operations
        backup_ops = len(re.findall(r'\.backup\s+|\bvacuum\s+into\b', code_no_comments, re.IGNORECASE))
        
        # External file references
        file_refs = len(re.findall(r'["\'][\w\\\/\.:]+\.(db|sqlite|csv|txt|json)["\']', code_no_comments, re.IGNORECASE))
        
        # SQLite shell commands
        shell_commands = len(re.findall(r'\.(output|open|read|shell|system)\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no external integration
        if file_refs > 0 or csv_mode > 0:
            score = 2  # Medium: file references, CSV mode
        if attach_database > 0 or csv_imports > 0 or backup_ops > 0:
            score = 3  # Complex: attached databases, imports, backups
        if shell_commands > 0 or (attach_database > 2 and file_refs > 3):
            score = 4  # Very Complex: shell commands, multiple attached databases and file operations
        
        self.file_io_external_integration = score

        # --- 9. ODS OUTPUT DELIVERY ---
        # Enhanced: result formatting, output modes, data export
        select_statements = selects
        
        # Output formatting
        output_modes = len(re.findall(r'\.mode\s+(csv|json|html|tabs|tcl|list|line|column)\b', code_no_comments, re.IGNORECASE))
        headers = len(re.findall(r'\.headers\s+(on|off)\b', code_no_comments, re.IGNORECASE))
        
        # Export operations
        output_files = len(re.findall(r'\.output\s+[\w\\\/\.:]+', code_no_comments, re.IGNORECASE))
        
        # Complex result sets
        complex_selects = len(re.findall(r'select\s+.*,.*,.*from', code_no_comments, re.IGNORECASE))
        
        # Multiple result formats
        format_variety = len(set(re.findall(r'\.mode\s+(\w+)', code_no_comments, re.IGNORECASE)))
        
        score = 1  # Simple: basic output
        if select_statements > 3 or output_modes > 0:
            score = 2  # Medium: multiple selects, output formatting
        if complex_selects > 2 or output_files > 0 or format_variety > 1:
            score = 3  # Complex: complex selects, file output, multiple formats
        if output_files > 3 or (format_variety > 2 and complex_selects > 5):
            score = 4  # Very Complex: multiple output files, various formats, complex result sets
        
        self.ods_output_delivery = score

        # --- 10. ERROR HANDLING & OPTIMIZATION ---
        # Enhanced: constraints, indexes, optimization, error checking
        
        # Constraints and integrity
        check_constraints = len(re.findall(r'\bcheck\s*\(', code_no_comments, re.IGNORECASE))
        unique_constraints = len(re.findall(r'\bunique\s*\(', code_no_comments, re.IGNORECASE))
        not_null = len(re.findall(r'\bnot\s+null\b', code_no_comments, re.IGNORECASE))
        
        # Index optimization
        index_count = indexes
        covering_indexes = len(re.findall(r'create\s+index\s+.*\binclude\s*\(', code_no_comments, re.IGNORECASE))
        
        # Query optimization pragmas
        opt_pragmas = len(re.findall(r'\bpragma\s+(optimize|analysis_limit|case_sensitive_like|automatic_index)\b', code_no_comments, re.IGNORECASE))
        
        # EXPLAIN query plans
        explain_plans = len(re.findall(r'\bexplain\s+(query\s+plan\s+)?', code_no_comments, re.IGNORECASE))
        
        # ANALYZE statistics
        analyze_stats = len(re.findall(r'\banalyze\b', code_no_comments, re.IGNORECASE))
        
        # Error handling
        on_conflict = len(re.findall(r'\bon\s+conflict\s+(abort|fail|ignore|replace|rollback)\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic schema
        if not_null > 2 or index_count > 0 or check_constraints > 0:
            score = 2  # Medium: constraints, basic indexing
        if unique_constraints > 0 or explain_plans > 0 or on_conflict > 0 or opt_pragmas > 0:
            score = 3  # Complex: unique constraints, query planning, conflict resolution, optimization
        if analyze_stats > 0 or covering_indexes > 0 or (opt_pragmas > 3 and explain_plans > 2):
            score = 4  # Very Complex: statistics analysis, covering indexes, extensive optimization
        
        self.error_handling_optimization = score

        # Calculate cyclomatic complexity
        self.cyclomatic = self._calculate_cyclomatic_complexity(code_no_comments)

    def _remove_comments(self, code: str) -> str:
        """Remove SQL comments from code for accurate analysis."""
        # Remove single-line comments --
        code_no_single = re.sub(r'--.*$', '', code, flags=re.MULTILINE)
        
        # Remove block comments /* ... */
        code_no_block = re.sub(r'/\*.*?\*/', '', code_no_single, flags=re.DOTALL)
        
        return code_no_block

    def _get_nesting_level(self, code: str) -> int:
        """
        Calculate the maximum nesting depth of control structures in SQLite code.
        """
        stack = []
        max_depth = 0

        # Regex patterns for opening and closing structures
        open_pattern = re.compile(r'\b(CASE|BEGIN|WITH)\b', re.IGNORECASE)
        close_pattern = re.compile(r'\b(END|COMMIT|ROLLBACK)\b', re.IGNORECASE)

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
        Calculate cyclomatic complexity for SQLite SQL.
        
        Counts decision points: CASE WHEN, IF conditions in triggers, logical operators
        Cyclomatic Complexity = decision points + 1
        """
        case_when = len(re.findall(r'\bwhen\b', code, re.IGNORECASE))
        if_conditions = len(re.findall(r'\bif\b', code, re.IGNORECASE))
        logical_ops = len(re.findall(r'\b(and|or)\b', code, re.IGNORECASE))
        
        decision_points = case_when + if_conditions + logical_ops
        return max(1, decision_points + 1)
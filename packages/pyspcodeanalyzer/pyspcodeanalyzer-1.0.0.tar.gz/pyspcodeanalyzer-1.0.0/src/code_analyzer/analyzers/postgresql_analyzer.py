# src/code_analyzer/analyzers/postgresql_analyzer.py
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


class PostgreSQLAnalyzer(AnalyzerBase):
    """
    PostgreSQL code complexity analyzer with enterprise metrics integration.
    
    Evaluates PostgreSQL scripts across 10 dimensions, each scored 1-4:
    - 1: Simple
    - 2: Medium
    - 3: Complex
    - 4: Very Complex
    
    Uses hybrid approach:
    - Config weights override registry defaults
    - Enterprise validation via metrics module
    - Standardized 0-100 scoring system
    """
    language = "postgresql"
    
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
        """Analyze PostgreSQL source code and return complexity metrics."""
        include_cyclomatic = self.config.get("include_cyclomatic", False)
        
        # If code is None or empty, try to read from file path
        if not code and path and path != "<string>":
            file_content = read_file_if_exists(path)
            if file_content:
                code = file_content
        
        # Run complexity analysis
        analyzer = PostgreSQLComplexity()
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
    

class PostgreSQLComplexity:
    """
    Enterprise-grade PostgreSQL complexity analyzer with comprehensive pattern detection.
    Each metric is scored 1 (Simple) to 4 (Very Complex) based on PostgreSQL-specific patterns.
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
        Analyze PostgreSQL source code and return complexity metrics.
        """
        if not code or not code.strip():
            return
        
        # Remove comments for accurate analysis
        code_no_comments = self._remove_comments(code)
        
        # Calculate nesting depth
        nesting_level = self._get_nesting_level(code_no_comments)

        # --- 1. SCRIPT SIZE & STRUCTURE ---
        # Enhanced: lines, functions, procedures, triggers, custom types, schemas
        lines = len([line for line in code.split('\n') if line.strip()])
        
        # PostgreSQL objects
        functions = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?function\b', code_no_comments, re.IGNORECASE))
        procedures = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?procedure\b', code_no_comments, re.IGNORECASE))  # PostgreSQL 11+
        triggers = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?trigger\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Custom Types and Domains
        custom_types = len(re.findall(r'\bcreate\s+type\s+\w+\s+as\s+(enum|composite|\()', code_no_comments, re.IGNORECASE))
        domains = len(re.findall(r'\bcreate\s+domain\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Extensions and Schemas
        extensions = len(re.findall(r'\bcreate\s+extension\b', code_no_comments, re.IGNORECASE))
        schemas = len(re.findall(r'\bcreate\s+schema\b', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Advanced Objects
        operators = len(re.findall(r'\bcreate\s+operator\b', code_no_comments, re.IGNORECASE))
        operator_classes = len(re.findall(r'\bcreate\s+operator\s+class\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: small script
        if lines > 100 or functions > 0 or procedures > 0 or nesting_level > 1:
            score = 2  # Medium: moderate size, functions, or basic nesting
        if lines > 500 or (functions + procedures) > 3 or triggers > 0 or custom_types > 0 or nesting_level > 3:
            score = 3  # Complex: large, multiple objects, custom types, or deep nesting
        if lines > 2000 or (functions + procedures + triggers) > 8 or extensions > 0 or operators > 0 or nesting_level > 5:
            score = 4  # Very Complex: very large, many objects, extensions, custom operators, or very deep nesting
        
        self.script_size_structure = score

        # --- 2. DEPENDENCY FOOTPRINT ---
        # Enhanced: tables, views, schemas, foreign servers, materialized views
        tables = len(re.findall(r'\bfrom\s+(\w+\.)?(\w+)', code_no_comments, re.IGNORECASE))
        tables += len(re.findall(r'\bjoin\s+(\w+\.)?(\w+)', code_no_comments, re.IGNORECASE))
        
        # Views and materialized views
        views = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?view\b', code_no_comments, re.IGNORECASE))
        materialized_views = len(re.findall(r'\bcreate\s+materialized\s+view\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Foreign Data Wrappers
        foreign_servers = len(re.findall(r'\bcreate\s+server\b', code_no_comments, re.IGNORECASE))
        foreign_tables = len(re.findall(r'\bcreate\s+foreign\s+table\b', code_no_comments, re.IGNORECASE))
        
        # Schema usage
        schema_refs = len(re.findall(r'\w+\.\w+', code_no_comments))
        
        # TIER 3: Logical Replication
        publications = len(re.findall(r'\bcreate\s+publication\b', code_no_comments, re.IGNORECASE))
        subscriptions = len(re.findall(r'\bcreate\s+subscription\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: few tables
        if tables > 3 or views > 0 or schema_refs > 2:
            score = 2  # Medium: multiple tables, views, schema usage
        if tables > 10 or materialized_views > 0 or foreign_tables > 0 or schema_refs > 10:
            score = 3  # Complex: many tables, materialized views, foreign tables
        if tables > 20 or foreign_servers > 0 or publications > 0 or subscriptions > 0:
            score = 4  # Very Complex: extensive dependencies, foreign servers, logical replication
        
        self.dependency_footprint = score

        # --- 3. ANALYTICS DEPTH ---
        # Enhanced: aggregations, window functions, statistical functions, arrays
        basic_agg = len(re.findall(r'\b(count|sum|avg|min|max|group\s+by)\b', code_no_comments, re.IGNORECASE))
        
        # Advanced aggregations and statistics
        advanced_agg = len(re.findall(r'\b(stddev|variance|corr|covar_pop|percentile_cont|mode)\b', code_no_comments, re.IGNORECASE))
        
        # Window functions
        window_funcs = len(re.findall(r'\b(row_number|rank|dense_rank|lead|lag|first_value|last_value|over\s*\()\b', code_no_comments, re.IGNORECASE))
        
        # CTEs and recursive queries
        cte = len(re.findall(r'\bwith\s+(\w+\s+)?as\s*\(', code_no_comments, re.IGNORECASE))
        recursive_cte = len(re.findall(r'\bwith\s+recursive\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Arrays and Complex Data Types
        arrays = len(re.findall(r'\[\]|\barray\[|\bunnest\(', code_no_comments, re.IGNORECASE))
        
        # TIER 2: JSONB Operations
        jsonb = len(re.findall(r'\bjsonb_|\->>|\->|\#>|\#>>', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Advanced Analytics
        hypothetical_sets = len(re.findall(r'\b(rank|dense_rank|percent_rank|cume_dist)\s*\(\s*\)\s+within\s+group\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic queries
        if basic_agg > 0 or cte > 0 or arrays > 0:
            score = 2  # Medium: aggregations, CTEs, arrays
        if window_funcs > 0 or advanced_agg > 0 or jsonb > 0 or recursive_cte > 0:
            score = 3  # Complex: window functions, JSONB, recursive queries
        if window_funcs > 3 or hypothetical_sets > 0 or (recursive_cte > 0 and jsonb > 2):
            score = 4  # Very Complex: extensive analytics, hypothetical sets
        
        self.analytics_depth = score

        # --- 4. SQL & REPORTING LOGIC ---
        # Enhanced: query complexity, joins, unions, subqueries
        joins = len(re.findall(r'\b(inner\s+join|left\s+join|right\s+join|full\s+join|cross\s+join|join)\b', code_no_comments, re.IGNORECASE))
        unions = len(re.findall(r'\bunion\s+(all\s+)?', code_no_comments, re.IGNORECASE))
        
        # Subqueries and EXISTS
        subqueries = len(re.findall(r'\(\s*select\s+', code_no_comments, re.IGNORECASE))
        exists_queries = len(re.findall(r'\bexists\s*\(', code_no_comments, re.IGNORECASE))
        
        # CASE statements
        case_stmt = len(re.findall(r'\bcase\s+when\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Lateral Joins (PostgreSQL-specific)
        lateral_joins = len(re.findall(r'\blateral\s+', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic SELECT
        if joins >= 1 or case_stmt > 0 or unions > 0:
            score = 2  # Medium: joins, CASE statements
        if joins > 3 or subqueries > 2 or exists_queries > 0 or lateral_joins > 0:
            score = 3  # Complex: multiple joins, subqueries, lateral joins
        if joins > 6 or subqueries > 5 or (lateral_joins > 0 and window_funcs > 0):
            score = 4  # Very Complex: many joins, complex subqueries, advanced patterns
        
        self.sql_reporting_logic = score

        # --- 5. TRANSFORMATION LOGIC ---
        # Enhanced: DML operations, UPSERT, data type conversions
        updates = len(re.findall(r'\bupdate\s+\w+', code_no_comments, re.IGNORECASE))
        inserts = len(re.findall(r'\binsert\s+into\b', code_no_comments, re.IGNORECASE))
        deletes = len(re.findall(r'\bdelete\s+from\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: UPSERT (ON CONFLICT)
        upsert = len(re.findall(r'\bon\s+conflict\b', code_no_comments, re.IGNORECASE))
        
        # Data type conversions
        conversions = len(re.findall(r'\b(cast|::|\bto_char|\bto_number|\bto_date)\b', code_no_comments, re.IGNORECASE))
        
        # String operations
        string_ops = len(re.findall(r'\b(substring|position|trim|regexp_replace|split_part|concat|format)\b', code_no_comments, re.IGNORECASE))
        
        # Date/time functions
        date_funcs = len(re.findall(r'\b(now|current_timestamp|extract|date_trunc|age|interval)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Bulk Operations
        copy_ops = len(re.findall(r'\bcopy\s+\w+\s+(from|to)\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic SELECT
        if updates > 0 or inserts > 0 or conversions > 2:
            score = 2  # Medium: basic DML, conversions
        if upsert > 0 or copy_ops > 0 or string_ops > 3 or date_funcs > 3:
            score = 3  # Complex: UPSERT, COPY, extensive transformations
        if (upsert > 0 and updates > 3) or copy_ops > 1 or (string_ops > 6 and date_funcs > 6):
            score = 4  # Very Complex: complex UPSERT patterns, bulk operations
        
        self.transformation_logic = score

        # --- 6. UTILITY COMPLEXITY ---
        # Enhanced: functions, procedures, parameters, returns, exception handling
        # Function parameters and returns
        params = len(re.findall(r'\b\w+\s+(integer|text|varchar|boolean|numeric|timestamp|json|jsonb)\b', code_no_comments, re.IGNORECASE))
        
        # PL/pgSQL variables
        declares = len(re.findall(r'\bdeclare\s+\w+', code_no_comments, re.IGNORECASE))
        
        # Control flow
        if_stmt = len(re.findall(r'\bif\b', code_no_comments, re.IGNORECASE))
        loops = len(re.findall(r'\b(loop|while|for)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Records and Custom Types
        records = len(re.findall(r'\b\w+%rowtype|\brecord\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Table Functions and Set-Returning Functions
        returns_table = len(re.findall(r'\breturns\s+table\b', code_no_comments, re.IGNORECASE))
        returns_setof = len(re.findall(r'\breturns\s+setof\b', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Security Definer and Language Extensions
        security_definer = len(re.findall(r'\bsecurity\s+definer\b', code_no_comments, re.IGNORECASE))
        language_c = len(re.findall(r'\blanguage\s+c\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic functions
        if params > 0 or declares > 2 or if_stmt > 1:
            score = 2  # Medium: parameters, variables, basic control flow
        if loops > 0 or records > 0 or returns_table > 0 or returns_setof > 0:
            score = 3  # Complex: loops, records, table functions
        if (loops > 2 and records > 1) or security_definer > 0 or language_c > 0:
            score = 4  # Very Complex: complex control flow, security features, C extensions
        
        self.utility_complexity = score

        # --- 7. EXECUTION CONTROL ---
        # Enhanced: transactions, savepoints, advisory locks, prepared statements
        begin_trans = len(re.findall(r'\bbegin\b', code_no_comments, re.IGNORECASE))
        commit = len(re.findall(r'\bcommit\b', code_no_comments, re.IGNORECASE))
        rollback = len(re.findall(r'\brollback\b', code_no_comments, re.IGNORECASE))
        
        # Savepoints
        savepoints = len(re.findall(r'\bsavepoint\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Advisory Locks
        advisory_locks = len(re.findall(r'\bpg_advisory_lock|\bpg_try_advisory_lock\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Prepared Statements
        prepared = len(re.findall(r'\bprepare\s+\w+|\bexecute\s+\w+', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Listen/Notify
        listen_notify = len(re.findall(r'\b(listen|notify|unlisten)\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no explicit transaction control
        if begin_trans > 0 or commit > 0:
            score = 2  # Medium: basic transaction control
        if rollback > 0 or savepoints > 0 or prepared > 0:
            score = 3  # Complex: rollbacks, savepoints, prepared statements
        if advisory_locks > 0 or listen_notify > 0 or (savepoints > 2 and rollback > 2):
            score = 4  # Very Complex: advisory locks, messaging, complex transaction patterns
        
        self.execution_control = score

        # --- 8. FILE I/O & EXTERNAL INTEGRATION ---
        # Enhanced: foreign data wrappers, COPY, extensions, external procedures
        # TIER 2: Foreign Data Wrappers
        fdw_usage = foreign_tables + foreign_servers
        
        # File operations
        copy_files = len(re.findall(r'\bcopy\s+.*\b(from|to)\s+\'[^\']*\.\w+\'', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Extensions and External Languages
        plpython = len(re.findall(r'\blanguage\s+plpython', code_no_comments, re.IGNORECASE))
        plperl = len(re.findall(r'\blanguage\s+plperl', code_no_comments, re.IGNORECASE))
        pltcl = len(re.findall(r'\blanguage\s+pltcl', code_no_comments, re.IGNORECASE))
        
        # System functions
        system_funcs = len(re.findall(r'\b(pg_stat_|pg_catalog\.|information_schema\.)', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no external integration
        if system_funcs > 0 or copy_files > 0:
            score = 2  # Medium: system functions, file operations
        if fdw_usage > 0 or extensions > 0 or (copy_files > 1 and system_funcs > 3):
            score = 3  # Complex: foreign data wrappers, extensions
        if plpython > 0 or plperl > 0 or pltcl > 0 or (fdw_usage > 0 and extensions > 1):
            score = 4  # Very Complex: external languages, extensive integration
        
        self.file_io_external_integration = score

        # --- 9. ODS OUTPUT DELIVERY ---
        # Enhanced: result sets, cursors, table functions, arrays
        select_stmt = len(re.findall(r'\bselect\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Cursors
        cursors = len(re.findall(r'\bdeclare\s+\w+\s+cursor\b', code_no_comments, re.IGNORECASE))
        fetch = len(re.findall(r'\bfetch\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Table Functions and Set-Returning Functions
        table_functions = returns_table + returns_setof
        
        # TIER 2: Array Returns
        array_returns = len(re.findall(r'\breturns\s+\w+\[\]', code_no_comments, re.IGNORECASE))
        
        # Output parameters (OUT, INOUT)
        output_params = len(re.findall(r'\b(out|inout)\s+\w+', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic SELECT
        if select_stmt > 1 or output_params > 0:
            score = 2  # Medium: multiple queries, output parameters
        if cursors > 0 or table_functions > 0 or array_returns > 0:
            score = 3  # Complex: cursors, table functions, arrays
        if (cursors > 0 and fetch > 3) or table_functions > 2 or (array_returns > 0 and jsonb > 0):
            score = 4  # Very Complex: complex cursors, multiple table functions, advanced returns
        
        self.ods_output_delivery = score

        # --- 10. ERROR HANDLING & OPTIMIZATION ---
        # Enhanced: exceptions, hints, indexing, performance tuning
        # Exception handling
        exceptions = len(re.findall(r'\bexception\s+when\b', code_no_comments, re.IGNORECASE))
        raise_stmt = len(re.findall(r'\braise\s+(exception|notice|warning)\b', code_no_comments, re.IGNORECASE))
        
        # Performance optimization
        explain = len(re.findall(r'\bexplain\s+(analyze\s+)?', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Advanced Indexing
        indexes = len(re.findall(r'\bcreate\s+(unique\s+)?index\b', code_no_comments, re.IGNORECASE))
        partial_indexes = len(re.findall(r'\bcreate\s+index\s+.*\bwhere\b', code_no_comments, re.IGNORECASE))
        gin_gist = len(re.findall(r'\busing\s+(gin|gist|spgist|brin)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Vacuum and Maintenance
        vacuum = len(re.findall(r'\bvacuum\s+(analyze\s+)?', code_no_comments, re.IGNORECASE))
        analyze_stmt = len(re.findall(r'\banalyze\s+', code_no_comments, re.IGNORECASE))
        
        # Performance hints and settings
        set_work_mem = len(re.findall(r'\bset\s+work_mem\b', code_no_comments, re.IGNORECASE))
        parallel_hints = len(re.findall(r'\bparallel\s+(safe|unsafe|restricted)\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no error handling or optimization
        if exceptions > 0 or raise_stmt > 0 or indexes > 0:
            score = 2  # Medium: basic exception handling, indexing
        if exceptions > 2 or partial_indexes > 0 or gin_gist > 0 or explain > 0:
            score = 3  # Complex: robust error handling, advanced indexing, performance analysis
        if vacuum > 0 or parallel_hints > 0 or (gin_gist > 1 and partial_indexes > 1):
            score = 4  # Very Complex: maintenance operations, parallel execution, advanced optimization
        
        self.error_handling_optimization = score

        # Calculate cyclomatic complexity
        self.cyclomatic = self._calculate_cyclomatic_complexity(code_no_comments)

    def _remove_comments(self, code: str) -> str:
        """Remove PostgreSQL comments from code."""
        # Remove block comments /* ... */
        code_no_block = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        
        # Remove single-line comments --
        code_no_single = re.sub(r'--.*$', '', code_no_block, flags=re.MULTILINE)
        
        return code_no_single

    def _get_nesting_level(self, code: str) -> int:
        """
        Calculate the maximum nesting depth of control structures in PostgreSQL code.
        """
        stack = []
        max_depth = 0

        # PostgreSQL control structures
        open_pattern = re.compile(r'\b(BEGIN|IF|LOOP|CASE|FOR|WHILE)\b', re.IGNORECASE)
        close_pattern = re.compile(r'\bEND(\s+IF|\s+LOOP|\s+CASE)?\b', re.IGNORECASE)

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
        Calculate cyclomatic complexity for PostgreSQL code.
        
        Counts decision points: IF, ELSIF, LOOP, WHILE, FOR, CASE WHEN, EXCEPTION handlers
        """
        if_count = len(re.findall(r'\bif\b', code, re.IGNORECASE))
        elsif_count = len(re.findall(r'\belsif\b', code, re.IGNORECASE))
        loop_count = len(re.findall(r'\b(loop|while|for)\b', code, re.IGNORECASE))
        case_when = len(re.findall(r'\bwhen\b', code, re.IGNORECASE))
        exception_when = len(re.findall(r'\bexception\s+when\b', code, re.IGNORECASE))
        
        decision_points = if_count + elsif_count + loop_count + case_when + exception_when
        
        return max(1, decision_points + 1)
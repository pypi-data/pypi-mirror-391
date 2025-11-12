# src/code_analyzer/analyzers/oracle_analyzer.py
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


class OracleAnalyzer(AnalyzerBase):
    """
    Oracle code complexity analyzer with enterprise metrics integration.
    
    Evaluates Oracle scripts across 10 dimensions, each scored 1-4:
    - 1: Simple
    - 2: Medium
    - 3: Complex
    - 4: Very Complex
    
    Uses hybrid approach:
    - Config weights override registry defaults
    - Enterprise validation via metrics module
    - Standardized 0-100 scoring system
    """
    language = "oracle"
    
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
        """Analyze Oracle source code and return complexity metrics."""
        include_cyclomatic = self.config.get("include_cyclomatic", False)
        
        # If code is None or empty, try to read from file path
        if not code and path and path != "<string>":
            file_content = read_file_if_exists(path)
            if file_content:
                code = file_content
        
        # Run complexity analysis
        analyzer = OracleComplexity()
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
    


class OracleComplexity:
    """
    Enterprise-grade Oracle PL/SQL complexity analyzer with comprehensive pattern detection.
    Each metric is scored 1 (Simple) to 4 (Very Complex) based on Oracle PL/SQL-specific patterns.
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
        Oracle PL/SQL Complexity Analyzer.
        
        Evaluates PL/SQL scripts across 10 dimensions, each scored 1-4:
        - 1: Simple
        - 2: Medium
        - 3: Complex
        - 4: Very Complex
        
        Each dimension has weight 10, so total score ranges from 10 to 40.
        """
        if not code or not code.strip():
            return
        
        # Remove comments for accurate analysis
        code_no_comments = self._remove_comments(code)

        # --- 1. SCRIPT SIZE & STRUCTURE ---
        # Enhanced: lines, procedures, functions, packages, types, triggers
        lines = len([line for line in code.split('\n') if line.strip()])
        
        # PL/SQL objects
        procedures = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?procedure\b', code_no_comments, re.IGNORECASE))
        functions = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?function\b', code_no_comments, re.IGNORECASE))
        packages = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?package\b', code_no_comments, re.IGNORECASE))
        triggers = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?trigger\b', code_no_comments, re.IGNORECASE))
        types = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?type\b', code_no_comments, re.IGNORECASE))
        
        # Pipelined functions
        pipelined = len(re.findall(r'\bpipelined\b', code_no_comments, re.IGNORECASE))
        
        # SQL Macros (Oracle 19c+)
        sql_macros = len(re.findall(r'\bsql_macro\b', code_no_comments, re.IGNORECASE))
        
        # Polymorphic Table Functions (Oracle 18c+)
        ptf = len(re.findall(r'\bpolymorphic\b', code_no_comments, re.IGNORECASE))

        # Calculate nesting depth
        nesting_level = self._get_nesting_level(code_no_comments)
        
        score = 1  # Simple: small script
        if lines > 100 or procedures > 0 or functions > 0 or nesting_level > 1:
            score = 2  # Medium: moderate size, procedures, or basic nesting
        if lines > 500 or packages > 0 or (procedures + functions) > 3 or triggers > 0 or pipelined > 0 or nesting_level > 3:
            score = 3  # Complex: large, packages, multiple objects, pipelined functions, or deep nesting
        if lines > 2000 or packages > 2 or (procedures + functions + triggers) > 8 or types > 1 or sql_macros > 0 or ptf > 0 or nesting_level > 5:
            score = 4  # Very Complex: very large, multiple packages, many objects, SQL macros, PTF, or very deep nesting
        
        self.script_size_structure = score

        # --- 2. DEPENDENCY FOOTPRINT ---
        # Enhanced: tables, views, sequences, synonyms, DBLinks, materialized views
        tables = len(re.findall(r'\bfrom\s+(\w+\.)?(\w+)', code_no_comments, re.IGNORECASE))
        joins = len(re.findall(r'\b(inner\s+join|left\s+join|right\s+join|full\s+join|cross\s+join|join)\b', code_no_comments, re.IGNORECASE))
        
        # Schema references
        schema_refs = len(re.findall(r'\b\w+\.\w+', code_no_comments))
        
        # Database links
        dblinks = len(re.findall(r'@\w+', code_no_comments))
        
        # Views and materialized views
        views = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?(materialized\s+)?view\b', code_no_comments, re.IGNORECASE))
        
        # Sequences
        sequences = len(re.findall(r'\b\w+\.nextval|\w+\.currval', code_no_comments, re.IGNORECASE))
        
        # Synonyms
        synonyms = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?synonym\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: External tables
        external_tables = len(re.findall(r'\bcreate\s+.*\bexternal\s+table\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: single table
        if tables > 2 or joins > 0 or schema_refs > 2:
            score = 2  # Medium: multiple tables or joins
        if tables > 5 or joins > 3 or dblinks > 0 or views > 0 or sequences > 2 or external_tables > 0:
            score = 3  # Complex: many tables, DBLinks, views, external tables
        if tables > 10 or joins > 6 or dblinks > 2 or (views > 2 and sequences > 3) or synonyms > 0:
            score = 4  # Very Complex: extensive dependencies across databases
        
        self.dependency_footprint = score

        # --- 3. ANALYTICS DEPTH ---
        # Enhanced: CTEs, window functions, hierarchical queries, PIVOT, MODEL, advanced analytics
        cte = len(re.findall(r'\bwith\s+\w+\s+as\s*\(', code_no_comments, re.IGNORECASE))
        
        # Window/analytic functions
        window_funcs = len(re.findall(r'\b(row_number|rank|dense_rank|lag|lead|first_value|last_value|nth_value|ntile|percent_rank|cume_dist|ratio_to_report)\s*\(', code_no_comments, re.IGNORECASE))
        over_clause = len(re.findall(r'\bover\s*\(', code_no_comments, re.IGNORECASE))
        
        # Hierarchical queries (CONNECT BY)
        hierarchical = len(re.findall(r'\bconnect\s+by\b', code_no_comments, re.IGNORECASE))
        start_with = len(re.findall(r'\bstart\s+with\b', code_no_comments, re.IGNORECASE))
        
        # PIVOT/UNPIVOT
        pivot = len(re.findall(r'\b(pivot|unpivot)\b', code_no_comments, re.IGNORECASE))
        
        # Recursive CTEs
        recursive_cte = len(re.findall(r'\bwith\s+recursive\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: MODEL clause
        model_clause = len(re.findall(r'\bmodel\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Advanced analytics (ROLLUP, CUBE, GROUPING SETS)
        rollup = len(re.findall(r'\brollup\s*\(', code_no_comments, re.IGNORECASE))
        cube = len(re.findall(r'\bcube\s*\(', code_no_comments, re.IGNORECASE))
        grouping_sets = len(re.findall(r'\bgrouping\s+sets\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: JSON/XML functions
        json_funcs = len(re.findall(r'\bjson_(table|value|query|exists|object|array|arrayagg|objectagg)\b', code_no_comments, re.IGNORECASE))
        xml_funcs = len(re.findall(r'\bxml(type|query|table|agg|element|forest|parse|serialize|cast|root)\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic queries
        if cte > 0 or window_funcs > 0 or over_clause > 0 or hierarchical > 0:
            score = 2  # Medium: CTEs, window functions, hierarchical queries
        if cte > 2 or window_funcs > 3 or pivot > 0 or recursive_cte > 0 or (rollup > 0 or cube > 0) or json_funcs > 0:
            score = 3  # Complex: multiple CTEs, PIVOT, recursive, ROLLUP/CUBE, JSON
        if cte > 4 or window_funcs > 6 or model_clause > 0 or grouping_sets > 0 or (json_funcs > 2 and xml_funcs > 2):
            score = 4  # Very Complex: MODEL clause, GROUPING SETS, extensive JSON/XML
        
        self.analytics_depth = score

        # --- 4. SQL REPORTING LOGIC ---
        # Enhanced: SELECT complexity, unions, subqueries, result sets
        select_stmt = len(re.findall(r'\bselect\b', code_no_comments, re.IGNORECASE))
        
        # UNION operations
        unions = len(re.findall(r'\bunion\s+(all\s+)?', code_no_comments, re.IGNORECASE))
        
        # Subqueries
        subqueries = len(re.findall(r'\(\s*select\b', code_no_comments, re.IGNORECASE))
        
        # EXISTS/IN subqueries
        exists_in = len(re.findall(r'\b(exists|in)\s*\(\s*select\b', code_no_comments, re.IGNORECASE))
        
        # CASE expressions
        case_expr = len(re.findall(r'\bcase\s+when\b', code_no_comments, re.IGNORECASE))
        
        # Aggregate functions
        aggregates = len(re.findall(r'\b(count|sum|avg|min|max|stddev|variance|listagg|xmlagg)\s*\(', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: single SELECT
        if select_stmt > 2 or subqueries > 0 or case_expr > 0:
            score = 2  # Medium: multiple SELECTs, subqueries, CASE
        if select_stmt > 5 or unions > 0 or subqueries > 3 or exists_in > 1 or aggregates > 4:
            score = 3  # Complex: many SELECTs, UNIONs, EXISTS/IN, aggregates
        if select_stmt > 10 or unions > 3 or subqueries > 6 or (exists_in > 3 and aggregates > 8):
            score = 4  # Very Complex: extensive SELECT logic
        
        self.sql_reporting_logic = score

        # --- 5. TRANSFORMATION LOGIC ---
        # Enhanced: DML operations, MERGE, data conversions, string/date operations
        inserts = len(re.findall(r'\binsert\s+into\b', code_no_comments, re.IGNORECASE))
        updates = len(re.findall(r'\bupdate\s+\w+\s+set\b', code_no_comments, re.IGNORECASE))
        deletes = len(re.findall(r'\bdelete\s+from\b', code_no_comments, re.IGNORECASE))
        merge = len(re.findall(r'\bmerge\s+into\b', code_no_comments, re.IGNORECASE))
        
        # Data conversions
        conversions = len(re.findall(r'\b(to_char|to_number|to_date|cast|convert|to_timestamp|to_clob)\s*\(', code_no_comments, re.IGNORECASE))
        
        # String operations
        string_ops = len(re.findall(r'\b(substr|instr|replace|translate|trim|ltrim|rtrim|upper|lower|initcap|concat|regexp_replace|regexp_substr)\s*\(', code_no_comments, re.IGNORECASE))
        
        # Date operations
        date_funcs = len(re.findall(r'\b(sysdate|systimestamp|current_date|current_timestamp|add_months|months_between|trunc|extract|to_timestamp_tz)\s*\(', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Bulk operations
        bulk_collect = len(re.findall(r'\bbulk\s+collect\b', code_no_comments, re.IGNORECASE))
        forall = len(re.findall(r'\bforall\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic SELECT, no transformations
        if updates > 0 or inserts > 0 or conversions > 2 or date_funcs > 0:
            score = 2  # Medium: basic DML, conversions
        if merge > 0 or (updates > 2 and inserts > 2) or string_ops > 3 or bulk_collect > 0 or forall > 0:
            score = 3  # Complex: MERGE, bulk operations
        if merge > 1 or (updates > 5 and deletes > 2) or conversions > 10 or (bulk_collect > 1 and forall > 1):
            score = 4  # Very Complex: complex MERGE, extensive bulk operations
        
        self.transformation_logic = score

        # --- 6. UTILITY COMPLEXITY ---
        # Enhanced: procedures, functions, packages, parameters, collections, cursors
        # Parameters
        params = len(re.findall(r'\b(in|out|in\s+out)\s+\w+', code_no_comments, re.IGNORECASE))
        
        # Variables and declarations
        declares = len(re.findall(r'\b(declare|begin)\b', code_no_comments, re.IGNORECASE))
        
        # Control flow
        if_stmt = len(re.findall(r'\bif\b', code_no_comments, re.IGNORECASE))
        loop_stmt = len(re.findall(r'\b(loop|while|for)\b', code_no_comments, re.IGNORECASE))
        
        # Cursors
        cursors = len(re.findall(r'\bcursor\s+\w+\s+is\b', code_no_comments, re.IGNORECASE))
        open_cursor = len(re.findall(r'\bopen\s+\w+', code_no_comments, re.IGNORECASE))
        fetch_cursor = len(re.findall(r'\bfetch\s+\w+\s+into\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Collections (nested tables, varrays, associative arrays)
        collections = len(re.findall(r'\b(table\s+of|varray)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Pipelined table functions (already counted above)
        pipe_row = len(re.findall(r'\bpipe\s+row\b', code_no_comments, re.IGNORECASE))
        
        # Dynamic SQL
        execute_immediate = len(re.findall(r'\bexecute\s+immediate\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no procedures
        if params > 0 or declares > 2 or if_stmt > 1 or cursors > 0:
            score = 2  # Medium: parameters, control flow, cursors
        if params > 5 or loop_stmt > 0 or cursors > 1 or collections > 0 or pipe_row > 0:
            score = 3  # Complex: many params, loops, collections, pipelined functions
        if params > 10 or cursors > 2 or execute_immediate > 0 or (collections > 1 and pipe_row > 1):
            score = 4  # Very Complex: extensive parameters, dynamic SQL, advanced collections
        
        self.utility_complexity = score

        # --- 7. EXECUTION CONTROL ---
        # Enhanced: transactions, savepoints, autonomous transactions, pragma
        commit = len(re.findall(r'\bcommit\b', code_no_comments, re.IGNORECASE))
        rollback = len(re.findall(r'\brollback\b', code_no_comments, re.IGNORECASE))
        savepoint = len(re.findall(r'\bsavepoint\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Autonomous transactions
        autonomous = len(re.findall(r'\bpragma\s+autonomous_transaction\b', code_no_comments, re.IGNORECASE))
        
        # Locking
        lock_table = len(re.findall(r'\block\s+table\b', code_no_comments, re.IGNORECASE))
        for_update = len(re.findall(r'\bfor\s+update\b', code_no_comments, re.IGNORECASE))
        
        # SET TRANSACTION
        set_transaction = len(re.findall(r'\bset\s+transaction\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no explicit transactions
        if commit > 0 or rollback > 0 or for_update > 0:
            score = 2  # Medium: basic transactions
        if savepoint > 0 or lock_table > 0 or set_transaction > 0 or autonomous > 0:
            score = 3  # Complex: savepoints, locking, autonomous transactions
        if savepoint > 2 or autonomous > 1 or (commit > 3 and savepoint > 1):
            score = 4  # Very Complex: complex transaction patterns
        
        self.execution_control = score

        # --- 8. FILE I/O & EXTERNAL INTEGRATION ---
        # Enhanced: external tables, UTL_FILE, UTL_HTTP, DBLinks, Java stored procedures
        # External tables (already counted)
        
        # UTL packages
        utl_file = len(re.findall(r'\butl_file\b', code_no_comments, re.IGNORECASE))
        utl_http = len(re.findall(r'\butl_http\b', code_no_comments, re.IGNORECASE))
        utl_smtp = len(re.findall(r'\butl_smtp\b', code_no_comments, re.IGNORECASE))
        utl_mail = len(re.findall(r'\butl_mail\b', code_no_comments, re.IGNORECASE))
        
        # DBMS packages for external access
        dbms_scheduler = len(re.findall(r'\bdbms_scheduler\b', code_no_comments, re.IGNORECASE))
        dbms_pipe = len(re.findall(r'\bdbms_pipe\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Java stored procedures
        java_call = len(re.findall(r'\bas\s+language\s+java\b', code_no_comments, re.IGNORECASE))
        
        # TIER 3: External procedures (C/C++)
        external_proc = len(re.findall(r'\bas\s+language\s+c\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no external integration
        if utl_file > 0 or dbms_scheduler > 0 or external_tables > 0:
            score = 2  # Medium: file I/O, external tables
        if dblinks > 0 or utl_http > 0 or utl_smtp > 0 or java_call > 0 or dbms_pipe > 0:
            score = 3  # Complex: network calls, Java, pipes
        if (utl_file > 2 and dblinks > 1) or java_call > 1 or external_proc > 0 or (utl_http > 1 and utl_smtp > 1):
            score = 4  # Very Complex: extensive external integration
        
        self.file_io_external_integration = score

        # --- 9. ODS OUTPUT DELIVERY ---
        # Enhanced: result sets, ref cursors, pipelined functions, bulk collect
        # REF CURSORs
        ref_cursor = len(re.findall(r'\bsys_refcursor\b', code_no_comments, re.IGNORECASE))
        open_for = len(re.findall(r'\bopen\s+\w+\s+for\b', code_no_comments, re.IGNORECASE))
        
        # Pipelined functions (already counted)
        
        # Return statements
        returns = len(re.findall(r'\breturn\b', code_no_comments, re.IGNORECASE))
        
        # OUT parameters
        out_params = len(re.findall(r'\bout\s+\w+', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: single SELECT or no results
        if select_stmt > 1 or returns > 0 or out_params > 0:
            score = 2  # Medium: multiple SELECTs, returns, OUT params
        if select_stmt > 3 or ref_cursor > 0 or open_for > 0 or pipelined > 0:
            score = 3  # Complex: REF CURSORs, pipelined functions
        if ref_cursor > 2 or pipelined > 1 or (pipe_row > 3 and bulk_collect > 1):
            score = 4  # Very Complex: multiple REF CURSORs, advanced pipelined functions
        
        self.ods_output_delivery = score

        # --- 10. ERROR HANDLING & OPTIMIZATION ---
        # Enhanced: exception handling, hints, parallel execution, result cache
        # Exception handling
        exception_block = len(re.findall(r'\bexception\b', code_no_comments, re.IGNORECASE))
        raise_exception = len(re.findall(r'\braise\b', code_no_comments, re.IGNORECASE))
        when_others = len(re.findall(r'\bwhen\s+others\b', code_no_comments, re.IGNORECASE))
        
        # Custom exceptions
        pragma_exception = len(re.findall(r'\bpragma\s+exception_init\b', code_no_comments, re.IGNORECASE))
        
        # Hints
        hints = len(re.findall(r'/\*\+', code))  # Use original code to catch hints
        
        # TIER 2: Parallel execution
        parallel = len(re.findall(r'\bparallel\s*\(', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Result cache
        result_cache = len(re.findall(r'\bresult_cache\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Advanced hints (INDEX, FULL, USE_NL, USE_HASH, etc.)
        advanced_hints = len(re.findall(r'/\*\+.*\b(index|full|use_nl|use_hash|use_merge|leading|ordered|append|parallel)\b', code, re.IGNORECASE))
        
        # Performance monitoring
        dbms_profiler = len(re.findall(r'\bdbms_profiler\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no error handling
        if exception_block > 0 or hints > 0:
            score = 2  # Medium: basic exception handling, hints
        if exception_block > 1 or pragma_exception > 0 or parallel > 0 or advanced_hints > 2:
            score = 3  # Complex: multiple exceptions, parallel, advanced hints
        if exception_block > 3 or (pragma_exception > 1 and raise_exception > 2) or result_cache > 0 or parallel > 1:
            score = 4  # Very Complex: extensive error handling, result cache, parallel
        
        self.error_handling_optimization = score

        # --- CROSS-METRIC BONUSES ---
        # Boost certain metrics when advanced enterprise features are present
        
        # Pipelined functions indicate sophisticated design
        if pipelined > 0 or pipe_row > 1:
            self.script_size_structure = max(self.script_size_structure, 3)
            self.utility_complexity = max(self.utility_complexity, 3)
            self.ods_output_delivery = max(self.ods_output_delivery, 3)
        
        # Bulk operations indicate high-performance requirements
        if bulk_collect > 1 or forall > 1:
            self.transformation_logic = max(self.transformation_logic, 3)
            self.utility_complexity = max(self.utility_complexity, 2)
        
        # Advanced analytics indicate sophisticated reporting
        if model_clause > 0 or grouping_sets > 0:
            self.analytics_depth = max(self.analytics_depth, 4)
            self.sql_reporting_logic = max(self.sql_reporting_logic, 3)
        
        # Autonomous transactions indicate complex transaction patterns
        if autonomous > 0:
            self.execution_control = max(self.execution_control, 3)
            self.utility_complexity = max(self.utility_complexity, 2)
        
        # Java/external procedures indicate enterprise integration
        if java_call > 0 or external_proc > 0:
            self.file_io_external_integration = max(self.file_io_external_integration, 3)
            self.script_size_structure = max(self.script_size_structure, 3)

        # --- CYCLOMATIC COMPLEXITY ---
        self.cyclomatic = self._calculate_cyclomatic_complexity(code_no_comments)

    def _remove_comments(self, code: str) -> str:
        """Remove SQL comments (-- and /* */) from code."""
        # Remove multi-line comments /* */
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        # Remove single-line comments --
        code = re.sub(r'--.*?$', '', code, flags=re.MULTILINE)
        
        return code


    def _get_nesting_level(self, code: str) -> int:
        """
        Calculate the maximum nesting depth of control structures in Oracle PL/SQL code.
        """
        stack = []
        max_depth = 0

        # Regex patterns for opening and closing structures
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
        Calculate cyclomatic complexity for Oracle PL/SQL.
        
        Counts decision points: IF, ELSIF, LOOP, WHILE, FOR, CASE WHEN, EXCEPTION handlers
        Cyclomatic Complexity = decision points + 1
        """
        if_count = len(re.findall(r'\bif\b', code, re.IGNORECASE))
        elsif_count = len(re.findall(r'\belsif\b', code, re.IGNORECASE))
        loop_count = len(re.findall(r'\b(loop|while|for)\b', code, re.IGNORECASE))
        case_when = len(re.findall(r'\bwhen\b', code, re.IGNORECASE))
        exception_when = len(re.findall(r'\bexception\s+when\b', code, re.IGNORECASE))
        decision_points = if_count + elsif_count + loop_count + case_when + exception_when

        return max(1, decision_points + 1)
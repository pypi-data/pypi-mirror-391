# src/code_analyzer/analyzers/sybase_analyzer.py
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


class SybaseAnalyzer(AnalyzerBase):
    """
    Sybase code complexity analyzer with enterprise metrics integration.
    
    Evaluates Sybase scripts across 10 dimensions, each scored 1-4:
    - 1: Simple
    - 2: Medium
    - 3: Complex
    - 4: Very Complex
    
    Uses hybrid approach:
    - Config weights override registry defaults
    - Enterprise validation via metrics module
    - Standardized 0-100 scoring system
    """
    language = "sybase"
    
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
        """Analyze Sybase source code and return complexity metrics."""
        include_cyclomatic = self.config.get("include_cyclomatic", False)
        
        # If code is None or empty, try to read from file path
        if not code and path and path != "<string>":
            file_content = read_file_if_exists(path)
            if file_content:
                code = file_content
        
        # Run complexity analysis
        analyzer = SybaseComplexity()
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
    
    
# Enterprise-grade Sybase T-SQL complexity analyzer
class SybaseComplexity:
    """
    Enterprise-grade Sybase T-SQL complexity analyzer with comprehensive pattern detection.
    Each metric is scored 1 (Simple) to 4 (Very Complex) based on Sybase-specific patterns.
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

    def analyze(self, code: str):
        """
        Analyze Sybase T-SQL code and compute all complexity metrics.
        Enhanced with comprehensive Sybase ASE 16.0+ feature detection.
        """
        if not code or not code.strip():
            return
        
        # Remove comments for accurate analysis
        code_no_comments = self._remove_comments(code)
        lines = [ln for ln in code_no_comments.splitlines() if ln.strip()]
        num_lines = len(lines)
        
        # Calculate nesting depth
        nesting_level = self._get_nesting_level(code_no_comments)
        
        # Count fundamental constructs
        procedures = len(re.findall(r'\bcreate\s+(proc|procedure)\b', code_no_comments, re.IGNORECASE))
        functions = len(re.findall(r'\bcreate\s+function\b', code_no_comments, re.IGNORECASE))
        triggers = len(re.findall(r'\bcreate\s+trigger\b', code_no_comments, re.IGNORECASE))
        batches = len(re.findall(r'\bgo\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Table-Valued Functions (inline & multi-statement)
        tvf_inline = len(re.findall(r'\bcreate\s+function\s+\w+.*returns\s+table\b', code_no_comments, re.IGNORECASE | re.DOTALL))
        tvf_multi = len(re.findall(r'\breturns\s+@\w+\s+table\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: ALTER statements (DDL complexity)
        alter_table = len(re.findall(r'\balter\s+table\b', code_no_comments, re.IGNORECASE))
        alter_proc = len(re.findall(r'\balter\s+(proc|procedure|function|view)\b', code_no_comments, re.IGNORECASE))
        alter_db = len(re.findall(r'\balter\s+database\b', code_no_comments, re.IGNORECASE))
        alter_index = len(re.findall(r'\balter\s+index\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: SEQUENCES (ASE 15.7+)
        sequences = len(re.findall(r'\bcreate\s+sequence\b', code_no_comments, re.IGNORECASE))
        next_value = len(re.findall(r'\bnext\s+value\s+for\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Materialized Views
        materialized_views = len(re.findall(r'\bcreate\s+materialized\s+view\b', code_no_comments, re.IGNORECASE))
        # (columnstore detection moved later to error handling section)
        
        # TIER 2: Table Partitioning
        partitions = len(re.findall(r'\bpartition\s+by\s+(range|hash|list)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Java in Database (SQLJ)
        java_funcs = len(re.findall(r'\blanguage\s+java\b', code_no_comments, re.IGNORECASE))
        external_name = len(re.findall(r'\bexternal\s+name\b', code_no_comments, re.IGNORECASE))
        
        # TIER 3: In-Memory Databases (IMDB)
        inmemory_db = len(re.findall(r'\bon\s+inmemory_cache\b', code_no_comments, re.IGNORECASE))
        
        # DDL Triggers (ASE 15.0.2+)
        ddl_triggers = len(re.findall(r'\bfor\s+ddl_\w+_events\b', code_no_comments, re.IGNORECASE))
        
        # --- 1. SCRIPT SIZE & STRUCTURE ---
        # Enhanced: lines, procedures, functions, triggers, TVFs, ALTER statements, batches, nesting, sequences
        score = 1  # Simple: <100 lines, 0-1 proc, no nesting
        if num_lines > 100 or procedures > 1 or functions > 1 or batches > 3 or tvf_inline > 0 or alter_proc > 0:
            score = 2  # Medium: 100-500 lines, 2-3 procs, TVFs, ALTER procedures
        if num_lines > 500 or procedures > 3 or functions > 2 or triggers > 0 or nesting_level > 2 or alter_table > 0 or tvf_multi > 0 or materialized_views > 0:
            score = 3  # Complex: 500-2000 lines, 4-6 procs, triggers, ALTER statements, multi-statement TVFs, materialized views
        if num_lines > 2000 or procedures > 6 or functions > 4 or triggers > 2 or nesting_level > 4 or alter_db > 0 or sequences > 0 or ddl_triggers > 0 or java_funcs > 0 or inmemory_db > 0 or (functions >= 1 and java_funcs > 0):
            score = 4  # Very Complex: >2000 lines, >6 procs, deep nesting, ALTER DATABASE, sequences, DDL triggers, Java UDFs, IMDB
        
        self.script_size_structure = score

        # --- 2. DEPENDENCY FOOTPRINT ---
        # Enhanced: databases, schemas, tables, views, external connections, proxy tables, IMDB
        use_database = len(re.findall(r'\buse\s+\w+', code_no_comments, re.IGNORECASE))
        table_refs = len(re.findall(r'\bfrom\s+[\w\.]+|\bjoin\s+[\w\.]+|\binto\s+[\w\.]+', code_no_comments, re.IGNORECASE))
        
        # Views and temp tables
        views = len(re.findall(r'\bcreate\s+view\b', code_no_comments, re.IGNORECASE))
        temp_tables = len(re.findall(r'#\w+|##\w+', code_no_comments))
        
        # TIER 1: Table Variables
        table_vars = len(re.findall(r'\bdeclare\s+@\w+\s+table\b', code_no_comments, re.IGNORECASE))
        
        # External servers and linked servers
        remote_servers = len(re.findall(r'\bsp_addserver|\bsp_addlinkedserver|\bexec\s+\w+\.\.\w+', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Proxy Tables (Sybase ASE specific)
        proxy_tables = len(re.findall(r'\bcreate\s+existing\s+table\s+\w+\s+at\b', code_no_comments, re.IGNORECASE))
        remote_procs = len(re.findall(r'\bexec\s+\w+\.\w+\.\w+\.\w+', code_no_comments, re.IGNORECASE))
        
        # Cross-database queries
        cross_db = len(re.findall(r'\w+\.\.\w+\.\w+|\w+\.\w+\.\w+\.\w+', code_no_comments))
        
        # TIER 3: In-Memory Database references
        imdb_refs = inmemory_db
        
        score = 1  # Simple: 0-1 database, 0-3 table refs
        if use_database >= 1 or table_refs > 3 or temp_tables > 0 or table_vars > 0:
            score = 2  # Medium: 1-2 databases, 4-10 tables, temp tables, table variables
        if use_database > 2 or table_refs > 10 or views > 0 or cross_db > 0 or materialized_views > 0 or table_vars >= 1:
            score = 3  # Complex: >2 databases, >10 tables, views, cross-db, materialized views, table variables
        if remote_servers > 0 or cross_db > 5 or table_refs > 20 or proxy_tables > 0 or imdb_refs > 0 or (table_vars > 0 and views > 0):
            score = 4  # Very Complex: remote servers, proxy tables, IMDB, many cross-db queries, combined table vars & views
        
        self.dependency_footprint = score

        # --- 3. ANALYTICS DEPTH ---
        # Enhanced: aggregations, window functions, statistical operations, analytical queries, XML, full-text
        basic_agg = len(re.findall(r'\b(count|sum|avg|min|max|group\s+by)\b', code_no_comments, re.IGNORECASE))
        
        # Advanced aggregations
        advanced_agg = len(re.findall(r'\b(stddev|variance|median|percentile|ntile)\b', code_no_comments, re.IGNORECASE))
        
        # Window functions
        window_funcs = len(re.findall(r'\b(row_number|rank|dense_rank|lead|lag|first_value|last_value|over\s*\()\b', code_no_comments, re.IGNORECASE))
        
        # Pivoting and unpivoting
        pivot_ops = len(re.findall(r'\b(pivot|unpivot)\b', code_no_comments, re.IGNORECASE))
        
        # CTEs and complex subqueries
        cte = len(re.findall(r'\bwith\s+\w+\s+as\s*\(', code_no_comments, re.IGNORECASE))
        subqueries = len(re.findall(r'\(\s*select\s+', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Recursive CTEs
        recursive_cte = len(re.findall(r'\bwith\s+recursive\s+\w+', code_no_comments, re.IGNORECASE))
        
        # TIER 1: XML Processing (ASE 15.7+)
        for_xml = len(re.findall(r'\bfor\s+xml\s+(path|raw|auto|explicit)\b', code_no_comments, re.IGNORECASE))
        xml_methods = len(re.findall(r'\.(query|value|exist|nodes|modify)\s*\(', code_no_comments, re.IGNORECASE))
        openxml = len(re.findall(r'\bopenxml\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Full-Text Search
        fulltext = len(re.findall(r'\b(contains|freetext|containstable|freetexttable)\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic SELECT, no aggregations
        if basic_agg > 0 or cte > 0:
            score = 2  # Medium: GROUP BY, COUNT, SUM, basic CTEs
        if window_funcs > 0 or advanced_agg > 0 or pivot_ops > 0 or subqueries > 2 or for_xml > 0 or fulltext > 0:
            score = 3  # Complex: window functions, pivots, nested subqueries, XML, full-text
        if window_funcs > 3 or pivot_ops > 1 or (cte > 2 and subqueries > 3) or recursive_cte > 0 or xml_methods > 2 or fulltext > 2:
            score = 4  # Very Complex: heavy analytical processing, recursive CTEs, XML methods, advanced full-text
        
        self.analytics_depth = score

        # --- 4. SQL & REPORTING LOGIC (was: QUERY & REPORTING LOGIC) ---
        # Enhanced: query complexity, joins, unions, result sets, computed columns
        joins = len(re.findall(r'\b(inner\s+join|left\s+join|right\s+join|full\s+join|cross\s+join|join)\b', code_no_comments, re.IGNORECASE))
        unions = len(re.findall(r'\bunion\s+(all\s+)?', code_no_comments, re.IGNORECASE))
        
        # Query optimization hints
        hints = len(re.findall(r'\b(index|nolock|readpast|rowlock|paglock|tablock|holdlock|updlock)\b', code_no_comments, re.IGNORECASE))
        
        # Complex WHERE clauses
        complex_where = len(re.findall(r'\bwhere\s+.*\b(and|or)\b.*\b(and|or)\b', code_no_comments, re.IGNORECASE))
        
        # CASE statements
        case_stmt = len(re.findall(r'\bcase\s+when\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Computed Columns
        computed_cols = len(re.findall(r'\badd\s+\w+\s+as\s+\(', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic SELECT, no joins
        if joins >= 1 or case_stmt > 0 or unions > 0:
            score = 2  # Medium: 1-3 joins, CASE statements
        if joins > 3 or unions > 1 or hints > 0 or complex_where > 0 or computed_cols > 0:
            score = 3  # Complex: >3 joins, unions, query hints, computed columns
        if joins > 6 or unions > 3 or hints > 3 or complex_where > 3 or computed_cols > 2:
            score = 4  # Very Complex: many joins/unions, extensive optimization, multiple computed columns
        
        self.sql_reporting_logic = score

        # --- 5. TRANSFORMATION LOGIC ---
        # Enhanced: data manipulation, conversions, string operations, date functions
        updates = len(re.findall(r'\bupdate\s+\w+', code_no_comments, re.IGNORECASE))
        inserts = len(re.findall(r'\binsert\s+into\b', code_no_comments, re.IGNORECASE))
        deletes = len(re.findall(r'\bdelete\s+from\b', code_no_comments, re.IGNORECASE))
        
        # Data type conversions
        conversions = len(re.findall(r'\b(convert|cast|str|isnull|coalesce|nullif)\b', code_no_comments, re.IGNORECASE))
        
        # String operations - Enhanced with TIER 2 functions
        string_ops = len(re.findall(r'\b(substring|charindex|patindex|stuff|replace|ltrim|rtrim|upper|lower|reverse|replicate|space|ascii|char|quotename|string_split|soundex|difference|concat|format)\b', code_no_comments, re.IGNORECASE))
        
        # Date/time functions - Enhanced with TIER 2 functions
        date_funcs = len(re.findall(r'\b(getdate|dateadd|datediff|datepart|datename|day|month|year|sysdatetime|sysutcdatetime|datefromparts|timefromparts|datetimefromparts|eomonth|datetrunc)\b', code_no_comments, re.IGNORECASE))
        
        # Timezone conversion (TIER 2)
        timezone = len(re.findall(r'\bat\s+time\s+zone\b', code_no_comments, re.IGNORECASE))
        
        # Merge statements
        merge = len(re.findall(r'\bmerge\s+', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic SELECT, no transformations
        if updates > 0 or inserts > 0 or conversions > 2 or date_funcs > 0:
            score = 2  # Medium: basic DML, conversions, date functions
        if merge > 0 or (updates > 2 and inserts > 2) or string_ops > 3 or date_funcs > 3 or timezone > 0:
            score = 3  # Complex: MERGE, multiple DML, extensive transformations, timezone
        if merge > 1 or (updates > 5 and deletes > 2) or conversions > 10 or string_ops > 8 or date_funcs > 8:
            score = 4  # Very Complex: complex MERGE, heavy DML operations, extensive string/date operations
        
        self.transformation_logic = score

        # --- 6. UTILITY COMPLEXITY (was: STORED PROCEDURE COMPLEXITY) ---
        # Enhanced: parameters, variables, control flow, nested calls, advanced cursors, TVFs, table vars
        # Enhanced data types (TIER 1) - split for regex complexity
        basic_types = r'int|varchar|char|datetime|decimal|money|bit'
        lob_types = r'text|image|ntext|xml'
        numeric_types = r'numeric|smallmoney|real|float'
        binary_types = r'binary|varbinary|timestamp|uniqueidentifier'
        special_types = r'nchar|nvarchar|java'
        all_types = f'{basic_types}|{lob_types}|{numeric_types}|{binary_types}|{special_types}'
        params = len(re.findall(rf'@\w+\s+({all_types})\b', code_no_comments, re.IGNORECASE))
        
        # Variables and declarations
        declares = len(re.findall(r'\bdeclare\s+@\w+', code_no_comments, re.IGNORECASE))
        
        # Control flow
        if_stmt = len(re.findall(r'\bif\b', code_no_comments, re.IGNORECASE))
        while_loop = len(re.findall(r'\bwhile\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Advanced Cursors - Enhanced detection
        cursors = len(re.findall(r'\bdeclare\s+\w+\s+cursor\b', code_no_comments, re.IGNORECASE))
        cursor_advanced = len(re.findall(r'\b(fast_forward|scroll|dynamic|static|keyset)\s+cursor\b', code_no_comments, re.IGNORECASE))
        fetch_status = len(re.findall(r'@@fetch_status', code_no_comments, re.IGNORECASE))
        cursor_vars = len(re.findall(r'\bdeclare\s+@\w+\s+cursor\b', code_no_comments, re.IGNORECASE))
        
        # Nested procedure calls
        exec_calls = len(re.findall(r'\bexec(ute)?\s+\w+', code_no_comments, re.IGNORECASE))
        
        # Dynamic SQL
        dynamic_sql = len(re.findall(r'\bsp_executesql|execute\s*\(|exec\s*\(', code_no_comments, re.IGNORECASE))
        
        # TIER 2: WAITFOR timing
        waitfor = len(re.findall(r'\bwaitfor\s+(delay|time)\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no procedures or simple procedures
        if params > 0 or declares > 2 or if_stmt > 1 or exec_calls > 0:
            score = 2  # Medium: procedures with params, basic control flow
        if params > 5 or while_loop > 0 or cursors > 0 or exec_calls > 3 or cursor_advanced > 0 or waitfor > 0 or cursor_vars > 0:
            score = 3  # Complex: many params, loops, cursors, advanced cursor types, WAITFOR, cursor variables
        if cursors > 1 or dynamic_sql > 0 or (params > 10 and while_loop > 2) or (cursor_advanced > 0 and fetch_status > 0) or cursor_vars > 0:
            score = 4  # Very Complex: multiple cursors, dynamic SQL, advanced cursors with fetch checking, cursor variables
        
        self.utility_complexity = score  # Was: procedure_complexity
        
        # Cross-metric bonus: Advanced cursor patterns indicate overall complexity
        if cursor_advanced > 0 or cursor_vars > 0 or fetch_status > 2:
            # Advanced cursors require sophisticated script structure
            self.script_size_structure = max(self.script_size_structure, 3)
            # Complex cursors often transform data
            self.transformation_logic = max(self.transformation_logic, 2)
            # Cursors involve complex query/reporting logic
            self.sql_reporting_logic = max(self.sql_reporting_logic, 2)
            # Cursor operations typically involve multiple table dependencies
            self.dependency_footprint = max(self.dependency_footprint, 2)
            # Cursor error handling is critical
            self.error_handling_optimization = max(self.error_handling_optimization, 2)

        # --- 7. EXECUTION CONTROL (was: TRANSACTION CONTROL) ---
        # Enhanced: transactions, isolation levels, locks, savepoints, deadlock handling
        begin_tran = len(re.findall(r'\bbegin\s+tran(saction)?\b', code_no_comments, re.IGNORECASE))
        commit = len(re.findall(r'\bcommit\s+tran(saction)?\b', code_no_comments, re.IGNORECASE))
        rollback = len(re.findall(r'\brollback\s+tran(saction)?\b', code_no_comments, re.IGNORECASE))
        
        # Savepoints
        savepoints = len(re.findall(r'\bsave\s+tran(saction)?\b', code_no_comments, re.IGNORECASE))
        
        # Isolation levels
        isolation = len(re.findall(r'\bset\s+transaction\s+isolation\s+level\b', code_no_comments, re.IGNORECASE))
        
        # Locking hints
        locks = len(re.findall(r'\b(holdlock|updlock|xlock|rowlock|paglock|tablock|tablockx)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Advanced SET options
        set_identity = len(re.findall(r'\bset\s+identity_insert\b', code_no_comments, re.IGNORECASE))
        set_lock_timeout = len(re.findall(r'\bset\s+lock_timeout\b', code_no_comments, re.IGNORECASE))
        set_deadlock_priority = len(re.findall(r'\bset\s+deadlock_priority\b', code_no_comments, re.IGNORECASE))
        set_ansi = len(re.findall(r'\bset\s+(ansi_nulls|quoted_identifier|context_info)\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no explicit transactions
        if begin_tran > 0 or commit > 0 or set_identity > 0:
            score = 2  # Medium: basic transactions, identity insert
        if rollback > 0 or savepoints > 0 or locks > 0 or set_ansi > 0:
            score = 3  # Complex: rollbacks, savepoints, locking, ANSI settings
        if isolation > 0 or savepoints > 2 or (begin_tran > 3 and rollback > 2) or set_deadlock_priority > 0:
            score = 4  # Very Complex: custom isolation, nested transactions, deadlock priority
        
        self.execution_control = score  # Was: transaction_control

        # --- 8. FILE I/O & EXTERNAL INTEGRATION (was: EXTERNAL INTEGRATION) ---
        # Enhanced: linked servers, external procedures, file operations, system calls, Service Broker
        linked_server = len(re.findall(r'\bsp_addlinkedserver|\bexec\s+\w+\.\.\w+', code_no_comments, re.IGNORECASE))
        
        # System stored procedures
        system_procs = len(re.findall(r'\bsp_\w+|\bxp_\w+', code_no_comments, re.IGNORECASE))
        
        # File operations
        file_ops = len(re.findall(r'\bbulk\s+insert|\bopenrowset|\bopendatasource', code_no_comments, re.IGNORECASE))
        
        # Email and external notifications
        email = len(re.findall(r'\bsp_send_dbmail|\bxp_sendmail', code_no_comments, re.IGNORECASE))
        
        # Command shell
        cmd_shell = len(re.findall(r'\bxp_cmdshell', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Service Broker / Messaging (if applicable to Sybase ASE 16+)
        service_broker = len(re.findall(r'\b(begin\s+conversation|send\s+on\s+conversation|end\s+conversation|receive)\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no external integration
        if system_procs > 0 or file_ops > 0:
            score = 2  # Medium: basic system procs, bulk operations
        if linked_server > 0 or email > 0 or file_ops > 1 or proxy_tables > 0 or remote_procs > 0:
            score = 3  # Complex: linked servers, email, multiple file ops, proxy tables
        if cmd_shell > 0 or linked_server > 2 or (file_ops > 2 and email > 0) or service_broker > 0:
            score = 4  # Very Complex: shell commands, extensive external integration, Service Broker
        
        self.file_io_external_integration = score  # Was: external_integration

        # --- 9. ODS OUTPUT DELIVERY (was: RESULT SET DELIVERY) ---
        # Enhanced: multiple result sets, output parameters, return codes, temp tables, table variables
        select_stmt = len(re.findall(r'\bselect\b', code_no_comments, re.IGNORECASE))
        
        # Output parameters
        output_params = len(re.findall(r'@\w+\s+output', code_no_comments, re.IGNORECASE))
        
        # Return statements
        returns = len(re.findall(r'\breturn\b', code_no_comments, re.IGNORECASE))
        
        # Temp tables for result staging
        temp_result_tables = len(re.findall(r'#\w+', code_no_comments))
        
        # Result set manipulation
        result_sets = len(re.findall(r'\binsert\s+into\s+#|\bselect\s+.*\binto\s+#', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Table variables (already counted above)
        table_var_usage = table_vars
        
        score = 1  # Simple: single SELECT or no results
        if select_stmt > 1 or output_params > 0 or returns > 0:
            score = 2  # Medium: multiple SELECTs, output params
        if select_stmt > 3 or temp_result_tables > 2 or result_sets > 0 or table_var_usage > 0:
            score = 3  # Complex: >3 result sets, temp table staging, table variables
        if select_stmt > 6 or (temp_result_tables > 4 and result_sets > 3) or table_var_usage > 2:
            score = 4  # Very Complex: many result sets, complex staging with table variables
        
        self.ods_output_delivery = score  # Was: result_delivery

        # --- 10. ERROR HANDLING & OPTIMIZATION ---
        # Enhanced: error handling, performance optimization, indexing, security
        try_catch = len(re.findall(r'\bbegin\s+try\b', code_no_comments, re.IGNORECASE))
        raiserror = len(re.findall(r'\braise(r)?error\b', code_no_comments, re.IGNORECASE))
        
        # Error checking
        error_check = len(re.findall(r'@@error|@@rowcount|if\s+@error', code_no_comments, re.IGNORECASE))
        
        # Performance optimization
        set_opts = len(re.findall(r'\bset\s+(nocount|rowcount|statistics|showplan)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Advanced Indexing - Enhanced detection
        basic_indexes = len(re.findall(r'\bcreate\s+index\b', code_no_comments, re.IGNORECASE))
        unique_indexes = len(re.findall(r'\bcreate\s+unique\s+(clustered|nonclustered)?\s*index\b', code_no_comments, re.IGNORECASE))
        columnstore = len(re.findall(r'\bcolumnstore\s+index\b', code_no_comments, re.IGNORECASE))  # ASE 16.0+
        filtered_index = len(re.findall(r'\bcreate\s+index\s+.*\bwhere\b', code_no_comments, re.IGNORECASE))
        include_cols = len(re.findall(r'\binclude\s*\(', code_no_comments, re.IGNORECASE))
        index_opts = len(re.findall(r'\b(fillfactor|pad_index|allow_row_locks|allow_page_locks)\b', code_no_comments, re.IGNORECASE))
        
        # Statistics
        stats = len(re.findall(r'\bupdate\s+statistics|\bcreate\s+statistics', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Security & Encryption
        grants = len(re.findall(r'\b(grant|revoke|deny)\b', code_no_comments, re.IGNORECASE))
        encryption = len(re.findall(r'\b(encrypt|decrypt)\s+with\s+password\b', code_no_comments, re.IGNORECASE))
        with_encryption = len(re.findall(r'\bwith\s+encryption\b', code_no_comments, re.IGNORECASE))
        security_policy = len(re.findall(r'\bcreate\s+security\s+policy\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Full-Text Index
        fulltext_index = len(re.findall(r'\bcreate\s+fulltext\s+index\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Schema-Bound objects
        schemabinding = len(re.findall(r'\bwith\s+schemabinding\b', code_no_comments, re.IGNORECASE))
        
        total_indexes = basic_indexes + unique_indexes + columnstore + filtered_index + fulltext_index
        
        score = 1  # Simple: no error handling or optimization
        if raiserror > 0 or error_check > 0 or set_opts > 0:
            score = 2  # Medium: basic error checking, SET NOCOUNT
        if try_catch > 0 or total_indexes > 0 or error_check > 3 or grants > 0 or schemabinding > 0 or with_encryption > 0:
            score = 3
        if try_catch > 2 or stats > 0 or (total_indexes > 2 and error_check > 5) or encryption > 0 or columnstore > 0 or security_policy > 0 or (grants > 2 and with_encryption > 0):
            score = 4  # Very Complex: comprehensive error handling, statistics, encryption, columnstore, row-level security, multiple security features
        
        self.error_handling_optimization = score
        
        # Cross-metric bonus: Security/encryption indicates enterprise-grade complexity
        if grants > 1 or encryption > 0 or with_encryption > 0 or security_policy > 0:
            # Security features require sophisticated script structure
            self.script_size_structure = max(self.script_size_structure, 3)
            # Often involves stored procedures
            self.utility_complexity = max(self.utility_complexity, 2)
            # May use transactions for security operations
            self.execution_control = max(self.execution_control, 2)

        # --- CROSS-METRIC BONUSES ---
        # Boost certain metrics when advanced enterprise features are present
        try:
            # escalate utility_complexity for advanced cursor usages
            if 'cursor_advanced' in locals() and (cursor_advanced > 0 or cursor_vars > 0 or fetch_status > 0):
                self.utility_complexity = max(self.utility_complexity, 4)

            # if columnstore, materialized views, sequences, Java UDFs, proxy tables or IMDB are present, raise script size
            if (('columnstore' in locals() and columnstore > 0) or materialized_views > 0 or sequences > 0 or ('java_funcs' in locals() and java_funcs > 0) or ('security_policy' in locals() and security_policy > 0) or ('with_encryption' in locals() and with_encryption > 0) or proxy_tables > 0 or imdb_refs > 0):
                self.script_size_structure = min(4, self.script_size_structure + 1)

            # Java functions imply external dependencies
            if 'java_funcs' in locals() and java_funcs > 0:
                self.dependency_footprint = max(self.dependency_footprint, 3)

            # Advanced indexing should guarantee high optimization complexity
            if (('columnstore' in locals() and columnstore > 0) or ('unique_indexes' in locals() and unique_indexes > 0) or ('filtered_index' in locals() and filtered_index > 0)):
                self.error_handling_optimization = max(self.error_handling_optimization, 4)
        except NameError:
            # Defensive: if some local vars are missing, ignore bonus application
            pass

        # --- CYCLOMATIC COMPLEXITY ---
        self.cyclomatic = self._calculate_cyclomatic_complexity(code_no_comments)

    def _remove_comments(self, code: str) -> str:
        """Remove T-SQL comments from code for accurate analysis."""
        # Remove block comments /* ... */
        code_no_block = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        
        # Remove single-line comments --
        code_no_single = re.sub(r'--.*$', '', code_no_block, flags=re.MULTILINE)
        
        return code_no_single

    def _get_nesting_level(self, code: str) -> int:
        """Calculate maximum nesting depth of control structures."""
        stack = []
        max_depth = 0
        
        for line in code.splitlines():
            # Opening keywords
            if re.search(r'\b(BEGIN|IF|WHILE|CASE)\b', line, re.IGNORECASE):
                stack.append(1)
                max_depth = max(max_depth, len(stack))
            
            # Closing keywords
            if re.search(r'\bEND\b', line, re.IGNORECASE) and stack:
                stack.pop()
        
        return max_depth

    def _calculate_cyclomatic_complexity(self, code: str) -> int:
        """Calculate cyclomatic complexity (McCabe metric)."""
        branches = 0
        
        # Conditional statements
        branches += len(re.findall(r'\bif\b', code, re.IGNORECASE))
        branches += len(re.findall(r'\belse\s+if\b', code, re.IGNORECASE))
        
        # CASE statements
        branches += len(re.findall(r'\bcase\s+when\b', code, re.IGNORECASE))
        
        # Loops
        branches += len(re.findall(r'\bwhile\b', code, re.IGNORECASE))
        
        # Logical operators (AND/OR add complexity)
        branches += len(re.findall(r'\b(and|or)\b', code, re.IGNORECASE))
        
        # McCabe formula: E - N + 2P (simplified: branches + 1)
        return branches + 1 if branches > 0 else 1

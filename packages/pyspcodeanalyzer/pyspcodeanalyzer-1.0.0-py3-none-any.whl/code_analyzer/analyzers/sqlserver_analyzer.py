# src/code_analyzer/analyzers/sqlserver_analyzer.py
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


class SQLServerAnalyzer(AnalyzerBase):
    """
    SQLServer code complexity analyzer with enterprise metrics integration.
    
    Evaluates SQLServer scripts across 10 dimensions, each scored 1-4:
    - 1: Simple
    - 2: Medium
    - 3: Complex
    - 4: Very Complex
    
    Uses hybrid approach:
    - Config weights override registry defaults
    - Enterprise validation via metrics module
    - Standardized 0-100 scoring system
    """
    language = "sqlserver"
    
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
        """Analyze SQLServer source code and return complexity metrics."""
        include_cyclomatic = self.config.get("include_cyclomatic", False)
        
        # If code is None or empty, try to read from file path
        if not code and path and path != "<string>":
            file_content = read_file_if_exists(path)
            if file_content:
                code = file_content
        
        # Run complexity analysis
        analyzer = SQLServerComplexity()
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
    

class SQLServerComplexity:
    """
    Enterprise-grade SQLServer T-SQL complexity analyzer with comprehensive pattern detection.
    Each metric is scored 1 (Simple) to 4 (Very Complex) based on SQLServer-specific patterns.
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
        Analyze SQLServer T-SQL source code and return complexity metrics.
        """
        if not code or not code.strip():
            return
        
        # Remove comments for accurate analysis
        code_no_comments = self._remove_comments(code)

        
        # --- 1. SCRIPT SIZE & STRUCTURE ---
        # Enhanced: lines, procedures, functions, triggers, user-defined types, assemblies
        lines = len([line for line in code.split('\n') if line.strip()])
        
        # T-SQL objects
        procedures = len(re.findall(r'\bcreate\s+(or\s+alter\s+)?proc(edure)?\b', code_no_comments, re.IGNORECASE))
        functions = len(re.findall(r'\bcreate\s+(or\s+alter\s+)?function\b', code_no_comments, re.IGNORECASE))
        triggers = len(re.findall(r'\bcreate\s+(or\s+alter\s+)?trigger\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Table-Valued Functions (inline & multi-statement)
        tvf_inline = len(re.findall(r'\breturns\s+table\s*as\s*return\b', code_no_comments, re.IGNORECASE))
        tvf_multi = len(re.findall(r'\breturns\s+@\w+\s+table\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: User-Defined Types (SQL Server specific)
        user_types = len(re.findall(r'\bcreate\s+type\b', code_no_comments, re.IGNORECASE))
        table_types = len(re.findall(r'\bcreate\s+type\s+\w+\s+as\s+table\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: CLR objects (SQL Server specific)
        clr_assemblies = len(re.findall(r'\bcreate\s+assembly\b', code_no_comments, re.IGNORECASE))
        clr_functions = len(re.findall(r'\bexternal\s+name\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Service Broker (SQL Server specific)
        service_broker = len(re.findall(r'\b(begin\s+conversation|send\s+on\s+conversation|end\s+conversation|receive)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Machine Learning Services (SQL Server 2017+)
        ml_services = len(re.findall(r'\bsp_execute_external_script\b', code_no_comments, re.IGNORECASE))
        
        # Calculate nesting depth
        nesting_level = self._get_nesting_level(code_no_comments)
        
        score = 1  # Simple: small script
        if lines > 100 or procedures > 0 or functions > 0 or nesting_level > 1:
            score = 2  # Medium: moderate size, procedures, or basic nesting
        if lines > 500 or (procedures + functions) > 3 or triggers > 0 or tvf_multi > 0 or user_types > 0 or nesting_level > 3:
            score = 3  # Complex: large, multiple objects, TVF, user types, or deep nesting
        if lines > 2000 or (procedures + functions + triggers) > 8 or clr_assemblies > 0 or service_broker > 0 or ml_services > 0 or nesting_level > 5:
            score = 4  # Very Complex: very large, CLR, Service Broker, ML Services, or very deep nesting
        
        self.script_size_structure = score

        # --- 2. DEPENDENCY FOOTPRINT ---
        # Enhanced: databases, schemas, tables, views, linked servers, synonyms, external data sources
        use_database = len(re.findall(r'\buse\s+\[?\w+\]?\b', code_no_comments, re.IGNORECASE))
        tables = len(re.findall(r'\bfrom\s+(\[?\w+\]?\.)?(\[?\w+\]?\.)?(\[?\w+\]?)', code_no_comments, re.IGNORECASE))
        
        # Views and temp tables
        views = len(re.findall(r'\bcreate\s+(or\s+alter\s+)?view\b', code_no_comments, re.IGNORECASE))
        temp_tables = len(re.findall(r'#\w+|##\w+', code_no_comments))
        
        # TIER 1: Table Variables (SQL Server specific)
        table_vars = len(re.findall(r'\bdeclare\s+@\w+\s+table\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Common Table Expressions
        cte_count = len(re.findall(r'\bwith\s+\w+\s*\([^)]*\)\s*as\s*\(', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Linked Servers and External Data Sources
        linked_servers = len(re.findall(r'\bsp_addlinkedserver|\b\w+\.\w+\.\w+\.\w+', code_no_comments, re.IGNORECASE))
        external_sources = len(re.findall(r'\bcreate\s+external\s+(data\s+source|table)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Synonyms
        synonyms = len(re.findall(r'\bcreate\s+synonym\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Temporal Tables (SQL Server 2016+)
        temporal_tables = len(re.findall(r'\bwith\s*\(\s*system_versioning\s*=\s*on\b', code_no_comments, re.IGNORECASE))
        
        # Cross-database queries
        cross_db = len(re.findall(r'\[\w+\]\.\[\w+\]\.\[\w+\]|\w+\.\w+\.\w+', code_no_comments))
        
        score = 1  # Simple: single database, few tables
        if use_database >= 1 or tables > 3 or temp_tables > 0 or table_vars > 0 or cte_count > 0:
            score = 2  # Medium: multiple tables, temp tables, table vars, CTEs
        if use_database > 2 or tables > 10 or views > 0 or cross_db > 0 or synonyms > 0 or temporal_tables > 0:
            score = 3  # Complex: multiple databases, views, cross-db queries, synonyms, temporal tables
        if linked_servers > 0 or external_sources > 0 or cross_db > 5 or tables > 20:
            score = 4  # Very Complex: linked servers, external data sources, extensive cross-db queries
        
        self.dependency_footprint = score

        # --- 3. ANALYTICS DEPTH ---
        # Enhanced: aggregations, window functions, analytical functions, machine learning, graph
        basic_agg = len(re.findall(r'\b(count|sum|avg|min|max|group\s+by)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Window Functions (SQL Server 2012+)
        window_funcs = len(re.findall(r'\b(row_number|rank|dense_rank|ntile|lead|lag|first_value|last_value|over\s*\()\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Advanced Analytics
        advanced_agg = len(re.findall(r'\b(stdev|var|percentile_cont|percentile_disc|cume_dist|percent_rank)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Pivoting and unpivoting
        pivot_ops = len(re.findall(r'\b(pivot|unpivot)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Recursive CTEs
        recursive_cte = len(re.findall(r'\bwith\s+\w+.*?\bas\s*\(.*?union\s+all\b', code_no_comments, re.IGNORECASE | re.DOTALL))
        
        # TIER 2: SQL Server 2017+ Analytics
        string_agg = len(re.findall(r'\bstring_agg\b', code_no_comments, re.IGNORECASE))
        approx_funcs = len(re.findall(r'\b(approx_count_distinct|approx_percentile_cont|approx_percentile_disc)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Graph Database (SQL Server 2017+)
        graph_tables = len(re.findall(r'\bas\s+(node|edge)\b', code_no_comments, re.IGNORECASE))
        graph_queries = len(re.findall(r'\bmatch\s*\(', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Machine Learning Integration
        predict_funcs = len(re.findall(r'\bpredict\s*\(', code_no_comments, re.IGNORECASE))
        
        # Subqueries and complex analytics
        subqueries = len(re.findall(r'\(\s*select\s+', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic queries
        if basic_agg > 0 or subqueries > 0:
            score = 2  # Medium: GROUP BY, basic aggregations
        if window_funcs > 0 or advanced_agg > 0 or pivot_ops > 0 or recursive_cte > 0 or string_agg > 0:
            score = 3  # Complex: window functions, analytics, pivoting, recursive CTEs
        if window_funcs > 3 or graph_queries > 0 or predict_funcs > 0 or approx_funcs > 0:
            score = 4  # Very Complex: advanced analytics, graph queries, machine learning
        
        self.analytics_depth = score

        # --- 4. SQL & REPORTING LOGIC ---
        # Enhanced: query complexity, joins, hints, query store, adaptive query processing
        joins = len(re.findall(r'\b(inner\s+join|left\s+join|right\s+join|full\s+join|cross\s+join|join)\b', code_no_comments, re.IGNORECASE))
        unions = len(re.findall(r'\bunion\s+(all\s+)?', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Query hints
        table_hints = len(re.findall(r'\bwith\s*\(\s*(nolock|readpast|rowlock|paglock|tablock|holdlock|updlock|index)\b', code_no_comments, re.IGNORECASE))
        query_hints = len(re.findall(r'\boption\s*\(\s*(recompile|optimize\s+for|use\s+plan|maxdop)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Complex WHERE and CASE
        complex_where = len(re.findall(r'\bwhere\s+.*\b(and|or)\b.*\b(and|or)\b', code_no_comments, re.IGNORECASE))
        case_stmt = len(re.findall(r'\bcase\s+when\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: SQL Server 2019+ Features
        batch_mode = len(re.findall(r'\bbatch_mode_on_rowstore\b', code_no_comments, re.IGNORECASE))
        adaptive_joins = len(re.findall(r'\badaptive\s+join\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Query Store hints (SQL Server 2022+)
        query_store_hints = len(re.findall(r'\bquery_store_hints\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic SELECT
        if joins >= 1 or case_stmt > 0 or unions > 0 or table_hints > 0:
            score = 2  # Medium: joins, CASE, table hints
        if joins > 3 or query_hints > 0 or complex_where > 0 or unions > 1:
            score = 3  # Complex: multiple joins, query hints, complex conditions
        if joins > 6 or query_hints > 3 or batch_mode > 0 or query_store_hints > 0 or adaptive_joins > 0:
            score = 4  # Very Complex: many joins, advanced optimization, intelligent query processing
        
        self.sql_reporting_logic = score

        # --- 5. TRANSFORMATION LOGIC ---
        # Enhanced: DML, MERGE, JSON/XML, data type conversions, string operations
        updates = len(re.findall(r'\bupdate\s+', code_no_comments, re.IGNORECASE))
        inserts = len(re.findall(r'\binsert\s+into\b', code_no_comments, re.IGNORECASE))
        deletes = len(re.findall(r'\bdelete\s+from\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: MERGE statements
        merge = len(re.findall(r'\bmerge\s+', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Data type conversions
        conversions = len(re.findall(r'\b(convert|cast|try_convert|try_cast|parse|try_parse)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: String operations
        string_ops = len(re.findall(r'\b(substring|charindex|patindex|stuff|replace|ltrim|rtrim|upper|lower|reverse|replicate|space|ascii|char|quotename|string_split|string_escape|string_agg|concat|format)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Date/time functions
        date_funcs = len(re.findall(r'\b(getdate|getutcdate|sysdatetime|sysutcdatetime|dateadd|datediff|datepart|datename|day|month|year|eomonth|datefromparts|timefromparts|datetimefromparts|datetime2fromparts|smalldatetimefromparts|datetimeoffsetfromparts)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: JSON operations (SQL Server 2016+)
        json_ops = len(re.findall(r'\b(json_value|json_query|json_modify|isjson|for\s+json)\b', code_no_comments, re.IGNORECASE))
        openjson = len(re.findall(r'\bopenjson\s*\(', code_no_comments, re.IGNORECASE))
        
        # TIER 2: XML operations
        xml_ops = len(re.findall(r'\b(for\s+xml|\.query\s*\(|\.value\s*\(|\.exist\s*\(|\.nodes\s*\(|\.modify\s*\()\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Bulk operations
        bulk_ops = len(re.findall(r'\bbulk\s+insert\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic SELECT
        if updates > 0 or inserts > 0 or conversions > 2 or date_funcs > 0:
            score = 2  # Medium: basic DML, conversions, date functions
        if merge > 0 or (updates > 2 and inserts > 2) or string_ops > 3 or json_ops > 0 or xml_ops > 0:
            score = 3  # Complex: MERGE, multiple DML, JSON/XML operations
        if merge > 1 or bulk_ops > 0 or (updates > 5 and deletes > 2) or (json_ops > 2 and xml_ops > 2):
            score = 4  # Very Complex: complex MERGE, bulk operations, extensive JSON/XML
        
        self.transformation_logic = score

        # --- 6. UTILITY COMPLEXITY ---
        # Enhanced: procedures, functions, parameters, cursors, CLR, user-defined types
        params = len(re.findall(r'@\w+\s+(int|varchar|nvarchar|char|nchar|datetime|datetime2|date|time|decimal|numeric|float|real|money|smallmoney|bit|binary|varbinary|uniqueidentifier|xml|geography|geometry|hierarchyid|sql_variant)\b', code_no_comments, re.IGNORECASE))
        
        # Variables and declarations
        declares = len(re.findall(r'\bdeclare\s+@\w+', code_no_comments, re.IGNORECASE))
        
        # Control flow
        if_stmt = len(re.findall(r'\bif\b', code_no_comments, re.IGNORECASE))
        while_loop = len(re.findall(r'\bwhile\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Cursors
        cursors = len(re.findall(r'\bdeclare\s+\w+\s+cursor\b', code_no_comments, re.IGNORECASE))
        cursor_types = len(re.findall(r'\b(fast_forward|scroll|dynamic|static|keyset|local|global)\s+cursor\b', code_no_comments, re.IGNORECASE))
        
        # Procedure calls and dynamic SQL
        exec_calls = len(re.findall(r'\bexec(ute)?\s+(\w+|sp_\w+)', code_no_comments, re.IGNORECASE))
        dynamic_sql = len(re.findall(r'\bsp_executesql|execute\s*\(', code_no_comments, re.IGNORECASE))
        
        # TIER 2: CLR integration
        clr_procs = len(re.findall(r'\bexternal\s+name\s+\w+\.\w+\.\w+', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Output parameters and return values
        output_params = len(re.findall(r'@\w+\s+\w+\s+output', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Error handling (TRY/CATCH)
        try_catch = len(re.findall(r'\bbegin\s+try\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no procedures or simple scripts
        if params > 0 or declares > 2 or if_stmt > 1 or exec_calls > 0:
            score = 2  # Medium: procedures with params, basic control flow
        if params > 5 or while_loop > 0 or cursors > 0 or try_catch > 0 or output_params > 0:
            score = 3  # Complex: many params, loops, cursors, error handling
        if cursors > 1 or dynamic_sql > 0 or clr_procs > 0 or (params > 10 and while_loop > 2):
            score = 4  # Very Complex: multiple cursors, dynamic SQL, CLR integration
        
        self.utility_complexity = score

        # --- 7. EXECUTION CONTROL ---
        # Enhanced: transactions, error handling, parallel execution, resource management
        begin_tran = len(re.findall(r'\bbegin\s+tran(saction)?\b', code_no_comments, re.IGNORECASE))
        commit = len(re.findall(r'\bcommit\s+tran(saction)?\b', code_no_comments, re.IGNORECASE))
        rollback = len(re.findall(r'\brollback\s+tran(saction)?\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Savepoints
        savepoints = len(re.findall(r'\bsave\s+tran(saction)?\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Isolation levels
        isolation = len(re.findall(r'\bset\s+transaction\s+isolation\s+level\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: TRY/CATCH blocks (already counted above)
        error_handling = try_catch
        
        # TIER 2: Parallel execution hints
        parallel_hints = len(re.findall(r'\bmaxdop\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Resource Governor (SQL Server 2008+)
        resource_governor = len(re.findall(r'\bcreate\s+(resource\s+pool|workload\s+group)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Memory-optimized tables (SQL Server 2014+)
        memory_optimized = len(re.findall(r'\bwith\s*\(\s*memory_optimized\s*=\s*on\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no explicit transactions
        if begin_tran > 0 or commit > 0 or error_handling > 0:
            score = 2  # Medium: basic transactions, error handling
        if rollback > 0 or savepoints > 0 or isolation > 0 or parallel_hints > 0:
            score = 3  # Complex: rollbacks, savepoints, isolation levels, parallel hints
        if savepoints > 2 or resource_governor > 0 or memory_optimized > 0 or (begin_tran > 3 and rollback > 2):
            score = 4  # Very Complex: advanced transaction control, resource management, memory-optimized
        
        self.execution_control = score

        # --- 8. FILE I/O & EXTERNAL INTEGRATION ---
        # Enhanced: linked servers, file operations, CLR, external scripts, Service Broker
        linked_server_ops = linked_servers  # Already counted above
        
        # TIER 1: File operations
        file_ops = len(re.findall(r'\bbulk\s+insert|\bopenrowset|\bopendatasource\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: System stored procedures
        system_procs = len(re.findall(r'\b(sp_|xp_)\w+', code_no_comments, re.IGNORECASE))
        
        # TIER 2: CLR integration (already counted above)
        clr_integration = clr_assemblies + clr_procs
        
        # TIER 2: Service Broker (already counted above)
        broker_ops = service_broker
        
        # TIER 2: External scripts (R/Python - SQL Server 2017+)
        external_scripts = ml_services  # Already counted above
        
        # TIER 2: PolyBase (SQL Server 2016+)
        polybase = external_sources  # Already counted above
        
        # TIER 1: Email operations
        database_mail = len(re.findall(r'\bsp_send_dbmail\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Command shell
        cmd_shell = len(re.findall(r'\bxp_cmdshell\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no external integration
        if system_procs > 0 or file_ops > 0 or database_mail > 0:
            score = 2  # Medium: basic system procs, file operations, email
        if linked_server_ops > 0 or cmd_shell > 0 or broker_ops > 0 or polybase > 0:
            score = 3  # Complex: linked servers, command shell, Service Broker, PolyBase
        if clr_integration > 0 or external_scripts > 0 or (linked_server_ops > 2 and file_ops > 2):
            score = 4  # Very Complex: CLR, external scripts, extensive external integration
        
        self.file_io_external_integration = score

        # --- 9. ODS OUTPUT DELIVERY ---
        # Enhanced: result sets, output parameters, table-valued functions, temp tables
        select_stmt = len(re.findall(r'\bselect\b', code_no_comments, re.IGNORECASE))
        
        # Output parameters (already counted above)
        output_parameters = output_params
        
        # Return statements
        returns = len(re.findall(r'\breturn\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Table-valued functions (already counted above)
        tvf_usage = tvf_inline + tvf_multi
        
        # TIER 1: Temp tables and table variables (already counted above)
        temp_storage = temp_tables + table_vars
        
        # TIER 1: Result set manipulation
        result_sets = len(re.findall(r'\binsert\s+into\s+#|\bselect\s+.*\binto\s+#', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Multiple result sets
        multiple_selects = select_stmt if select_stmt > 1 else 0
        
        # TIER 2: FOR XML/JSON output
        structured_output = xml_ops + json_ops
        
        score = 1  # Simple: single SELECT or no results
        if select_stmt > 1 or output_parameters > 0 or returns > 0:
            score = 2  # Medium: multiple SELECTs, output parameters
        if select_stmt > 3 or temp_storage > 2 or result_sets > 0 or tvf_usage > 0:
            score = 3  # Complex: many result sets, temp storage, TVFs
        if select_stmt > 6 or structured_output > 2 or (temp_storage > 4 and result_sets > 3):
            score = 4  # Very Complex: many result sets, structured output, complex temp storage
        
        self.ods_output_delivery = score

        # --- 10. ERROR HANDLING & OPTIMIZATION ---
        # Enhanced: error handling, query optimization, indexing, statistics, plan guides
        error_handling_total = try_catch + len(re.findall(r'\braise(r)?error\b', code_no_comments, re.IGNORECASE))
        
        # Error checking with system functions
        error_check = len(re.findall(r'@@error|@@rowcount|error_number|error_message|error_state', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Performance optimization
        set_opts = len(re.findall(r'\bset\s+(nocount|rowcount|statistics|showplan|arithabort)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Indexing
        indexes = len(re.findall(r'\bcreate\s+(unique\s+)?(clustered\s+|nonclustered\s+)?index\b', code_no_comments, re.IGNORECASE))
        columnstore = len(re.findall(r'\bcolumnstore\s+index\b', code_no_comments, re.IGNORECASE))
        filtered_index = len(re.findall(r'\bcreate\s+.*index\s+.*\bwhere\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Statistics
        statistics = len(re.findall(r'\b(create|update)\s+statistics\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Plan guides and hints (SQL Server specific)
        plan_guides = len(re.findall(r'\bsp_create_plan_guide\b', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Intelligent Query Processing features (SQL Server 2017+)
        iqp_features = batch_mode + adaptive_joins + approx_funcs
        
        total_indexes = indexes + columnstore + filtered_index
        
        score = 1  # Simple: no error handling or optimization
        if error_handling_total > 0 or error_check > 0 or set_opts > 0:
            score = 2  # Medium: basic error handling, SET options
        if error_handling_total > 1 or total_indexes > 0 or statistics > 0 or query_hints > 0:
            score = 3  # Complex: comprehensive error handling, indexing, statistics, query hints
        if plan_guides > 0 or columnstore > 0 or iqp_features > 0 or (error_handling_total > 2 and statistics > 2):
            score = 4  # Very Complex: plan guides, columnstore, intelligent query processing
        
        self.error_handling_optimization = score

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
        """
        Calculate the maximum nesting depth of control structures in T-SQL code.
        """
        stack = []
        max_depth = 0

        # Regex patterns for opening and closing structures
        open_pattern = re.compile(r'\b(BEGIN|IF|WHILE|CASE|FOR|TRY|CATCH)\b', re.IGNORECASE)
        close_pattern = re.compile(r'\bEND(\s+TRY|\s+CATCH)?\b', re.IGNORECASE)

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
        Calculate cyclomatic complexity for SQL Server T-SQL.
        
        Counts decision points: IF, WHILE, CASE WHEN, TRY/CATCH, AND/OR conditions
        Cyclomatic Complexity = decision points + 1
        """
        if_count = len(re.findall(r'\bif\b', code, re.IGNORECASE))
        while_count = len(re.findall(r'\bwhile\b', code, re.IGNORECASE))
        case_when = len(re.findall(r'\bwhen\b', code, re.IGNORECASE))
        try_catch = len(re.findall(r'\b(try|catch)\b', code, re.IGNORECASE))
        logical_ops = len(re.findall(r'\b(and|or)\b', code, re.IGNORECASE))
        
        decision_points = if_count + while_count + case_when + try_catch + logical_ops
        
        return max(1, decision_points + 1)
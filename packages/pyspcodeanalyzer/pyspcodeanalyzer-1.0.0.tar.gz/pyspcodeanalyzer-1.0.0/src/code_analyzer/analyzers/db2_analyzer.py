# src/code_analyzer/analyzers/db2_analyzer.py
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


class DB2Analyzer(AnalyzerBase):
    """
    DB2 code complexity analyzer with enterprise metrics integration.
    
    Evaluates DB2 scripts across 10 dimensions, each scored 1-4:
    - 1: Simple
    - 2: Medium
    - 3: Complex
    - 4: Very Complex
    
    Uses hybrid approach:
    - Config weights override registry defaults
    - Enterprise validation via metrics module
    - Standardized 0-100 scoring system
    """
    language = "db2"
    
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
        """Analyze DB2 source code and return complexity metrics."""
        include_cyclomatic = self.config.get("include_cyclomatic", False)
        
        # If code is None or empty, try to read from file path
        if not code and path and path != "<string>":
            file_content = read_file_if_exists(path)
            if file_content:
                code = file_content
        
        # Run complexity analysis
        analyzer = DB2Complexity()
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
    

class DB2Complexity:
    """
    Enterprise-grade DB2 complexity analyzer with comprehensive pattern detection.
    Each metric is scored 1 (Simple) to 4 (Very Complex) based on DB2-specific patterns.
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
        # Enhanced: lines, procedures, functions, modules, packages, triggers
        lines = len([line for line in code.split('\n') if line.strip()])
        
        # DB2 objects
        procedures = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?procedure\b', code_no_comments, re.IGNORECASE))
        functions = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?function\b', code_no_comments, re.IGNORECASE))
        triggers = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?trigger\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: DB2 Modules and Packages
        modules = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?module\b', code_no_comments, re.IGNORECASE))
        packages = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?package\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Table Functions
        table_functions = len(re.findall(r'\bcreate\s+function\s+\w+.*returns\s+table\b', code_no_comments, re.IGNORECASE | re.DOTALL))
        
        # TIER 2: Advanced Objects
        sequences = len(re.findall(r'\bcreate\s+sequence\b', code_no_comments, re.IGNORECASE))
        types = len(re.findall(r'\bcreate\s+type\b', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Advanced Features
        columnar_tables = len(re.findall(r'\borganized\s+by\s+column\b', code_no_comments, re.IGNORECASE))
        temporal_tables = len(re.findall(r'\bsystem_time\b|\bperiod\s+for\s+system_time\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: small script
        if lines > 100 or procedures > 0 or functions > 0 or nesting_level > 1:
            score = 2  # Medium: moderate size, procedures, or basic nesting
        if lines > 500 or modules > 0 or (procedures + functions) > 3 or triggers > 0 or table_functions > 0 or nesting_level > 3:
            score = 3  # Complex: large, modules, multiple objects, table functions, or deep nesting
        if lines > 2000 or packages > 2 or (procedures + functions + triggers) > 8 or types > 1 or columnar_tables > 0 or temporal_tables > 0 or nesting_level > 5:
            score = 4  # Very Complex: very large, multiple packages, many objects, advanced features, or very deep nesting
        
        self.script_size_structure = score

        # --- 2. DEPENDENCY FOOTPRINT ---
        # Enhanced: tables, views, nicknames, federated sources, synonyms
        tables = len(re.findall(r'\bfrom\s+(\w+\.)?(\w+)', code_no_comments, re.IGNORECASE))
        views = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?view\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: DB2 Federation - Nicknames
        nicknames = len(re.findall(r'\bcreate\s+nickname\b|\bfrom\s+\w+\.\w+\.\w+', code_no_comments, re.IGNORECASE))
        
        # Synonyms and aliases
        synonyms = len(re.findall(r'\bcreate\s+(or\s+replace\s+)?alias\b', code_no_comments, re.IGNORECASE))
        
        # Database links and remote connections
        database_links = len(re.findall(r'\bconnect\s+to\b|\bset\s+connection\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Materialized Query Tables (MQTs)
        mqts = len(re.findall(r'\bcreate\s+table\s+\w+.*as\s+.*refresh\b', code_no_comments, re.IGNORECASE | re.DOTALL))
        
        # TIER 2: Federated sources
        servers = len(re.findall(r'\bcreate\s+server\b|\bcreate\s+wrapper\b', code_no_comments, re.IGNORECASE))
        
        # Cross-database references
        cross_db = len(re.findall(r'\w+\.\w+\.\w+', code_no_comments))
        
        score = 1  # Simple: basic table references
        if tables > 3 or views > 0 or synonyms > 0:
            score = 2  # Medium: multiple tables, views, or synonyms
        if tables > 10 or nicknames > 0 or cross_db > 0 or mqts > 0:
            score = 3  # Complex: many tables, nicknames, cross-db, or MQTs
        if nicknames > 3 or servers > 0 or cross_db > 5 or tables > 20:
            score = 4  # Very Complex: extensive federation, many servers, or many tables
        
        self.dependency_footprint = score

        # --- 3. ANALYTICS DEPTH ---
        # Enhanced: aggregations, OLAP functions, analytics, XML processing
        basic_agg = len(re.findall(r'\b(count|sum|avg|min|max|group\s+by)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: OLAP and Window Functions
        window_funcs = len(re.findall(r'\b(row_number|rank|dense_rank|lead|lag|first_value|last_value|over\s*\()\b', code_no_comments, re.IGNORECASE))
        olap_funcs = len(re.findall(r'\b(rollup|cube|grouping\s+sets)\b', code_no_comments, re.IGNORECASE))
        
        # Advanced aggregations
        advanced_agg = len(re.findall(r'\b(stddev|variance|correlation|regression)\b', code_no_comments, re.IGNORECASE))
        
        # CTEs and recursive queries
        cte = len(re.findall(r'\bwith\s+\w+\s+as\s*\(', code_no_comments, re.IGNORECASE))
        recursive_cte = len(re.findall(r'\bwith\s+recursive\s+\w+', code_no_comments, re.IGNORECASE))
        
        # TIER 2: XML Processing
        xml_funcs = len(re.findall(r'\bxmlquery\b|\bxmlexists\b|\bxmltable\b|\bxmlparse\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Spatial Functions
        spatial_funcs = len(re.findall(r'\bst_\w+\b|\bdb2gse\.\w+', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Analytics and Machine Learning
        ml_funcs = len(re.findall(r'\bpredict\b|\bscore\b|\bregression\b|\bclassify\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic queries
        if basic_agg > 0 or cte > 0:
            score = 2  # Medium: aggregations or basic CTEs
        if window_funcs > 0 or olap_funcs > 0 or xml_funcs > 0 or advanced_agg > 0:
            score = 3  # Complex: OLAP, window functions, XML, or advanced analytics
        if recursive_cte > 0 or spatial_funcs > 2 or ml_funcs > 0 or (window_funcs > 3 and olap_funcs > 1):
            score = 4  # Very Complex: recursive CTEs, extensive spatial/ML, or heavy analytics
        
        self.analytics_depth = score

        # --- 4. SQL REPORTING LOGIC ---
        # Enhanced: query complexity, joins, cursors, result sets
        joins = len(re.findall(r'\b(inner\s+join|left\s+join|right\s+join|full\s+join|cross\s+join|join)\b', code_no_comments, re.IGNORECASE))
        unions = len(re.findall(r'\bunion\s+(all\s+)?', code_no_comments, re.IGNORECASE))
        
        # DB2-specific: Cursors
        cursors = len(re.findall(r'\bdeclare\s+\w+\s+cursor\b', code_no_comments, re.IGNORECASE))
        cursor_operations = len(re.findall(r'\bopen\b|\bfetch\b|\bclose\b', code_no_comments, re.IGNORECASE))
        
        # Complex predicates
        case_stmt = len(re.findall(r'\bcase\s+when\b', code_no_comments, re.IGNORECASE))
        subqueries = len(re.findall(r'\(\s*select\s+', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Common Table Expressions with multiple references
        cte_refs = len(re.findall(r'\bwith\s+.*,\s*\w+\s+as\s*\(', code_no_comments, re.IGNORECASE | re.DOTALL))
        
        score = 1  # Simple: basic SELECT
        if joins >= 1 or case_stmt > 0 or cursors > 0:
            score = 2  # Medium: basic joins, CASE, or cursors
        if joins > 3 or unions > 1 or subqueries > 2 or cursor_operations > 3:
            score = 3  # Complex: multiple joins, unions, subqueries, or cursor operations
        if joins > 6 or unions > 3 or subqueries > 5 or cte_refs > 2:
            score = 4  # Very Complex: extensive joins, unions, subqueries, or complex CTEs
        
        self.sql_reporting_logic = score

        # --- 5. TRANSFORMATION LOGIC ---
        # Enhanced: DML operations, data transformations, MERGE operations
        updates = len(re.findall(r'\bupdate\s+\w+', code_no_comments, re.IGNORECASE))
        inserts = len(re.findall(r'\binsert\s+into\b', code_no_comments, re.IGNORECASE))
        deletes = len(re.findall(r'\bdelete\s+from\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: MERGE operations
        merge = len(re.findall(r'\bmerge\s+into\b', code_no_comments, re.IGNORECASE))
        
        # Data type conversions
        conversions = len(re.findall(r'\b(cast|decimal|varchar|char|date|timestamp)\s*\(', code_no_comments, re.IGNORECASE))
        
        # String and date functions
        string_ops = len(re.findall(r'\b(substr|substring|concat|trim|upper|lower|replace|translate)\b', code_no_comments, re.IGNORECASE))
        date_funcs = len(re.findall(r'\b(current\s+date|current\s+time|current\s+timestamp|year|month|day|extract)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Advanced transformations
        pivot_ops = len(re.findall(r'\bpivot\b|\bunpivot\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic SELECT
        if updates > 0 or inserts > 0 or conversions > 2:
            score = 2  # Medium: basic DML or conversions
        if merge > 0 or deletes > 0 or string_ops > 3 or date_funcs > 3:
            score = 3  # Complex: MERGE, deletes, or extensive transformations
        if merge > 2 or pivot_ops > 0 or (updates > 5 and deletes > 2):
            score = 4  # Very Complex: multiple MERGE, pivot operations, or heavy DML
        
        self.transformation_logic = score

        # --- 6. UTILITY COMPLEXITY ---
        # Enhanced: procedures, functions, parameters, control structures
        params = len(re.findall(r'\b(in|out|inout)\s+\w+', code_no_comments, re.IGNORECASE))
        variables = len(re.findall(r'\bdeclare\s+\w+', code_no_comments, re.IGNORECASE))
        
        # Control flow
        if_stmt = len(re.findall(r'\bif\b', code_no_comments, re.IGNORECASE))
        while_loop = len(re.findall(r'\bwhile\b', code_no_comments, re.IGNORECASE))
        for_loop = len(re.findall(r'\bfor\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: DB2 Compound statements
        compound_stmt = len(re.findall(r'\bbegin\s+atomic\b', code_no_comments, re.IGNORECASE))
        
        # Exception handling
        handlers = len(re.findall(r'\bdeclare\s+.*handler\b', code_no_comments, re.IGNORECASE))
        
        # Dynamic SQL
        dynamic_sql = len(re.findall(r'\bprepare\b|\bexecute\s+immediate\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic statements
        if params > 0 or variables > 2 or if_stmt > 1:
            score = 2  # Medium: parameters, variables, or basic control flow
        if while_loop > 0 or for_loop > 0 or compound_stmt > 0 or handlers > 0:
            score = 3  # Complex: loops, compound statements, or handlers
        if dynamic_sql > 0 or handlers > 3 or (params > 10 and while_loop > 2):
            score = 4  # Very Complex: dynamic SQL, extensive handlers, or complex procedures
        
        self.utility_complexity = score

        # --- 7. EXECUTION CONTROL ---
        # Enhanced: transactions, savepoints, compound statements
        begin_work = len(re.findall(r'\bbegin\s+work\b|\bstart\s+transaction\b', code_no_comments, re.IGNORECASE))
        commit = len(re.findall(r'\bcommit\s+work\b|\bcommit\b', code_no_comments, re.IGNORECASE))
        rollback = len(re.findall(r'\brollback\s+work\b|\brollback\b', code_no_comments, re.IGNORECASE))
        
        # Savepoints
        savepoints = len(re.findall(r'\bsavepoint\b|\brelease\s+savepoint\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Isolation levels
        isolation = len(re.findall(r'\bset\s+isolation\b|\bisolation\s+level\b', code_no_comments, re.IGNORECASE))
        
        # Lock statements
        lock_table = len(re.findall(r'\block\s+table\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Workload management
        workload = len(re.findall(r'\bset\s+workload\b|\bwlm_set_\w+\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no explicit transaction control
        if begin_work > 0 or commit > 0:
            score = 2  # Medium: basic transaction control
        if rollback > 0 or savepoints > 0 or lock_table > 0:
            score = 3  # Complex: rollbacks, savepoints, or locking
        if isolation > 0 or savepoints > 2 or workload > 0:
            score = 4  # Very Complex: custom isolation, multiple savepoints, or workload management
        
        self.execution_control = score

        # --- 8. FILE I/O & EXTERNAL INTEGRATION ---
        # Enhanced: federation, external procedures, web services
        # TIER 1: Federation
        federated_queries = nicknames  # Already calculated above
        
        # External stored procedures
        external_procs = len(re.findall(r'\bexternal\s+name\b|\blanguage\s+(java|c)\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Import/Export operations
        import_export = len(re.findall(r'\bimport\s+from\b|\bexport\s+to\b|\bload\s+from\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Web services and HTTP
        web_services = len(re.findall(r'\bhttp\w+\b|\bsoap\w+\b|\brest\w+\b', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Advanced integration
        mq_functions = len(re.findall(r'\bmq\w+\b|\bmessage\s+queue\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no external integration
        if import_export > 0 or external_procs > 0:
            score = 2  # Medium: basic file operations or external procedures
        if federated_queries > 0 or web_services > 0:
            score = 3  # Complex: federation or web services
        if mq_functions > 0 or federated_queries > 3 or web_services > 2:
            score = 4  # Very Complex: message queues, extensive federation, or multiple web services
        
        self.file_io_external_integration = score

        # --- 9. ODS OUTPUT DELIVERY ---
        # Enhanced: result sets, output parameters, cursors
        select_stmt = len(re.findall(r'\bselect\b', code_no_comments, re.IGNORECASE))
        
        # Output parameters
        output_params = len(re.findall(r'\bout\s+\w+', code_no_comments, re.IGNORECASE))
        
        # Return statements and codes
        returns = len(re.findall(r'\breturn\b', code_no_comments, re.IGNORECASE))
        
        # TIER 1: Result set cursors
        result_cursors = cursors  # Already calculated above
        
        # Temporary tables for staging
        temp_tables = len(re.findall(r'\bcreate\s+(global\s+)?temp(orary)?\s+table\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Multiple result sets
        multiple_selects = 1 if select_stmt > 3 else 0
        
        score = 1  # Simple: single result set
        if select_stmt > 1 or output_params > 0 or returns > 0:
            score = 2  # Medium: multiple SELECTs or output parameters
        if result_cursors > 0 or temp_tables > 0 or multiple_selects > 0:
            score = 3  # Complex: cursors, temp tables, or multiple result sets
        if result_cursors > 2 or temp_tables > 3 or select_stmt > 8:
            score = 4  # Very Complex: multiple cursors, many temp tables, or extensive result sets
        
        self.ods_output_delivery = score

        # --- 10. ERROR HANDLING & OPTIMIZATION ---
        # Enhanced: exception handling, hints, optimization features
        # Exception handlers
        exception_handlers = handlers  # Already calculated above
        signal_stmt = len(re.findall(r'\bsignal\s+sqlstate\b|\bresign\b', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Optimization hints and directives
        hints = len(re.findall(r'\boptimize\s+for\b|\bwith\s+ur\b|\bwith\s+cs\b', code_no_comments, re.IGNORECASE))
        explain_stmt = len(re.findall(r'\bexplain\s+plan\b|\bexplain\s+all\b', code_no_comments, re.IGNORECASE))
        
        # Performance features
        indexes = len(re.findall(r'\bcreate\s+(unique\s+)?index\b', code_no_comments, re.IGNORECASE))
        statistics = len(re.findall(r'\brunstats\b|\bupdate\s+statistics\b', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Advanced optimization
        workload_mgmt = workload  # Already calculated above
        compression = len(re.findall(r'\bcompress\b|\brow\s+compression\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic statements
        if exception_handlers > 0 or signal_stmt > 0 or hints > 0:
            score = 2  # Medium: basic error handling or hints
        if explain_stmt > 0 or indexes > 0 or statistics > 0:
            score = 3  # Complex: optimization analysis, indexing, or statistics
        if workload_mgmt > 0 or compression > 0 or (exception_handlers > 3 and hints > 2):
            score = 4  # Very Complex: workload management, compression, or comprehensive optimization
        
        self.error_handling_optimization = score

        # Calculate cyclomatic complexity
        self.cyclomatic = self._calculate_cyclomatic_complexity(code_no_comments)

    def _remove_comments(self, code: str) -> str:
        """Remove DB2 SQL comments from code for accurate analysis."""
        # Remove block comments /* ... */
        code_no_block = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        
        # Remove single-line comments --
        code_no_single = re.sub(r'--.*$', '', code_no_block, flags=re.MULTILINE)
        
        return code_no_single

    def _get_nesting_level(self, code: str) -> int:
        """
        Calculate the maximum nesting depth of control structures in DB2 SQL code.
        """
        stack = []
        max_depth = 0

        # Regex patterns for opening and closing structures
        open_pattern = re.compile(r'\b(BEGIN|IF|WHILE|FOR|LOOP|CASE)\b', re.IGNORECASE)
        close_pattern = re.compile(r'\bEND(\s+IF|\s+WHILE|\s+FOR|\s+LOOP|\s+CASE)?\b', re.IGNORECASE)

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
        Calculate cyclomatic complexity for DB2 SQL.
        
        Counts decision points: IF, CASE WHEN, WHILE, FOR, exception handlers
        Cyclomatic Complexity = decision points + 1
        """
        if_count = len(re.findall(r'\bif\b', code, re.IGNORECASE))
        case_when = len(re.findall(r'\bwhen\b', code, re.IGNORECASE))
        while_count = len(re.findall(r'\bwhile\b', code, re.IGNORECASE))
        for_count = len(re.findall(r'\bfor\b', code, re.IGNORECASE))
        handler_count = len(re.findall(r'\bhandler\b', code, re.IGNORECASE))
        
        decision_points = if_count + case_when + while_count + for_count + handler_count

        return max(1, decision_points + 1)
# src/code_analyzer/analyzers/sas_analyzer.py
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

class SASAnalyzer(AnalyzerBase):
    """
    SAS code complexity analyzer with enterprise metrics integration.
    
    Evaluates SAS scripts across 10 dimensions, each scored 1-4:
    - 1: Simple
    - 2: Medium
    - 3: Complex
    - 4: Very Complex
    
    Uses hybrid approach:
    - Config weights override registry defaults
    - Enterprise validation via metrics module
    - Standardized 0-100 scoring system
    """
    language = "sas"
    
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
        """Analyze SAS source code and return complexity metrics."""
        include_cyclomatic = self.config.get("include_cyclomatic", False)
        
        # If code is None or empty, try to read from file path
        if not code and path and path != "<string>":
            file_content = read_file_if_exists(path)
            if file_content:
                code = file_content
        
        # Run complexity analysis
        analyzer = SASComplexity()
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
    
# New requirements-based SAS complexity analyzer
class SASComplexity:
    """
    Enterprise-grade SAS complexity analyzer with comprehensive pattern detection.
    Each metric is scored 1 (Simple) to 4 (Very Complex) based on requirements.
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
        """Analyze SAS code and compute all complexity metrics."""
        if not code or not code.strip():
            return
        
        # Remove comments for accurate analysis
        code_no_comments = self._remove_comments(code)
        lines = [ln for ln in code_no_comments.splitlines() if ln.strip()]
        num_lines = len(lines)
        
        # Calculate nesting depth
        nesting_level = self._get_nesting_level(code_no_comments)
        
        # Count fundamental constructs
        num_data_steps = len(re.findall(r'(^|;)\s*data\s+[^;]+;', code_no_comments, re.IGNORECASE | re.MULTILINE))
        proc_steps = len(re.findall(r'\bproc\s+\w+', code_no_comments, re.IGNORECASE))
        
        # --- 1. SCRIPT SIZE & STRUCTURE ---
        # Considers: lines, DATA steps, PROC steps, macro blocks, nesting
        macro_blocks = len(re.findall(r'%macro\s+\w+', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: <100 lines, 1 DATA step, no nesting
        if num_lines > 100 or num_data_steps > 1 or proc_steps > 3:
            score = 2  # Medium: 100-500 lines, 2-3 DATA steps
        if num_lines > 500 or num_data_steps > 3 or proc_steps > 6 or macro_blocks > 2 or nesting_level > 2:
            score = 3  # Complex: 500-2000 lines, 4-6 DATA steps, moderate nesting
        if num_lines > 2000 or num_data_steps > 6 or macro_blocks > 5 or nesting_level > 4:
            score = 4  # Very Complex: >2000 lines, >6 DATA steps, deep nesting, modularized
        
        self.script_size_structure = score

        # --- 2. DEPENDENCY FOOTPRINT ---
        # Considers: LIBNAME, schemas, external datasets, table references, connections
        libnames = len(re.findall(r'\blibname\s+\w+', code_no_comments, re.IGNORECASE))
        schemas = len(re.findall(r'\b(schema|database|catalog|authdomain)\b', code_no_comments, re.IGNORECASE))
        
        # External connections: ODBC, Oracle, cloud storage, modern DB
        ext_conn = len(re.findall(r'\b(odbc|oracle|teradata|db2|mysql|postgresql|hadoop|spark|s3|azure|gcs|bigquery|snowflake|redshift)\b', code_no_comments, re.IGNORECASE))
        
        # Count unique table references (from dataset references)
        # Pattern: libname.tablename or work.tablename
        table_refs = len(re.findall(r'\b\w+\.\w+(?=\s|;|\)|$)', code_no_comments))
        
        score = 1  # Simple: 0-1 LIBNAME, 0-3 table refs, no external connections
        if libnames >= 2 or (table_refs > 3 and table_refs <= 10):
            score = 2  # Medium: 2-3 LIBNAME, 4-10 tables
        if libnames >= 4 or schemas >= 1 or table_refs > 10 or ext_conn > 0:
            score = 3  # Complex: 4-6 LIBNAME/schema, 11-20 tables, or external connections
        if libnames > 6 or schemas > 2 or table_refs > 20 or ext_conn > 2:
            score = 4  # Very Complex: >6 LIBNAME/schema, >20 tables, dynamic schema switching
        
        self.dependency_footprint = score

        # --- 3. ANALYTICS DEPTH ---
        # Considers: statistical procedures, predictive modeling, custom analytics
        analytics_simple = len(re.findall(r'\bproc\s+(means|freq|univariate|summary|tabulate|print)\b', code_no_comments, re.IGNORECASE))
        analytics_medium = len(re.findall(r'\bproc\s+(ttest|anova|reg|corr|glm|logistic|npar1way)\b', code_no_comments, re.IGNORECASE))
        analytics_complex = len(re.findall(r'\bproc\s+(arima|hpforest|hpsplit|timeseries|esm|ucm|forecast|varmax)\b', code_no_comments, re.IGNORECASE))
        analytics_very_complex = len(re.findall(r'\bproc\s+(hpsvm|hpimpute|treeboost|neural|discrim|princomp|factor|cluster|fastclus|candisc)\b', code_no_comments, re.IGNORECASE))
        
        # Advanced features: arrays, hash objects, PROC FCMP, user-defined functions
        custom_array = len(re.findall(r'\barray\s+\w+', code_no_comments, re.IGNORECASE))
        hash_object = len(re.findall(r'\b(hash|hiter)\s+\w+', code_no_comments, re.IGNORECASE))
        user_func = len(re.findall(r'proc\s+fcmp|function\s+\w+\s*\(', code_no_comments, re.IGNORECASE))
        
        # Custom analytics macros
        custom_analytics_macro = len(re.findall(r'%analytics|%model|%predict|%score', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: PROC MEANS, FREQ, UNIVARIATE only
        if analytics_medium > 0 or custom_array > 0:
            score = 2  # Medium: adds TTEST, ANOVA, REG, CORR, GLM
        if analytics_complex > 0 or hash_object > 0 or user_func > 0 or analytics_medium > 2:
            score = 3  # Complex: ARIMA, HPFOREST, HPSPLIT, TIMESERIES, ESM, UCM
        if analytics_very_complex > 0 or custom_analytics_macro > 0 or (analytics_complex > 2 and analytics_medium > 2):
            score = 4  # Very Complex: multiple advanced analytics together, user-defined analytics
        
        self.analytics_depth = score

        # --- 4. SQL + REPORTING LOGIC ---
        # Considers: SQL complexity, joins, tables, views, reporting procs
        proc_print = len(re.findall(r'\bproc\s+print\b', code_no_comments, re.IGNORECASE))
        proc_report = len(re.findall(r'\bproc\s+(report|tabulate)\b', code_no_comments, re.IGNORECASE))
        
        # SQL detection
        proc_sql = len(re.findall(r'\bproc\s+sql\b', code_no_comments, re.IGNORECASE))
        
        # Explicit join counting (inner, left, right, full, cross)
        join_count = len(re.findall(r'\b(inner\s+join|left\s+join|right\s+join|full\s+join|cross\s+join|join)\b', code_no_comments, re.IGNORECASE))
        
        # Merge statements (SAS data step merges)
        merge_count = len(re.findall(r'\bmerge\s+', code_no_comments, re.IGNORECASE))
        
        # Table creation and manipulation
        table_create = len(re.findall(r'\bcreate\s+table\b', code_no_comments, re.IGNORECASE))
        table_views = len(re.findall(r'\bcreate\s+view\b', code_no_comments, re.IGNORECASE))
        
        # Advanced SQL features
        sql_advanced = len(re.findall(r'\b(alter\s+table|union|intersect|except|outer\s+apply|cross\s+apply)\b', code_no_comments, re.IGNORECASE))
        sql_nested = len(re.findall(r'\b(with\s+\w+\s+as|case\s+when|subquery|exists\s*\(|having\b)\b', code_no_comments, re.IGNORECASE))
        
        # Dynamic SQL
        dynamic_sql = len(re.findall(r'execute\s*\(|%sql|%sysfunc\s*\(\s*execute', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: PROC PRINT only, or basic SQL with no joins/views
        # Medium: basic SQL with simple SELECT/GROUP BY, or PROC REPORT (no joins, no views)
        if (proc_sql > 0 and join_count == 0 and table_views == 0) or proc_report > 0:
            score = 2
        # Complex: SQL with joins, views, or advanced features
        if join_count >= 1 or table_views > 0 or sql_nested > 0 or merge_count >= 1:
            score = 3
        # Very Complex: heavy nesting, dynamic SQL, many joins/merges or many created tables
        if sql_nested > 2 or dynamic_sql > 0 or join_count > 4 or merge_count > 4 or table_create > 4:
            score = 4
        
        self.sql_reporting_logic = score

        # --- 5. TRANSFORMATION LOGIC ---
        # Considers: data reshaping, date functions, loops, merges, arrays, hash
        case_when = len(re.findall(r'\b(case\s+when|select\s+when)\b', code_no_comments, re.IGNORECASE))
        group_by = len(re.findall(r'\bgroup\s+by\b', code_no_comments, re.IGNORECASE))
        
        # Date/time functions
        intnx_intck = len(re.findall(r'\b(intnx|intck)\s*\(', code_no_comments, re.IGNORECASE))
        date_fn = len(re.findall(r'\b(year|month|day|mdy|today|datepart|timepart|dhms)\s*\(', code_no_comments, re.IGNORECASE))
        
        # Data reshaping
        proc_transpose = len(re.findall(r'\bproc\s+transpose\b', code_no_comments, re.IGNORECASE))
        
        # Loops and nested logic
        do_loops = len(re.findall(r'\bdo\s+(while|until|\w+\s*=|;)', code_no_comments, re.IGNORECASE))
        nested_if = len(re.findall(r'if\s+.*then\s+do', code_no_comments, re.IGNORECASE))
        
        # SQL subqueries
        sql_subq = len(re.findall(r'\(\s*select\s+.*\bfrom\b', code_no_comments, re.IGNORECASE))
        
        # Arrays and hash for transformations
        array_proc = len(re.findall(r'\barray\s+\w+', code_no_comments, re.IGNORECASE))
        hash_proc = len(re.findall(r'\b(hash|hiter)\s+\w+', code_no_comments, re.IGNORECASE))
        
        # Custom transformation macros
        custom_trans = len(re.findall(r'%transform|%trans|%pivot|%reshape', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic math, simple IF-ELSE
        if case_when > 0 or group_by > 0 or intnx_intck > 0 or date_fn >= 2 or do_loops > 0 or merge_count >= 1:
            score = 2  # Medium: CASE WHEN, GROUP BY, date functions, DO loops, simple joins/merges
        if proc_transpose > 0 or do_loops > 3 or nested_if > 1 or array_proc > 0 or hash_proc > 0 or merge_count > 2:
            score = 3  # Complex: PROC TRANSPOSE, multiple DO loops, nested IF-ELSE, array/hash processing
        if sql_subq > 1 or proc_transpose > 1 or do_loops > 6 or merge_count > 4 or custom_trans > 0 or (array_proc > 2 and hash_proc > 0):
            score = 4  # Very Complex: nested loops, multiple PROC TRANSPOSE, SQL subqueries, advanced joins/merges
        
        self.transformation_logic = score

        # --- 6. MACRO COMPLEXITY (UTILITY COMPLEXITY) ---
        # Considers: macro variables, macro programs, nesting, dynamic execution
        macro_let = len(re.findall(r'%let\s+\w+', code_no_comments, re.IGNORECASE))
        macro_global = len(re.findall(r'%global\s+\w+', code_no_comments, re.IGNORECASE))
        macro_local = len(re.findall(r'%local\s+\w+', code_no_comments, re.IGNORECASE))
        call_symput = len(re.findall(r'call\s+symput', code_no_comments, re.IGNORECASE))
        
        macro_def = len(re.findall(r'%macro\s+\w+', code_no_comments, re.IGNORECASE))
        macro_do = len(re.findall(r'%do\s+', code_no_comments, re.IGNORECASE))
        macro_if = len(re.findall(r'%if\s+', code_no_comments, re.IGNORECASE))
        macro_put = len(re.findall(r'%put\s+', code_no_comments, re.IGNORECASE))
        
        # Advanced macro features
        macro_sysfunc = len(re.findall(r'%sysfunc|%eval|%sysevalf', code_no_comments, re.IGNORECASE))
        macro_scan = len(re.findall(r'%scan|%substr|%index|%upcase|%length', code_no_comments, re.IGNORECASE))
        
        # Nested macros (rough heuristic)
        macro_nested = len(re.findall(r'%macro\s+\w+[^%]*%macro\s+\w+', code_no_comments, re.IGNORECASE | re.DOTALL))
        
        # Macro calls
        macro_calls = len(re.findall(r'%\w+\s*\(', code_no_comments))
        
        score = 1  # Simple: no macros or 1 trivial macro (just wrapping PROCs)
        # Medium: macros with conditional logic (%IF/%DO) or multiple simple macros
        if (macro_def > 0 and (macro_do > 0 or macro_if > 1)) or macro_def > 2 or macro_let > 5 or macro_sysfunc > 0:
            score = 2
        if macro_def > 5 or macro_calls > 10 or macro_sysfunc > 2 or macro_nested > 0 or (macro_global > 3 and macro_local > 3):
            score = 3  # Complex: many macros, nested macros, dynamic variable creation
        if macro_def > 10 or macro_calls > 20 or macro_nested > 1 or (macro_sysfunc > 5 and macro_scan > 5):
            score = 4  # Very Complex: deep macro libraries, dynamic flow, extensive %SYSFUNC, %EVAL
        
        self.utility_complexity = score

        # --- 7. EXECUTION CONTROL ---
        # Considers: includes, returns, conditional execution, modular flow, grid computing
        include_stmt = len(re.findall(r'%include\s+', code_no_comments, re.IGNORECASE))
        return_stmt = len(re.findall(r'%return\s*;', code_no_comments, re.IGNORECASE))
        abort_stmt = len(re.findall(r'%abort\s+', code_no_comments, re.IGNORECASE))
        
        # Conditional execution
        conditional_exec = len(re.findall(r'%if.*%then|%else', code_no_comments, re.IGNORECASE))
        
        # Modular execution and advanced control
        goto_stmt = len(re.findall(r'%goto\s+', code_no_comments, re.IGNORECASE))
        
        # Grid computing and distributed execution
        signon = len(re.findall(r'%signon|%signoff|signon\s+|signoff\s+', code_no_comments, re.IGNORECASE))
        gridsvc = len(re.findall(r'grdsvc_|gridopt|%syslput|%sysrput|rsubmit', code_no_comments, re.IGNORECASE))
        
        # Job orchestration macros
        job_orch = len(re.findall(r'%job|%orchestrate|%workflow|%pipeline', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: 0-2 %INCLUDE, no conditional/grid control
        if include_stmt > 2 or conditional_exec > 0 or return_stmt > 0:
            score = 2  # Medium: 3+ %INCLUDE, %RETURN, or basic conditional execution
        if include_stmt > 4 or conditional_exec > 3 or abort_stmt > 0 or job_orch > 0:
            score = 3  # Complex: many includes (>4), conditional execution
        if goto_stmt > 0 or signon > 0 or gridsvc > 0 or job_orch > 1 or include_stmt > 8:
            score = 4  # Very Complex: modular execution with %GOTO, dynamic flow, grid computing
        
        self.execution_control = score

        # --- 8. FILE I/O & EXTERNAL INTEGRATION ---
        # Considers: file operations, system calls, external connections, cloud storage
        infile_stmt = len(re.findall(r'\binfile\s+', code_no_comments, re.IGNORECASE))
        file_stmt = len(re.findall(r'\bfile\s+\w+', code_no_comments, re.IGNORECASE))
        filename_stmt = len(re.findall(r'\bfilename\s+\w+', code_no_comments, re.IGNORECASE))
        
        # Input/output operations
        input_stmt = len(re.findall(r'\binput\s+', code_no_comments, re.IGNORECASE))
        put_stmt = len(re.findall(r'\bput\s+', code_no_comments, re.IGNORECASE))
        
        # PROC PRINTTO for redirecting output
        proc_printto = len(re.findall(r'\bproc\s+printto\b', code_no_comments, re.IGNORECASE))
        
        # System calls
        sysexec = len(re.findall(r'%sysexec|systask\s+|x\s+[\'"]', code_no_comments, re.IGNORECASE))
        
        # External integrations: FTP, HTTP, REST, cloud storage
        ext_io = len(re.findall(r'\b(ftp|http|https|rest|api|soap|wsdl)\b', code_no_comments, re.IGNORECASE))
        cloud_storage = len(re.findall(r'\b(hadoop|spark|s3|gcs|azure|bigquery|snowflake)\b', code_no_comments, re.IGNORECASE))
        
        # Modern DB connectors
        db_conn = len(re.findall(r'\b(odbc|jdbc|oracle|teradata|db2|mysql|postgresql|connection\s*=)\b', code_no_comments, re.IGNORECASE))
        
        # Dynamic file handling macros
        dynamic_file = len(re.findall(r'%file|%external|%import|%export', code_no_comments, re.IGNORECASE))
        
        # Remote execution and grid computing (counts as external integration)
        remote_exec = len(re.findall(r'\b(rsubmit|endrsubmit|%syslput|%sysrput)\b', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no file ops/system calls
        if infile_stmt > 0 or file_stmt > 0 or filename_stmt > 0 or input_stmt > 5 or db_conn > 0 or proc_printto > 0:
            score = 2  # Medium: INFILE, FILE, FILENAME, basic DB connectors
        if filename_stmt > 2 or sysexec > 0 or dynamic_file > 0 or db_conn > 2 or remote_exec > 0:
            score = 3  # Complex: multiple file blocks, basic system calls, ODBC/Oracle/modern DB, remote execution
        if ext_io > 0 or cloud_storage > 0 or sysexec > 2 or db_conn > 5 or remote_exec > 2:
            score = 4  # Very Complex: dynamic file handling, FTP, shell, REST API, cloud storage, advanced DB connectors
        
        self.file_io_external_integration = score

        # --- 9. ODS & OUTPUT DELIVERY ---
        # Considers: ODS complexity, styling, destinations, templates, graphs
        ods_basic = len(re.findall(r'\bods\s+(html|listing|output|trace|close)\b', code_no_comments, re.IGNORECASE))
        
        # ODS styling and options (separate statements, not inline with file=)
        ods_styling = len(re.findall(r'^\s*ods\s+(title|footnote|select|exclude|proctitle)\b', code_no_comments, re.IGNORECASE | re.MULTILINE))
        
        # Advanced ODS: templates, graphs, multiple formats
        ods_templates = len(re.findall(r'\bods\s+(template|tagsets|markup|path)\b', code_no_comments, re.IGNORECASE))
        ods_advanced = len(re.findall(r'\bods\s+(excel|powerpoint|pdf|rtf|printer|csvall|json|xmlmap)\b', code_no_comments, re.IGNORECASE))
        ods_graph = len(re.findall(r'\bods\s+(graphics?|graph)\b', code_no_comments, re.IGNORECASE))
        
        # Custom ODS and macros
        ods_custom = len(re.findall(r'%ods|%output|%report|ods\s+layout', code_no_comments, re.IGNORECASE))
        
        # ODS document and other advanced features
        ods_document = len(re.findall(r'\bods\s+(document|results|preferences)\b', code_no_comments, re.IGNORECASE))
        
        # Multiple output destinations (more than just open/close)
        ods_total_statements = ods_basic + ods_advanced + ods_templates + ods_graph
        
        score = 1  # Simple: no ODS
        if ods_basic > 0 and ods_total_statements <= 2:
            score = 2  # Medium: basic ODS (HTML, LISTING) - simple open/close with file=
        if ods_styling > 0 or ods_advanced > 0 or ods_graph > 0 or ods_custom > 0 or ods_total_statements > 2 or ods_document > 0:
            score = 3  # Complex: ODS with styling, multiple destinations, custom ODS
        if ods_templates > 0 or ods_advanced > 2 or ods_graph > 2 or ods_custom > 2:
            score = 4  # Very Complex: ODS templates, graphs, multiple/custom destinations, advanced ODS options
        
        self.ods_output_delivery = score

        # --- 10. ERROR HANDLING & OPTIMIZATION ---
        # Considers: error handling, performance tuning, optimization techniques
        
        # Basic error handling
        if_syserr = len(re.findall(r'%if\s+&syserr|%if\s+&sqlrc|if\s+_error_', code_no_comments, re.IGNORECASE))
        abort_stmt_count = len(re.findall(r'%abort|abort\s+', code_no_comments, re.IGNORECASE))
        
        # Macro-based error handling
        macro_error = len(re.findall(r'%macro\s+\w*error|%macro\s+\w*fail|rcset|rcsetds|call\s+symput.*error|call\s+symput.*rc', code_no_comments, re.IGNORECASE))
        
        # Try-catch patterns in macros
        try_catch = len(re.findall(r'try|catch|onerror|%label|%goto.*error', code_no_comments, re.IGNORECASE))
        
        # Performance optimization
        keep_drop = len(re.findall(r'\b(keep|drop)\s*=', code_no_comments, re.IGNORECASE))
        where_stmt = len(re.findall(r'\bwhere\s+', code_no_comments, re.IGNORECASE))
        compress_opt = len(re.findall(r'\bcompress\s*=', code_no_comments, re.IGNORECASE))
        index_opt = len(re.findall(r'\bindex\s*=|proc\s+datasets.*index', code_no_comments, re.IGNORECASE))
        
        # Advanced optimization
        hash_opt = len(re.findall(r'\bhash\s+\w+', code_no_comments, re.IGNORECASE))
        sort_nodupkey = len(re.findall(r'proc\s+sort.*nodupkey', code_no_comments, re.IGNORECASE))
        parallel_opt = len(re.findall(r'\bthreads\s*=|parallel\s*=|cpucount|nothreads', code_no_comments, re.IGNORECASE))
        
        # Performance macros
        perf_macro = len(re.findall(r'%optimize|%performance|%benchmark|%timer', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no error handling/tuning
        if if_syserr > 0 or abort_stmt_count > 0 or keep_drop > 2 or where_stmt > 2:
            score = 2  # Medium: basic %IF %THEN %ABORT, KEEP/DROP
        if abort_stmt_count > 2 or macro_error > 0 or compress_opt > 0 or index_opt > 0 or try_catch > 0:
            score = 3  # Complex: multiple ABORTs, WHERE, COMPRESS, SORT, INDEX, try/catch in macros
        if macro_error > 2 or try_catch > 2 or hash_opt > 0 or parallel_opt > 0 or perf_macro > 0 or (compress_opt > 2 and index_opt > 2):
            score = 4  # Very Complex: robust error handling, hash, memory tuning, parallel, advanced macro error handling
        
        self.error_handling_optimization = score

        # --- CYCLOMATIC COMPLEXITY ---
        self.cyclomatic = self._calculate_cyclomatic_complexity(code_no_comments)

    def _remove_comments(self, code: str) -> str:
        """
        Remove SAS comments from code for accurate analysis.
        Handles both block comments (/* */) and single-line comments (* ;).
        """
        # Remove block comments /* ... */
        code_no_block = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        
        # Remove single-line comments: lines starting with * and ending with ;
        code_no_single = re.sub(r'^\s*\*[^;]*;\s*$', '', code_no_block, flags=re.MULTILINE)
        
        return code_no_single

    def _get_nesting_level(self, code: str) -> int:
        """
        Calculate maximum nesting depth of control structures.
        Considers: DO/END blocks, %MACRO/%MEND, PROC/RUN, DATA/RUN
        """
        stack = []
        max_depth = 0
        
        for line in code.splitlines():
            line_upper = line.upper().strip()
            
            # Opening keywords
            if re.search(r'\b(DO|%MACRO|PROC|DATA)\b', line, re.IGNORECASE):
                stack.append(1)
                max_depth = max(max_depth, len(stack))
            
            # Closing keywords
            if re.search(r'\b(END|%MEND|RUN|QUIT)\b', line, re.IGNORECASE):
                if stack:
                    stack.pop()
        
        return max_depth

    def _calculate_cyclomatic_complexity(self, code: str) -> int:
        """
        Calculate cyclomatic complexity (McCabe metric).
        Counts decision points: IF, ELSE IF, SELECT WHEN, DO loops, logical operators
        """
        branches = 0
        
        # Conditional statements
        branches += len(re.findall(r'\bif\b', code, re.IGNORECASE))
        branches += len(re.findall(r'\belse\s+if\b', code, re.IGNORECASE))
        branches += len(re.findall(r'%if\b', code, re.IGNORECASE))
        
        # CASE/SELECT statements
        branches += len(re.findall(r'\b(select|case)\s+when\b', code, re.IGNORECASE))
        
        # Loops
        branches += len(re.findall(r'\bdo\s+(while|until|\w+\s*=)', code, re.IGNORECASE))
        branches += len(re.findall(r'%do\b', code, re.IGNORECASE))
        
        # Logical operators (AND/OR add complexity)
        branches += len(re.findall(r'\b(and|or)\b', code, re.IGNORECASE))
        branches += len(re.findall(r'&&|\|\|', code))
        
        # Cyclomatic = branches + 1 (minimum is 1 for sequential code)
        return max(1, branches + 1)

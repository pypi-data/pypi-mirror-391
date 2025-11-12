# src/code_analyzer/analyzers/python_analyzer.py
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


class PythonAnalyzer(AnalyzerBase):
    """
    Python code complexity analyzer with enterprise metrics integration.
    
    Evaluates Python scripts across 10 dimensions, each scored 1-4:
    - 1: Simple
    - 2: Medium
    - 3: Complex
    - 4: Very Complex
    
    Uses hybrid approach:
    - Config weights override registry defaults
    - Enterprise validation via metrics module
    - Standardized 0-100 scoring system
    """
    language = "python"
    
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
        """Analyze Python source code and return complexity metrics."""
        include_cyclomatic = self.config.get("include_cyclomatic", False)
        
        # If code is None or empty, try to read from file path
        if not code and path and path != "<string>":
            file_content = read_file_if_exists(path)
            if file_content:
                code = file_content
        
        # Run complexity analysis
        analyzer = PythonComplexity()
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
    

class PythonComplexity:
    """
    Enterprise-grade Python complexity analyzer with comprehensive pattern detection.
    Each metric is scored 1 (Simple) to 4 (Very Complex) based on Python-specific patterns.
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
        
        # Remove comments for accurate pattern matching
        code_no_comments = self._remove_comments(code)
        
        # Calculate nesting depth
        nesting_level = self._get_nesting_level(code_no_comments)

        # --- 1. SCRIPT SIZE & STRUCTURE ---
        # Enhanced: lines, classes, functions, methods, modules
        lines = len([line for line in code.split('\n') if line.strip() and not line.strip().startswith('#')])
        
        # Object-oriented constructs
        classes = len(re.findall(r'^\s*class\s+\w+', code, re.MULTILINE))
        functions = len(re.findall(r'^\s*def\s+\w+', code, re.MULTILINE))
        methods = len(re.findall(r'^\s+def\s+\w+', code, re.MULTILINE))
        
        # TIER 1: Advanced Python constructs
        decorators = len(re.findall(r'@\w+', code))
        generators = len(re.findall(r'\byield\b', code))
        context_managers = len(re.findall(r'\bwith\s+\w+', code))
        
        # TIER 2: Enterprise constructs
        metaclasses = len(re.findall(r'metaclass\s*=', code))
        dataclasses = len(re.findall(r'@dataclass', code))
        type_hints = len(re.findall(r':\s*\w+(\[\w+\])?', code))
        
        # TIER 3: Modern Python features (3.8+)
        pattern_matching = len(re.findall(r'\bmatch\s+\w+', code))
        walrus_operator = len(re.findall(r':=', code))
        
        score = 1  # Simple: small script
        if lines > 100 or functions > 2 or classes > 0 or decorators > 0 or nesting_level > 1:
            score = 2  # Medium: moderate size, functions, classes, decorators, basic nesting
        if lines > 500 or classes > 2 or methods > 5 or generators > 0 or context_managers > 0 or type_hints > 5 or nesting_level > 3:
            score = 3  # Complex: large, multiple classes, generators, context managers, type hints, deep nesting
        if lines > 2000 or classes > 5 or methods > 15 or metaclasses > 0 or pattern_matching > 0 or dataclasses > 3 or nesting_level > 5:
            score = 4  # Very Complex: very large, many classes, metaclasses, pattern matching, dataclasses, very deep nesting
        
        self.script_size_structure = score

        # --- 2. DEPENDENCY FOOTPRINT ---
        # Enhanced: imports, packages, external libraries
        import_statements = len(re.findall(r'^\s*(import|from)\s+\w+', code, re.MULTILINE))
        from_imports = len(re.findall(r'^\s*from\s+\w+', code, re.MULTILINE))
        
        # Third-party library indicators
        common_libs = len(re.findall(r'\b(numpy|pandas|requests|flask|django|tensorflow|torch|scikit|matplotlib|seaborn)\b', code, re.IGNORECASE))
        
        # Package structure indicators
        init_files = len(re.findall(r'__init__\.py', code))
        relative_imports = len(re.findall(r'from\s+\.', code))
        
        # TIER 2: Advanced import patterns
        dynamic_imports = len(re.findall(r'importlib|__import__', code))
        star_imports = len(re.findall(r'from\s+\w+\s+import\s+\*', code))
        
        score = 1  # Simple: few or no imports
        if import_statements > 3 or from_imports > 2 or common_libs > 0:
            score = 2  # Medium: several imports, common libraries
        if import_statements > 8 or relative_imports > 0 or common_libs > 3 or dynamic_imports > 0:
            score = 3  # Complex: many imports, relative imports, many libraries, dynamic imports
        if import_statements > 15 or star_imports > 0 or common_libs > 8 or (relative_imports > 3 and dynamic_imports > 0):
            score = 4  # Very Complex: extensive imports, star imports, many external dependencies
        
        self.dependency_footprint = score

        # --- 3. ANALYTICS DEPTH ---
        # Enhanced: comprehensions, functional programming, data analysis
        list_comprehensions = len(re.findall(r'\[.*for.*in.*\]', code))
        dict_comprehensions = len(re.findall(r'\{.*:.*for.*in.*\}', code))
        set_comprehensions = len(re.findall(r'\{.*for.*in.*\}', code))
        generator_expressions = len(re.findall(r'\(.*for.*in.*\)', code))
        
        # Functional programming
        lambda_functions = len(re.findall(r'\blambda\s+', code))
        map_filter_reduce = len(re.findall(r'\b(map|filter|reduce)\s*\(', code))
        
        # Data analysis patterns
        data_science = len(re.findall(r'\b(pd\.|np\.|plt\.|sns\.)', code))
        numpy_ops = len(re.findall(r'\b(array|matrix|dot|reshape|transpose)\b', code))
        
        # TIER 2: Advanced analytics
        statistical_ops = len(re.findall(r'\b(mean|std|var|corr|groupby|agg|pivot|melt)\b', code))
        machine_learning = len(re.findall(r'\b(fit|predict|transform|score|cross_val|GridSearch)\b', code))
        
        # TIER 3: Advanced data processing
        async_generators = len(re.findall(r'async\s+def.*yield', code, re.DOTALL))
        
        score = 1  # Simple: basic operations
        if list_comprehensions > 0 or lambda_functions > 0 or data_science > 0:
            score = 2  # Medium: comprehensions, lambda, basic data science
        if (list_comprehensions + dict_comprehensions) > 3 or map_filter_reduce > 0 or numpy_ops > 0 or statistical_ops > 0:
            score = 3  # Complex: multiple comprehensions, functional programming, statistical operations
        if generator_expressions > 2 or machine_learning > 0 or async_generators > 0 or statistical_ops > 5:
            score = 4  # Very Complex: generator expressions, ML, async generators, extensive analytics
        
        self.analytics_depth = score

        # --- 4. SQL & REPORTING LOGIC ---
        # Enhanced: database operations, ORM usage, data queries
        sql_keywords = len(re.findall(r'\b(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)\b', code, re.IGNORECASE))
        
        # Database connection patterns
        db_connections = len(re.findall(r'\b(connect|cursor|execute|fetchall|fetchone)\b', code))
        
        # ORM patterns
        orm_patterns = len(re.findall(r'\b(Model|Table|Column|relationship|query|filter|join)\b', code))
        sqlalchemy = len(re.findall(r'\b(sqlalchemy|session|engine|metadata)\b', code, re.IGNORECASE))
        django_orm = len(re.findall(r'\b(objects\.filter|objects\.get|Q\(|F\()\b', code))
        
        # Data querying libraries
        pandas_query = len(re.findall(r'\b(query|loc|iloc|groupby|merge|join)\b', code))
        
        # TIER 2: Advanced querying
        complex_queries = len(re.findall(r'\b(subquery|union|having|window)\b', code, re.IGNORECASE))
        query_optimization = len(re.findall(r'\b(index|explain|analyze|vacuum)\b', code, re.IGNORECASE))
        
        score = 1  # Simple: no database operations
        if sql_keywords > 0 or db_connections > 0 or pandas_query > 3:
            score = 2  # Medium: basic SQL, database connections, pandas queries
        if orm_patterns > 0 or sqlalchemy > 0 or django_orm > 0 or complex_queries > 0:
            score = 3  # Complex: ORM usage, complex queries
        if (orm_patterns > 5 and sql_keywords > 5) or query_optimization > 0 or complex_queries > 3:
            score = 4  # Very Complex: extensive ORM + SQL, query optimization
        
        self.sql_reporting_logic = score

        # --- 5. TRANSFORMATION LOGIC ---
        # Enhanced: data processing, serialization, format conversion
        json_operations = len(re.findall(r'\b(json\.|loads|dumps)\b', code))
        xml_operations = len(re.findall(r'\b(xml\.|etree|BeautifulSoup|lxml)\b', code))
        csv_operations = len(re.findall(r'\b(csv\.|read_csv|to_csv)\b', code))
        
        # Data transformations
        string_operations = len(re.findall(r'\.(strip|split|join|replace|format|encode|decode)', code))
        data_conversion = len(re.findall(r'\b(int|float|str|bool|list|dict|set|tuple)\s*\(', code))
        
        # TIER 1: Advanced transformations
        regex_operations = len(re.findall(r'\bre\.(match|search|findall|sub|compile)', code))
        datetime_operations = len(re.findall(r'\b(datetime|strftime|strptime|timedelta)\b', code))
        
        # TIER 2: Enterprise data processing
        serialization = len(re.findall(r'\b(pickle|marshal|shelve|dill)\b', code))
        compression = len(re.findall(r'\b(gzip|zlib|bz2|lzma)\b', code))
        encoding = len(re.findall(r'\b(base64|hashlib|hmac|cryptography)\b', code))
        
        # TIER 3: Advanced data pipelines
        streaming = len(re.findall(r'\b(kafka|redis|celery|queue)\b', code, re.IGNORECASE))
        
        score = 1  # Simple: basic operations
        if json_operations > 0 or string_operations > 3 or data_conversion > 5:
            score = 2  # Medium: JSON processing, string operations, basic conversions
        if regex_operations > 0 or xml_operations > 0 or datetime_operations > 0 or serialization > 0:
            score = 3  # Complex: regex, XML, datetime, serialization
        if compression > 0 or encoding > 0 or streaming > 0 or (serialization > 2 and xml_operations > 2):
            score = 4  # Very Complex: compression, encryption, streaming, extensive serialization
        
        self.transformation_logic = score

        # --- 6. UTILITY COMPLEXITY ---
        # Enhanced: functions, classes, inheritance, design patterns
        inheritance = len(re.findall(r'class\s+\w+\s*\([^)]+\)', code))
        multiple_inheritance = len(re.findall(r'class\s+\w+\s*\([^,)]+,[^)]+\)', code))
        
        # Method types
        static_methods = len(re.findall(r'@staticmethod', code))
        class_methods = len(re.findall(r'@classmethod', code))
        properties = len(re.findall(r'@property', code))
        
        # TIER 1: Advanced OOP
        abstract_classes = len(re.findall(r'\bABC\b|@abstractmethod', code))
        magic_methods = len(re.findall(r'def\s+__(init|str|repr|len|getitem|setitem|call)__', code))
        
        # TIER 2: Design patterns
        descriptors = len(re.findall(r'__get__|__set__|__delete__', code))
        context_manager_impl = len(re.findall(r'__enter__|__exit__', code))
        singleton_pattern = len(re.findall(r'__new__|_instance', code))
        
        # TIER 3: Advanced patterns
        protocols = len(re.findall(r'\bProtocol\b|@runtime_checkable', code))
        generics = len(re.findall(r'\bTypeVar\b|Generic\[', code))
        
        score = 1  # Simple: basic functions
        if classes > 0 or decorators > 2 or static_methods > 0 or properties > 0:
            score = 2  # Medium: classes, decorators, static methods, properties
        if inheritance > 0 or abstract_classes > 0 or magic_methods > 2 or context_manager_impl > 0:
            score = 3  # Complex: inheritance, abstract classes, magic methods, context managers
        if multiple_inheritance > 0 or descriptors > 0 or protocols > 0 or generics > 0:
            score = 4  # Very Complex: multiple inheritance, descriptors, protocols, generics
        
        self.utility_complexity = score

        # --- 7. EXECUTION CONTROL ---
        # Enhanced: exception handling, async programming, threading
        try_except = len(re.findall(r'\btry\s*:', code))
        custom_exceptions = len(re.findall(r'class\s+\w+\s*\(\s*\w*Exception', code))
        
        # Async programming
        async_def = len(re.findall(r'\basync\s+def\b', code))
        await_calls = len(re.findall(r'\bawait\s+', code))
        async_context = len(re.findall(r'\basync\s+with\b', code))
        
        # TIER 2: Concurrent programming
        threading = len(re.findall(r'\bthreading\b|Thread\(|Lock\(', code))
        multiprocessing = len(re.findall(r'\bmultiprocessing\b|Process\(|Pool\(', code))
        asyncio_patterns = len(re.findall(r'\basyncio\.|gather|create_task', code))
        
        # TIER 3: Advanced concurrency
        futures = len(re.findall(r'\bconcurrent\.futures\b|ThreadPoolExecutor|ProcessPoolExecutor', code))
        async_generators_control = len(re.findall(r'async\s+def.*yield', code, re.DOTALL))
        
        score = 1  # Simple: basic execution
        if try_except > 0 or async_def > 0:
            score = 2  # Medium: exception handling, async functions
        if custom_exceptions > 0 or threading > 0 or asyncio_patterns > 0 or async_context > 0:
            score = 3  # Complex: custom exceptions, threading, asyncio, async context
        if multiprocessing > 0 or futures > 0 or (async_def > 3 and await_calls > 5):
            score = 4  # Very Complex: multiprocessing, futures, extensive async programming
        
        self.execution_control = score

        # --- 8. FILE I/O & EXTERNAL INTEGRATION ---
        # Enhanced: file operations, network, APIs, external services
        file_operations = len(re.findall(r'\bopen\(|with\s+open\(|pathlib|os\.path', code))
        
        # Network operations
        http_requests = len(re.findall(r'\brequests\.|urllib|httpx|aiohttp', code))
        web_frameworks = len(re.findall(r'\bflask|django|fastapi|tornado|bottle', code, re.IGNORECASE))
        
        # API integrations
        rest_apis = len(re.findall(r'\b(GET|POST|PUT|DELETE|PATCH)\b|@app\.route|api_key', code))
        json_apis = len(re.findall(r'\.json\(\)|application/json', code))
        
        # TIER 2: Advanced integrations
        database_drivers = len(re.findall(r'\b(psycopg2|pymongo|redis|elasticsearch)\b', code))
        cloud_services = len(re.findall(r'\b(boto3|azure|gcp|aws)\b', code, re.IGNORECASE))
        message_queues = len(re.findall(r'\b(kafka|rabbitmq|celery|sqs)\b', code, re.IGNORECASE))
        
        # TIER 3: Enterprise integrations
        microservices = len(re.findall(r'\b(grpc|protobuf|consul|etcd)\b', code, re.IGNORECASE))
        monitoring = len(re.findall(r'\b(prometheus|grafana|datadog|newrelic)\b', code, re.IGNORECASE))
        
        score = 1  # Simple: basic operations
        if file_operations > 0 or http_requests > 0:
            score = 2  # Medium: file I/O, HTTP requests
        if web_frameworks > 0 or database_drivers > 0 or rest_apis > 0 or cloud_services > 0:
            score = 3  # Complex: web frameworks, databases, APIs, cloud services
        if message_queues > 0 or microservices > 0 or monitoring > 0 or (cloud_services > 2 and rest_apis > 3):
            score = 4  # Very Complex: message queues, microservices, monitoring, extensive cloud integration
        
        self.file_io_external_integration = score

        # --- 9. ODS OUTPUT DELIVERY ---
        # Enhanced: output formatting, logging, reporting, templates
        print_statements = len(re.findall(r'\bprint\(', code))
        logging_operations = len(re.findall(r'\blogging\.|logger\.|log\(', code))
        
        # Formatting and templates
        string_formatting = len(re.findall(r'\.format\(|f".*{.*}"|\%.*\%', code))
        template_engines = len(re.findall(r'\bjinja2|mako|django.*template', code, re.IGNORECASE))
        
        # Data visualization
        plotting = len(re.findall(r'\bmatplotlib|seaborn|plotly|bokeh', code, re.IGNORECASE))
        charts = len(re.findall(r'\.plot\(|\.show\(|\.savefig\(', code))
        
        # TIER 2: Advanced output
        report_generation = len(re.findall(r'\breportlab|fpdf|openpyxl|xlswriter', code, re.IGNORECASE))
        email_delivery = len(re.findall(r'\bsmtplib|email\.|sendmail', code))
        
        # TIER 3: Enterprise reporting
        dashboard_frameworks = len(re.findall(r'\bdash|streamlit|gradio|panel', code, re.IGNORECASE))
        business_intelligence = len(re.findall(r'\btableau|powerbi|qlik', code, re.IGNORECASE))
        
        score = 1  # Simple: basic output
        if print_statements > 3 or logging_operations > 0 or string_formatting > 3:
            score = 2  # Medium: formatted output, logging
        if template_engines > 0 or plotting > 0 or report_generation > 0 or email_delivery > 0:
            score = 3  # Complex: templates, plotting, report generation, email
        if dashboard_frameworks > 0 or business_intelligence > 0 or (plotting > 3 and report_generation > 0):
            score = 4  # Very Complex: dashboards, BI tools, extensive visualization and reporting
        
        self.ods_output_delivery = score

        # --- 10. ERROR HANDLING & OPTIMIZATION ---
        # Enhanced: exception handling, logging, performance optimization
        exception_handling = try_except  # Reuse from execution_control
        specific_exceptions = len(re.findall(r'except\s+\w+Exception', code))
        finally_blocks = len(re.findall(r'\bfinally\s*:', code))
        
        # Logging and monitoring
        log_levels = len(re.findall(r'\.(debug|info|warning|error|critical)\(', code))
        error_tracking = len(re.findall(r'\bsentry|rollbar|bugsnag', code, re.IGNORECASE))
        
        # TIER 2: Performance optimization
        profiling = len(re.findall(r'\bcProfile|line_profiler|memory_profiler', code))
        caching = len(re.findall(r'\b@lru_cache|@cache|redis.*cache|memcached', code))
        optimization = len(re.findall(r'\bnumpy|numba|cython|joblib', code, re.IGNORECASE))
        
        # TIER 3: Advanced optimization
        memory_management = len(re.findall(r'\b__slots__|gc\.|weakref|memory_map', code))
        parallel_processing = len(re.findall(r'\bmultiprocessing\.Pool|concurrent\.futures|joblib\.Parallel', code))
        
        score = 1  # Simple: basic or no error handling
        if exception_handling > 0 or log_levels > 0:
            score = 2  # Medium: basic exception handling, logging
        if specific_exceptions > 0 or error_tracking > 0 or caching > 0 or optimization > 0:
            score = 3  # Complex: specific exception handling, error tracking, caching, optimization
        if profiling > 0 or memory_management > 0 or parallel_processing > 0 or (optimization > 3 and caching > 2):
            score = 4  # Very Complex: profiling, memory management, parallel processing, extensive optimization
        
        self.error_handling_optimization = score

        # Calculate cyclomatic complexity
        self.cyclomatic = self._calculate_cyclomatic_complexity(code_no_comments)

    def _remove_comments(self, code: str) -> str:
        """Remove Python comments and docstrings for accurate analysis."""
        # Remove single-line comments
        lines = code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Find # that's not in a string
            in_string = False
            quote_char = None
            escaped = False
            
            for i, char in enumerate(line):
                if escaped:
                    escaped = False
                    continue
                    
                if char == '\\':
                    escaped = True
                    continue
                    
                if char in ('"', "'") and not in_string:
                    in_string = True
                    quote_char = char
                elif char == quote_char and in_string:
                    in_string = False
                    quote_char = None
                elif char == '#' and not in_string:
                    line = line[:i]
                    break
            
            cleaned_lines.append(line)
        
        code_no_comments = '\n'.join(cleaned_lines)
        
        # Remove docstrings (simplified approach)
        code_no_comments = re.sub(r'""".*?"""', '', code_no_comments, flags=re.DOTALL)
        code_no_comments = re.sub(r"'''.*?'''", '', code_no_comments, flags=re.DOTALL)
        
        return code_no_comments

    def _get_nesting_level(self, code: str) -> int:
        """
        Calculate the maximum nesting depth of control structures in Python code.
        """
        lines = code.split('\n')
        max_depth = 0
        current_depth = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
                
            # Calculate indentation
            indent = len(line) - len(line.lstrip())
            
            # Check for control structures
            if re.match(r'^\s*(if|elif|else|for|while|try|except|finally|with|def|class|async\s+def|async\s+with):', line):
                current_depth = (indent // 4) + 1  # Assuming 4-space indentation
                max_depth = max(max_depth, current_depth)
        
        return max_depth

    def _calculate_cyclomatic_complexity(self, code: str) -> int:
        """
        Calculate cyclomatic complexity for Python.
        
        Counts decision points: if, elif, while, for, except, and, or, comprehensions
        Cyclomatic Complexity = decision points + 1
        """
        # Decision points
        if_count = len(re.findall(r'\bif\b', code))
        elif_count = len(re.findall(r'\belif\b', code))
        while_count = len(re.findall(r'\bwhile\b', code))
        for_count = len(re.findall(r'\bfor\b', code))
        except_count = len(re.findall(r'\bexcept\b', code))
        
        # Logical operators add complexity
        and_or_count = len(re.findall(r'\b(and|or)\b', code))
        
        # Comprehensions add complexity
        comprehension_count = len(re.findall(r'\[.*for.*in.*\]|\{.*for.*in.*\}|\(.*for.*in.*\)', code))
        
        decision_points = if_count + elif_count + while_count + for_count + except_count + and_or_count + comprehension_count
        
        return max(1, decision_points + 1)
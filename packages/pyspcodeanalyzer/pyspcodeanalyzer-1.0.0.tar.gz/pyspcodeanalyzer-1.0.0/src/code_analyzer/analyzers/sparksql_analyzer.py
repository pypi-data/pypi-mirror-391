# src/code_analyzer/analyzers/sparksql_analyzer.py
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


class SparkSQLAnalyzer(AnalyzerBase):
    """
    SparkSQL code complexity analyzer with enterprise metrics integration.
    
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
    language = "sparksql"
    
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
        """Analyze SparkSQL source code and return complexity metrics."""
        include_cyclomatic = self.config.get("include_cyclomatic", False)
        
        # If code is None or empty, try to read from file path
        if not code and path and path != "<string>":
            file_content = read_file_if_exists(path)
            if file_content:
                code = file_content
        
        # Run complexity analysis
        analyzer = SparkSQLComplexity()
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
    

class SparkSQLComplexity:
    """
    Enterprise-grade SparkSQL complexity analyzer with comprehensive pattern detection.
    Each metric is scored 1 (Simple) to 4 (Very Complex) based on SparkSQL-specific patterns.
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
        # Enhanced: lines, DataFrames, SQL queries, transformations, streaming
        lines = len([line for line in code.split('\n') if line.strip()])
        
        # DataFrame/Dataset operations
        dataframes = len(re.findall(r'\.(?:toDF|createDataFrame|read|sql)\s*\(', code_no_comments, re.IGNORECASE))
        spark_session = len(re.findall(r'spark\.(?:sql|read|range|table)', code_no_comments, re.IGNORECASE))
        
        # SQL queries
        sql_queries = len(re.findall(r'spark\.sql\s*\(|\.sql\s*\(', code_no_comments, re.IGNORECASE))
        create_view = len(re.findall(r'\.createOrReplaceTempView\s*\(|CREATE\s+(?:OR\s+REPLACE\s+)?(?:TEMP\s+|GLOBAL\s+TEMP\s+)?VIEW', code_no_comments, re.IGNORECASE))
        
        # Transformations and actions
        transformations = len(re.findall(r'\.(?:select|filter|where|groupBy|orderBy|join|union|distinct|drop|withColumn|withColumnRenamed)', code_no_comments, re.IGNORECASE))
        actions = len(re.findall(r'\.(?:collect|show|count|first|take|write|save)', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Streaming
        streaming = len(re.findall(r'\.(?:readStream|writeStream|trigger|outputMode)', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Delta Lake
        delta_operations = len(re.findall(r'\.format\s*\(\s*["\']delta["\']|DeltaTable\.|\.merge\s*\(', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic operations
        if lines > 100 or dataframes > 1 or sql_queries > 0 or transformations > 3 or nesting_level > 1:
            score = 2  # Medium: moderate DataFrames, SQL, basic nesting
        if lines > 500 or dataframes > 3 or sql_queries > 3 or transformations > 10 or streaming > 0 or nesting_level > 3:
            score = 3  # Complex: multiple DataFrames, streaming, deep nesting
        if lines > 2000 or dataframes > 8 or sql_queries > 8 or transformations > 25 or streaming > 3 or delta_operations > 0 or nesting_level > 5:
            score = 4  # Very Complex: large scripts, extensive operations, Delta Lake, very deep nesting
        
        self.script_size_structure = score

        # --- 2. DEPENDENCY FOOTPRINT ---
        # Enhanced: data sources, external systems, tables, Delta tables, catalogs
        file_reads = len(re.findall(r'\.(?:text|csv|json|parquet|orc|avro|delta|jdbc)', code_no_comments, re.IGNORECASE))
        external_sources = len(re.findall(r'\.option\s*\(\s*["\'](?:url|path|host|driver)', code_no_comments, re.IGNORECASE))
        
        # Database connections
        jdbc_connections = len(re.findall(r'\.format\s*\(\s*["\']jdbc["\']|\.jdbc\s*\(', code_no_comments, re.IGNORECASE))
        
        # Catalogs and metastores
        catalog_refs = len(re.findall(r'spark\.catalog\.|SHOW\s+(?:DATABASES|TABLES|COLUMNS)', code_no_comments, re.IGNORECASE))
        hive_tables = len(re.findall(r'spark\.table\s*\(|FROM\s+\w+\.\w+', code_no_comments, re.IGNORECASE))
        
        # External systems
        kafka_streams = len(re.findall(r'\.format\s*\(\s*["\']kafka["\']', code_no_comments, re.IGNORECASE))
        cloud_storage = len(re.findall(r's3a?://|gs://|abfss?://|wasbs?://', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Delta Lake dependencies
        delta_tables = len(re.findall(r'DeltaTable\.forPath|DeltaTable\.forName', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: single source
        if file_reads > 1 or external_sources > 0 or catalog_refs > 0:
            score = 2  # Medium: multiple files, basic external sources
        if jdbc_connections > 0 or hive_tables > 0 or kafka_streams > 0 or cloud_storage > 0:
            score = 3  # Complex: databases, Hive, streaming sources, cloud storage
        if external_sources > 3 or jdbc_connections > 2 or delta_tables > 0 or (kafka_streams > 0 and cloud_storage > 0):
            score = 4  # Very Complex: multiple external systems, Delta tables, hybrid architectures
        
        self.dependency_footprint = score

        # --- 3. ANALYTICS DEPTH ---
        # Enhanced: aggregations, window functions, ML operations, graph processing
        aggregations = len(re.findall(r'\.(?:agg|groupBy|sum|count|avg|max|min|collect_list|collect_set)', code_no_comments, re.IGNORECASE))
        window_functions = len(re.findall(r'Window\.|row_number\s*\(\)|rank\s*\(\)|dense_rank\s*\(\)|lag\s*\(|lead\s*\(', code_no_comments, re.IGNORECASE))
        
        # Statistical functions
        statistical = len(re.findall(r'\.(?:corr|cov|approxQuantile|freqItems|crosstab)', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Machine Learning
        mllib_operations = len(re.findall(r'from\s+pyspark\.ml\.|MLlib|Pipeline\s*\(|Estimator|Transformer', code_no_comments, re.IGNORECASE))
        ml_algorithms = len(re.findall(r'(?:LinearRegression|LogisticRegression|RandomForest|GBT|KMeans|ALS)', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Graph processing
        graphx_operations = len(re.findall(r'GraphX|\.vertices|\.edges|\.triplets|pageRank|connectedComponents', code_no_comments, re.IGNORECASE))
        
        # Complex SQL analytics
        complex_sql = len(re.findall(r'(?:ROLLUP|CUBE|GROUPING\s+SETS|PIVOT|UNPIVOT)', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic operations
        if aggregations > 0 or window_functions > 0:
            score = 2  # Medium: aggregations, window functions
        if statistical > 0 or mllib_operations > 0 or complex_sql > 0 or window_functions > 3:
            score = 3  # Complex: statistics, ML, advanced SQL
        if ml_algorithms > 0 or graphx_operations > 0 or mllib_operations > 3:
            score = 4  # Very Complex: ML algorithms, graph processing, advanced analytics
        
        self.analytics_depth = score

        # --- 4. SQL REPORTING LOGIC ---
        # Enhanced: SQL complexity, views, CTEs, subqueries
        select_statements = len(re.findall(r'\bSELECT\b', code_no_comments, re.IGNORECASE))
        joins = len(re.findall(r'\.join\s*\(|(?:INNER|LEFT|RIGHT|FULL|CROSS)\s+JOIN', code_no_comments, re.IGNORECASE))
        
        # Complex SQL constructs
        ctes = len(re.findall(r'\bWITH\s+\w+\s+AS\s*\(', code_no_comments, re.IGNORECASE))
        subqueries = len(re.findall(r'\(\s*SELECT\b', code_no_comments, re.IGNORECASE))
        unions = len(re.findall(r'\bUNION\s+(?:ALL\s+)?', code_no_comments, re.IGNORECASE))
        
        # Views and temporary tables
        temp_views = len(re.findall(r'createOrReplaceTempView|CREATE\s+(?:OR\s+REPLACE\s+)?(?:TEMP\s+)?VIEW', code_no_comments, re.IGNORECASE))
        
        # Query optimization hints
        hints = len(re.findall(r'/\*\+\s*(?:BROADCAST|MERGE|SHUFFLE_HASH|SORT_MERGE)', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic SELECT
        if select_statements > 1 or joins > 0 or temp_views > 0:
            score = 2  # Medium: multiple queries, joins, views
        if ctes > 0 or subqueries > 0 or unions > 0 or joins > 3 or hints > 0:
            score = 3  # Complex: CTEs, subqueries, multiple joins, optimization hints
        if ctes > 2 or subqueries > 3 or joins > 6 or (unions > 1 and ctes > 0):
            score = 4  # Very Complex: complex nested queries, multiple CTEs and subqueries
        
        self.sql_reporting_logic = score

        # --- 5. TRANSFORMATION LOGIC ---
        # Enhanced: DataFrame transformations, ETL operations, data quality
        data_transforms = len(re.findall(r'\.(?:withColumn|withColumnRenamed|drop|cast|alias)', code_no_comments, re.IGNORECASE))
        data_cleaning = len(re.findall(r'\.(?:na\.drop|na\.fill|dropDuplicates|dropna|fillna)', code_no_comments, re.IGNORECASE))
        
        # Complex transformations
        pivoting = len(re.findall(r'\.(?:pivot|unpivot)', code_no_comments, re.IGNORECASE))
        exploding = len(re.findall(r'\.(?:explode|flatten|split)', code_no_comments, re.IGNORECASE))
        
        # Data type operations
        type_operations = len(re.findall(r'\.(?:cast|astype)|(?:StringType|IntegerType|DoubleType|ArrayType|StructType)', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Advanced ETL
        complex_etl = len(re.findall(r'\.(?:coalesce|repartition|partitionBy)', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Delta Lake operations
        delta_etl = len(re.findall(r'\.merge\s*\(|\.vacuum\s*\(|\.optimize\s*\(', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: basic transformations
        if data_transforms > 0 or data_cleaning > 0:
            score = 2  # Medium: column operations, data cleaning
        if pivoting > 0 or exploding > 0 or type_operations > 3 or complex_etl > 0:
            score = 3  # Complex: pivoting, complex data types, partitioning
        if delta_etl > 0 or (pivoting > 0 and exploding > 0 and complex_etl > 2):
            score = 4  # Very Complex: Delta operations, multiple complex transformations
        
        self.transformation_logic = score

        # --- 6. UTILITY COMPLEXITY ---
        # Enhanced: UDFs, custom functions, broadcast variables, accumulators
        udfs = len(re.findall(r'\.udf\s*\(|@udf|spark\.udf\.register', code_no_comments, re.IGNORECASE))
        python_udfs = len(re.findall(r'def\s+\w+.*udf|pyspark\.sql\.functions\.udf', code_no_comments, re.IGNORECASE))
        
        # Custom functions and complex operations
        custom_functions = len(re.findall(r'def\s+\w+.*return|lambda\s+\w+:', code_no_comments, re.IGNORECASE))
        map_operations = len(re.findall(r'\.(?:map|flatMap|mapPartitions|foreachPartition)', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Broadcast and accumulators
        broadcast_vars = len(re.findall(r'spark\.sparkContext\.broadcast|sc\.broadcast', code_no_comments, re.IGNORECASE))
        accumulators = len(re.findall(r'spark\.sparkContext\.accumulator|sc\.accumulator', code_no_comments, re.IGNORECASE))
        
        # Advanced operations
        rdd_operations = len(re.findall(r'\.rdd\.|\.toRDD\s*\(|parallelize\s*\(', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: built-in functions only
        if custom_functions > 0 or udfs > 0:
            score = 2  # Medium: custom functions, basic UDFs
        if python_udfs > 0 or map_operations > 0 or broadcast_vars > 0 or rdd_operations > 0:
            score = 3  # Complex: Python UDFs, RDD operations, broadcast variables
        if udfs > 3 or accumulators > 0 or (broadcast_vars > 0 and map_operations > 2):
            score = 4  # Very Complex: multiple UDFs, accumulators, complex distributed operations
        
        self.utility_complexity = score

        # --- 7. EXECUTION CONTROL ---
        # Enhanced: jobs, stages, checkpoints, streaming triggers
        spark_config = len(re.findall(r'spark\.conf\.set|SparkConf\(\)', code_no_comments, re.IGNORECASE))
        
        # Checkpointing and persistence
        checkpointing = len(re.findall(r'\.checkpoint\s*\(|\.cache\s*\(|\.persist\s*\(', code_no_comments, re.IGNORECASE))
        storage_levels = len(re.findall(r'StorageLevel\.|MEMORY_ONLY|MEMORY_AND_DISK|DISK_ONLY', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Streaming control
        streaming_control = len(re.findall(r'\.trigger\s*\(|\.outputMode\s*\(|\.start\s*\(|\.awaitTermination', code_no_comments, re.IGNORECASE))
        streaming_triggers = len(re.findall(r'Trigger\.(?:ProcessingTime|Once|Continuous)', code_no_comments, re.IGNORECASE))
        
        # Job control
        job_control = len(re.findall(r'spark\.sparkContext\.setJobGroup|sc\.setJobGroup', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: default execution
        if spark_config > 0 or checkpointing > 0:
            score = 2  # Medium: configuration, caching
        if storage_levels > 0 or streaming_control > 0 or job_control > 0:
            score = 3  # Complex: custom storage, streaming control, job management
        if streaming_triggers > 0 or (checkpointing > 3 and storage_levels > 0):
            score = 4  # Very Complex: advanced streaming triggers, sophisticated caching strategies
        
        self.execution_control = score

        # --- 8. FILE I/O & EXTERNAL INTEGRATION ---
        # Enhanced: file formats, connectors, external systems
        file_formats = len(re.findall(r'\.(?:csv|json|parquet|orc|avro|text|delta)\s*\(', code_no_comments, re.IGNORECASE))
        
        # External connectors
        external_connectors = len(re.findall(r'\.format\s*\(\s*["\'](?:jdbc|kafka|elasticsearch|cassandra|mongodb)', code_no_comments, re.IGNORECASE))
        
        # Cloud storage
        cloud_integrations = len(re.findall(r'(?:s3a?|gs|abfss?)://|\.option\s*\(\s*["\'](?:aws|azure|gcp)', code_no_comments, re.IGNORECASE))
        
        # Streaming sources/sinks
        streaming_io = len(re.findall(r'readStream|writeStream|\.format\s*\(\s*["\'](?:socket|rate|console)', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Advanced integrations
        delta_io = len(re.findall(r'\.format\s*\(\s*["\']delta["\']', code_no_comments, re.IGNORECASE))
        custom_sources = len(re.findall(r'DataSourceRegister|RelationProvider', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: single file type
        if file_formats > 1 or external_connectors > 0:
            score = 2  # Medium: multiple formats, basic connectors
        if cloud_integrations > 0 or streaming_io > 0 or external_connectors > 2:
            score = 3  # Complex: cloud storage, streaming I/O, multiple connectors
        if delta_io > 0 or custom_sources > 0 or (cloud_integrations > 2 and streaming_io > 0):
            score = 4  # Very Complex: Delta Lake, custom data sources, multi-cloud streaming
        
        self.file_io_external_integration = score

        # --- 9. ODS OUTPUT DELIVERY ---
        # Enhanced: output formats, writers, streaming sinks, Delta operations
        output_formats = len(re.findall(r'\.write\.(?:csv|json|parquet|orc|avro|text|delta)', code_no_comments, re.IGNORECASE))
        write_modes = len(re.findall(r'\.mode\s*\(\s*["\'](?:overwrite|append|ignore|error)', code_no_comments, re.IGNORECASE))
        
        # Partitioning and bucketing
        partitioned_writes = len(re.findall(r'\.partitionBy\s*\(|\.bucketBy\s*\(', code_no_comments, re.IGNORECASE))
        
        # Streaming outputs
        streaming_sinks = len(re.findall(r'\.writeStream\.(?:format|outputMode|trigger)', code_no_comments, re.IGNORECASE))
        console_output = len(re.findall(r'\.format\s*\(\s*["\']console["\']|\.show\s*\(', code_no_comments, re.IGNORECASE))
        
        # Multiple outputs
        multiple_writes = len(re.findall(r'\.write\.|\.save\s*\(', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Delta Lake outputs
        delta_writes = len(re.findall(r'\.write\.format\s*\(\s*["\']delta["\']|\.write\.delta\s*\(', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: single output
        if output_formats > 0 or write_modes > 0 or console_output > 0:
            score = 2  # Medium: formatted outputs, write modes
        if partitioned_writes > 0 or streaming_sinks > 0 or multiple_writes > 3:
            score = 3  # Complex: partitioned outputs, streaming sinks, multiple outputs
        if delta_writes > 0 or (streaming_sinks > 2 and partitioned_writes > 0):
            score = 4  # Very Complex: Delta outputs, complex streaming with partitioning
        
        self.ods_output_delivery = score

        # --- 10. ERROR HANDLING & OPTIMIZATION ---
        # Enhanced: error handling, optimization, performance tuning
        try_catch = len(re.findall(r'\btry\s*:|except\s+\w+:', code_no_comments, re.IGNORECASE))
        
        # Performance optimization
        optimization_hints = len(re.findall(r'/\*\+\s*(?:BROADCAST|MERGE|SHUFFLE_HASH|SORT_MERGE|COALESCE|REPARTITION)', code_no_comments, re.IGNORECASE))
        partitioning = len(re.findall(r'\.(?:repartition|coalesce|partitionBy)\s*\(', code_no_comments, re.IGNORECASE))
        
        # Caching and persistence strategies
        caching_strategies = len(re.findall(r'\.(?:cache|persist|unpersist)\s*\(', code_no_comments, re.IGNORECASE))
        
        # TIER 2: Advanced optimization
        adaptive_query = len(re.findall(r'spark\.sql\.adaptive|AQE|spark\.serializer', code_no_comments, re.IGNORECASE))
        columnar_storage = len(re.findall(r'spark\.sql\.parquet|spark\.sql\.orc|vectorized', code_no_comments, re.IGNORECASE))
        
        # Monitoring and debugging
        monitoring = len(re.findall(r'spark\.sparkContext\.(?:statusTracker|getExecutorInfos)|explain\s*\(', code_no_comments, re.IGNORECASE))
        
        score = 1  # Simple: no optimization
        if try_catch > 0 or caching_strategies > 0:
            score = 2  # Medium: basic error handling, caching
        if optimization_hints > 0 or partitioning > 0 or adaptive_query > 0:
            score = 3  # Complex: query hints, partitioning, adaptive features
        if columnar_storage > 0 or monitoring > 0 or (optimization_hints > 2 and caching_strategies > 2):
            score = 4  # Very Complex: columnar optimization, monitoring, comprehensive tuning
        
        self.error_handling_optimization = score

        # Calculate cyclomatic complexity
        self.cyclomatic = self._calculate_cyclomatic_complexity(code_no_comments)
        
    def _remove_comments(self, code: str) -> str:
        """Remove comments from Spark SQL code for accurate analysis."""
        # Remove SQL-style comments --
        code_no_single = re.sub(r'--.*$', '', code, flags=re.MULTILINE)
        
        # Remove multi-line comments /* ... */
        code_no_multi = re.sub(r'/\*.*?\*/', '', code_no_single, flags=re.DOTALL)
        
        # Remove Python-style comments #
        code_no_python = re.sub(r'#.*$', '', code_no_multi, flags=re.MULTILINE)
        
        return code_no_python

    def _get_nesting_level(self, code: str) -> int:
        """
        Calculate the maximum nesting depth of control structures in Spark SQL code.
        """
        stack = []
        max_depth = 0

        # Patterns for opening and closing structures
        open_patterns = [
            r'\bif\s+.*:',  # Python if
            r'\bfor\s+.*:',  # Python for
            r'\bwhile\s+.*:',  # Python while
            r'\btry\s*:',  # Python try
            r'\bwith\s+.*:',  # Python with
            r'\bdef\s+\w+.*:',  # Python function
            r'\bclass\s+\w+.*:',  # Python class
            r'\(\s*SELECT\b',  # SQL subquery
            r'\bWITH\s+\w+\s+AS\s*\(',  # SQL CTE
        ]
        
        close_patterns = [
            r'^\s*$',  # Empty line (Python block end)
            r'^\s*(?:except|finally|else|elif)',  # Python exception/control
            r'\)\s*$',  # Closing parenthesis
        ]

        lines = code.splitlines()
        prev_indent = 0

        for line in lines:
            # Skip empty lines and comments
            stripped = line.strip()
            if not stripped or stripped.startswith('#') or stripped.startswith('--'):
                continue

            # Calculate indentation
            current_indent = len(line) - len(line.lstrip())

            # Check for opening patterns
            for pattern in open_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    stack.append(current_indent)
                    max_depth = max(max_depth, len(stack))
                    break

            # Check for decreased indentation (block end)
            if current_indent < prev_indent and stack:
                # Pop stack for each level of decreased indentation
                while stack and stack[-1] >= current_indent:
                    stack.pop()

            prev_indent = current_indent

        return max_depth

    def _calculate_cyclomatic_complexity(self, code: str) -> int:
        """
        Calculate cyclomatic complexity for Spark SQL code.
        
        Counts decision points in both SQL and Python code
        """
        # Python control structures
        if_count = len(re.findall(r'\bif\b', code, re.IGNORECASE))
        elif_count = len(re.findall(r'\belif\b', code, re.IGNORECASE))
        for_count = len(re.findall(r'\bfor\b', code, re.IGNORECASE))
        while_count = len(re.findall(r'\bwhile\b', code, re.IGNORECASE))
        except_count = len(re.findall(r'\bexcept\b', code, re.IGNORECASE))
        
        # SQL control structures
        case_when = len(re.findall(r'\bCASE\s+WHEN\b', code, re.IGNORECASE))
        where_and_or = len(re.findall(r'\bWHERE\s+.*\b(?:AND|OR)\b', code, re.IGNORECASE))
        having_and_or = len(re.findall(r'\bHAVING\s+.*\b(?:AND|OR)\b', code, re.IGNORECASE))
        
        # Spark-specific conditional operations
        when_otherwise = len(re.findall(r'\.when\s*\(|\.otherwise\s*\(', code, re.IGNORECASE))
        filter_conditions = len(re.findall(r'\.filter\s*\(|\.where\s*\(', code, re.IGNORECASE))
        
        decision_points = (if_count + elif_count + for_count + while_count + except_count +
                          case_when + where_and_or + having_and_or + when_otherwise + filter_conditions)

        return max(1, decision_points + 1)
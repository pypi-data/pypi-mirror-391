# src/code_analyzer/analyzers/pyspark_analyzer.py
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


class PySparkAnalyzer(AnalyzerBase):
    """
    Sybase code complexity analyzer with enterprise metrics integration.
    
    Evaluates PySpark scripts across 10 dimensions, each scored 1-4:
    - 1: Simple
    - 2: Medium
    - 3: Complex
    - 4: Very Complex
    
    Uses hybrid approach:
    - Config weights override registry defaults
    - Enterprise validation via metrics module
    - Standardized 0-100 scoring system
    """
    language = "pyspark"
    
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
        """Analyze PySpark source code and return complexity metrics."""
        include_cyclomatic = self.config.get("include_cyclomatic", False)
        
        # If code is None or empty, try to read from file path
        if not code and path and path != "<string>":
            file_content = read_file_if_exists(path)
            if file_content:
                code = file_content
        
        # Run complexity analysis
        analyzer = PySparkComplexity()
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
    

class PySparkComplexity:
    """
    Enterprise-grade PySpark complexity analyzer with comprehensive pattern detection.
    Each metric is scored 1 (Simple) to 4 (Very Complex) based on PySpark-specific patterns.
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
    
        # Remove comments and strings for accurate analysis
        code_no_comments = self._remove_comments(code)
        
        # Calculate nesting depth
        nesting_level = self._get_nesting_level(code_no_comments)
        
        # --- 1. SCRIPT SIZE & STRUCTURE ---
        lines = len([line for line in code.split('\n') if line.strip()])
        
        # Python structure
        classes = len(re.findall(r'^class\s+\w+', code_no_comments, re.MULTILINE))
        functions = len(re.findall(r'^\s*def\s+\w+', code_no_comments, re.MULTILINE))
        
        # PySpark-specific structures
        spark_context = len(re.findall(r'SparkContext|SparkConf|SparkSession', code_no_comments))
        notebooks = len(re.findall(r'get_ipython|display\(|dbutils', code_no_comments))
        
        # TIER 2: MLlib pipelines and models
        ml_pipelines = len(re.findall(r'Pipeline\(|Estimator|Transformer', code_no_comments))
        
        # TIER 3: Enterprise frameworks
        koalas_pandas = len(re.findall(r'pyspark\.pandas|ps\.|to_pandas|from_pandas', code_no_comments))
        delta_lake = len(re.findall(r'DeltaTable|delta\.|\.format\("delta"\)', code_no_comments))
        
        score = 1  # Simple: small script
        if lines > 100 or functions > 3 or spark_context > 0:
            score = 2  # Medium: moderate size, basic PySpark
        if lines > 500 or classes > 0 or functions > 10 or nesting_level > 3 or ml_pipelines > 0:
            score = 3  # Complex: large script, OOP, ML pipelines
        if lines > 2000 or classes > 3 or functions > 20 or nesting_level > 5 or koalas_pandas > 0 or delta_lake > 0:
            score = 4  # Very Complex: very large, complex OOP, enterprise features
        
        self.script_size_structure = score

        # --- 2. DEPENDENCY FOOTPRINT ---
        imports = len(re.findall(r'^import\s+|^from\s+\w+\s+import', code_no_comments, re.MULTILINE))
        
        # PySpark-specific imports
        pyspark_imports = len(re.findall(r'from pyspark|import pyspark', code_no_comments))
        spark_sql_imports = len(re.findall(r'from pyspark\.sql|pyspark\.sql\.functions', code_no_comments))
        mllib_imports = len(re.findall(r'from pyspark\.ml|from pyspark\.mllib', code_no_comments))
        
        # External data connections
        jdbc_connections = len(re.findall(r'\.jdbc\(|\.format\("jdbc"\)', code_no_comments))
        cloud_storage = len(re.findall(r's3a://|s3n://|gs://|abfss://|wasbs://', code_no_comments))
        kafka_streams = len(re.findall(r'\.format\("kafka"\)|readStream.*kafka', code_no_comments))
        
        # TIER 2: Broadcast variables and accumulators
        broadcasts = len(re.findall(r'\.broadcast\(|sc\.broadcast', code_no_comments))
        accumulators = len(re.findall(r'\.accumulator\(|sc\.accumulator', code_no_comments))
        
        # TIER 3: External systems
        external_systems = len(re.findall(r'\.format\("mongodb"\)|\.format\("cassandra"\)|\.format\("elasticsearch"\)', code_no_comments))
        
        score = 1  # Simple: minimal imports
        if imports > 5 or pyspark_imports > 0:
            score = 2  # Medium: basic imports, PySpark usage
        if imports > 15 or spark_sql_imports > 0 or jdbc_connections > 0 or cloud_storage > 0 or broadcasts > 0:
            score = 3  # Complex: many imports, external data, broadcasts
        if imports > 30 or mllib_imports > 0 or kafka_streams > 0 or external_systems > 0 or (broadcasts > 0 and accumulators > 0):
            score = 4  # Very Complex: heavy dependencies, streaming, external systems
        
        self.dependency_footprint = score

        # --- 3. ANALYTICS DEPTH ---
        # DataFrames and RDDs
        dataframes = len(re.findall(r'\.createDataFrame|\.read\.|\.sql\(|DataFrame', code_no_comments))
        rdds = len(re.findall(r'\.parallelize|\.textFile|\.rdd|RDD', code_no_comments))
        
        # Aggregations and analytics
        aggregations = len(re.findall(r'\.groupBy|\.agg\(|\.count\(|\.sum\(|\.avg\(|\.max\(|\.min\(', code_no_comments))
        window_functions = len(re.findall(r'Window\.|\.over\(|row_number|rank|dense_rank', code_no_comments))
        
        # Advanced analytics
        pivot_operations = len(re.findall(r'\.pivot\(|\.unpivot\(', code_no_comments))
        statistical_funcs = len(re.findall(r'\.describe\(|\.corr\(|\.cov\(|\.stat\.|\.summary\(', code_no_comments))
        
        # TIER 2: MLlib analytics
        ml_algorithms = len(re.findall(r'LogisticRegression|RandomForest|LinearRegression|KMeans|ALS', code_no_comments))
        feature_engineering = len(re.findall(r'VectorAssembler|StandardScaler|StringIndexer|OneHotEncoder', code_no_comments))
        
        # TIER 3: Advanced ML
        ml_pipelines_advanced = len(re.findall(r'CrossValidator|ParamGridBuilder|TrainValidationSplit', code_no_comments))
        graph_analytics = len(re.findall(r'GraphFrame|GraphX|pageRank|connectedComponents', code_no_comments))
        
        score = 1  # Simple: basic operations
        if dataframes > 0 or rdds > 0 or aggregations > 0:
            score = 2  # Medium: DataFrames/RDDs, basic aggregations
        if window_functions > 0 or pivot_operations > 0 or statistical_funcs > 0 or ml_algorithms > 0:
            score = 3  # Complex: window functions, ML algorithms
        if ml_pipelines_advanced > 0 or graph_analytics > 0 or (ml_algorithms > 2 and feature_engineering > 2):
            score = 4  # Very Complex: advanced ML pipelines, graph analytics
        
        self.analytics_depth = score

        # --- 4. SQL & REPORTING LOGIC ---
        # Spark SQL usage
        spark_sql = len(re.findall(r'\.sql\(|spark\.sql', code_no_comments))
        sql_queries = len(re.findall(r'SELECT|FROM|WHERE|JOIN', code_no_comments, re.IGNORECASE))
        
        # DataFrame operations that mimic SQL
        joins = len(re.findall(r'\.join\(|\.crossJoin\(', code_no_comments))
        filters = len(re.findall(r'\.filter\(|\.where\(', code_no_comments))
        selects = len(re.findall(r'\.select\(|\.selectExpr\(', code_no_comments))
        
        # Complex SQL patterns
        subqueries = len(re.findall(r'\(\s*SELECT', code_no_comments, re.IGNORECASE))
        ctes = len(re.findall(r'WITH\s+\w+\s+AS', code_no_comments, re.IGNORECASE))
        unions = len(re.findall(r'\.union\(|\.unionAll\(|UNION', code_no_comments, re.IGNORECASE))
        
        # TIER 3: Advanced SQL features
        temp_views = len(re.findall(r'\.createOrReplaceTempView|\.createTempView', code_no_comments))
        catalog_operations = len(re.findall(r'spark\.catalog\.|\.listTables\(|\.listColumns\(', code_no_comments))
        
        score = 1  # Simple: minimal SQL
        if spark_sql > 0 or selects > 2 or filters > 2:
            score = 2  # Medium: basic SQL operations
        if joins > 0 or sql_queries > 5 or subqueries > 0 or temp_views > 0:
            score = 3  # Complex: joins, complex queries, temp views
        if ctes > 0 or unions > 2 or catalog_operations > 0 or (joins > 3 and subqueries > 2):
            score = 4  # Very Complex: CTEs, catalog operations, complex joins
        
        self.sql_reporting_logic = score

        # --- 5. TRANSFORMATION LOGIC ---
        # Basic transformations
        transformations = len(re.findall(r'\.map\(|\.flatMap\(|\.filter\(|\.distinct\(', code_no_comments))
        column_operations = len(re.findall(r'\.withColumn\(|\.drop\(|\.rename\(', code_no_comments))
        
        # Data type conversions
        casting = len(re.findall(r'\.cast\(|\.astype\(', code_no_comments))
        string_operations = len(re.findall(r'upper\(|lower\(|trim\(|substring\(|regexp_replace', code_no_comments))
        
        # Advanced transformations
        udf_usage = len(re.findall(r'@udf|udf\(|UserDefinedFunction', code_no_comments))
        lambda_functions = len(re.findall(r'lambda\s+\w+:', code_no_comments))
        
        # TIER 2: ETL operations
        data_cleaning = len(re.findall(r'\.na\.|\.fillna\(|\.dropna\(|\.isNull\(|\.isNotNull\(', code_no_comments))
        data_validation = len(re.findall(r'\.exceptAll\(|\.intersect\(|\.subtract\(', code_no_comments))
        
        # TIER 3: Advanced ETL
        custom_partitioning = len(re.findall(r'\.repartition\(|\.coalesce\(|\.partitionBy\(', code_no_comments))
        streaming_transforms = len(re.findall(r'\.writeStream\.|\.readStream\.|foreachBatch', code_no_comments))
        
        score = 1  # Simple: minimal transformations
        if transformations > 2 or column_operations > 2:
            score = 2  # Medium: basic transformations
        if udf_usage > 0 or lambda_functions > 3 or data_cleaning > 2 or casting > 3:
            score = 3  # Complex: UDFs, data cleaning, type conversions
        if streaming_transforms > 0 or custom_partitioning > 0 or (udf_usage > 2 and lambda_functions > 5):
            score = 4  # Very Complex: streaming, custom partitioning, heavy UDF usage
        
        self.transformation_logic = score

        # --- 6. UTILITY COMPLEXITY ---
        # Custom functions and UDFs
        function_defs = len(re.findall(r'def\s+\w+\s*\(', code_no_comments))
        udfs = len(re.findall(r'@udf|F\.udf|udf\(', code_no_comments))
        pandas_udfs = len(re.findall(r'@pandas_udf|pandas_udf\(', code_no_comments))
        
        # Lambda expressions and functional programming
        lambdas = len(re.findall(r'lambda\s+', code_no_comments))
        map_operations = len(re.findall(r'\.map\(|\.flatMap\(|\.mapPartitions\(', code_no_comments))
        
        # Configuration and session management
        spark_config = len(re.findall(r'\.config\(|SparkConf\(|setAppName|setMaster', code_no_comments))
        session_management = len(re.findall(r'\.getOrCreate\(|\.stop\(|\.sparkContext', code_no_comments))
        
        # TIER 3: Advanced utilities
        custom_serializers = len(re.findall(r'pickle\.|cloudpickle|kryo', code_no_comments))
        monitoring = len(re.findall(r'\.ui\.|SparkListener|JobProgressListener', code_no_comments))
        
        score = 1  # Simple: basic functions
        if function_defs > 3 or lambdas > 2 or spark_config > 0:
            score = 2  # Medium: custom functions, basic config
        if udfs > 0 or pandas_udfs > 0 or map_operations > 3 or session_management > 2:
            score = 3  # Complex: UDFs, advanced operations
        if custom_serializers > 0 or monitoring > 0 or (udfs > 2 and pandas_udfs > 0):
            score = 4  # Very Complex: custom serializers, monitoring, advanced UDFs
        
        self.utility_complexity = score

        # --- 7. EXECUTION CONTROL ---
        # Job and execution control
        actions = len(re.findall(r'\.collect\(|\.take\(|\.count\(|\.show\(|\.foreach\(', code_no_comments))
        caching = len(re.findall(r'\.cache\(|\.persist\(|StorageLevel', code_no_comments))
        checkpointing = len(re.findall(r'\.checkpoint\(|setCheckpointDir', code_no_comments))
        
        # Resource management
        partitioning = len(re.findall(r'\.repartition\(|\.coalesce\(|getNumPartitions', code_no_comments))
        resource_config = len(re.findall(r'spark\.executor\.|spark\.driver\.|spark\.sql\.adaptive', code_no_comments))
        
        # TIER 2: Advanced execution control
        dynamic_allocation = len(re.findall(r'dynamicAllocation|spark\.shuffle\.|spark\.serializer', code_no_comments))
        job_groups = len(re.findall(r'setJobGroup|setJobDescription|cancelJobGroup', code_no_comments))
        
        # TIER 3: Enterprise execution features
        fair_scheduler = len(re.findall(r'spark\.scheduler\.mode|FAIR|spark\.scheduler\.pool', code_no_comments))
        external_shuffle = len(re.findall(r'spark\.shuffle\.service|spark\.dynamicAllocation\.externalShuffleService', code_no_comments))
        
        score = 1  # Simple: basic actions
        if actions > 3 or caching > 0 or partitioning > 0:
            score = 2  # Medium: caching, partitioning
        if checkpointing > 0 or resource_config > 0 or dynamic_allocation > 0:
            score = 3  # Complex: checkpointing, resource management
        if fair_scheduler > 0 or external_shuffle > 0 or job_groups > 0:
            score = 4  # Very Complex: advanced scheduling, job management
        
        self.execution_control = score

        # --- 8. FILE I/O & EXTERNAL INTEGRATION ---
        # File I/O operations
        file_reads = len(re.findall(r'\.read\.|\.load\(|\.text\(|\.textFile\(', code_no_comments))
        file_writes = len(re.findall(r'\.write\.|\.save\(|\.saveAsTextFile\(', code_no_comments))
        
        # File formats
        formats = len(re.findall(r'\.parquet\(|\.json\(|\.csv\(|\.orc\(|\.avro\(', code_no_comments))
        
        # External data sources
        databases = len(re.findall(r'\.format\("jdbc"\)|\.jdbc\(', code_no_comments))
        cloud_storage_ops = len(re.findall(r's3a://|s3n://|gs://|abfss://|wasbs://|hdfs://', code_no_comments))
        streaming_sources = len(re.findall(r'\.format\("kafka"\)|\.format\("socket"\)', code_no_comments))
        
        # TIER 2: Advanced I/O
        custom_datasources = len(re.findall(r'\.format\("delta"\)|\.format\("mongodb"\)|\.format\("cassandra"\)', code_no_comments))
        external_catalogs = len(re.findall(r'HiveMetastore|GlueMetastore|spark\.sql\.catalogImplementation', code_no_comments))
        
        # TIER 3: Enterprise integrations
        data_lake_integration = len(re.findall(r'DeltaTable|IcebergTable|HudiTable', code_no_comments))
        rest_apis = len(re.findall(r'requests\.|urllib|httpx|aiohttp', code_no_comments))
        
        score = 1  # Simple: minimal I/O
        if file_reads > 0 or file_writes > 0 or formats > 0:
            score = 2  # Medium: basic file I/O
        if databases > 0 or cloud_storage_ops > 0 or streaming_sources > 0 or custom_datasources > 0:
            score = 3  # Complex: databases, cloud storage, streaming
        if data_lake_integration > 0 or external_catalogs > 0 or rest_apis > 0:
            score = 4  # Very Complex: data lake integration, external catalogs
        
        self.file_io_external_integration = score

        # --- 9. ODS OUTPUT DELIVERY ---
        # Output operations
        writes = len(re.findall(r'\.write\.|\.save\(', code_no_comments))
        shows = len(re.findall(r'\.show\(|\.display\(', code_no_comments))
        collects = len(re.findall(r'\.collect\(|\.toPandas\(', code_no_comments))
        
        # Output formats and modes
        output_formats = len(re.findall(r'\.parquet\(|\.json\(|\.csv\(|\.orc\(|\.avro\(', code_no_comments))
        write_modes = len(re.findall(r'\.mode\("overwrite"\)|\.mode\("append"\)|\.mode\("ignore"\)', code_no_comments))
        
        # Partitioned outputs
        partitioned_writes = len(re.findall(r'\.partitionBy\(|\.bucketBy\(', code_no_comments))
        
        # TIER 2: Advanced outputs
        streaming_outputs = len(re.findall(r'\.writeStream\.|\.outputMode\(|\.trigger\(', code_no_comments))
        multiple_outputs = len(re.findall(r'foreach\(|foreachBatch\(', code_no_comments))
        
        # TIER 3: Enterprise outputs
        data_quality = len(re.findall(r'\.option\("checkpointLocation"\)|\.option\("path"\)', code_no_comments))
        monitoring_outputs = len(re.findall(r'StreamingQueryListener|StreamingQuery\.|queryName', code_no_comments))
        
        score = 1  # Simple: minimal output
        if writes > 0 or shows > 2 or collects > 0:
            score = 2  # Medium: basic outputs
        if output_formats > 1 or write_modes > 0 or partitioned_writes > 0 or streaming_outputs > 0:
            score = 3  # Complex: multiple formats, partitioned writes, streaming
        if data_quality > 0 or monitoring_outputs > 0 or (streaming_outputs > 0 and multiple_outputs > 0):
            score = 4  # Very Complex: data quality checks, monitoring, complex streaming
        
        self.ods_output_delivery = score

        # --- 10. ERROR HANDLING & OPTIMIZATION ---
        # Error handling
        try_except = len(re.findall(r'try:|except\s+\w+:|except:', code_no_comments))
        spark_exceptions = len(re.findall(r'AnalysisException|Py4JJavaError|SparkException', code_no_comments))
        
        # Performance optimization
        broadcast_vars = len(re.findall(r'broadcast\(|F\.broadcast', code_no_comments))
        cache_persist = len(re.findall(r'\.cache\(|\.persist\(|\.unpersist\(', code_no_comments))
        
        # SQL optimization
        sql_hints = len(re.findall(r'/\*\+.*\*/|\.hint\(', code_no_comments))
        adaptive_query = len(re.findall(r'spark\.sql\.adaptive|AQE|adaptiveQueryExecution', code_no_comments))
        
        # TIER 2: Advanced optimization
        custom_partitioners = len(re.findall(r'Partitioner|HashPartitioner|RangePartitioner', code_no_comments))
        memory_management = len(re.findall(r'spark\.executor\.memory|spark\.driver\.memory|spark\.sql\.execution\.arrow', code_no_comments))
        
        # TIER 3: Enterprise optimization
        cost_based_optimizer = len(re.findall(r'spark\.sql\.cbo|spark\.sql\.statistics|ANALYZE TABLE', code_no_comments))
        vectorization = len(re.findall(r'vectorized|wholeStageCodegen|spark\.sql\.codegen', code_no_comments))
        
        score = 1  # Simple: minimal error handling
        if try_except > 0 or broadcast_vars > 0 or cache_persist > 0:
            score = 2  # Medium: basic error handling, caching
        if spark_exceptions > 0 or sql_hints > 0 or adaptive_query > 0 or custom_partitioners > 0:
            score = 3  # Complex: Spark-specific handling, SQL optimization
        if cost_based_optimizer > 0 or vectorization > 0 or (memory_management > 0 and adaptive_query > 0):
            score = 4  # Very Complex: CBO, vectorization, advanced memory management
        
        self.error_handling_optimization = score
        
        # Calculate cyclomatic complexity
        self.cyclomatic = self._calculate_cyclomatic_complexity(code_no_comments)

    def _remove_comments(self, code: str) -> str:
        """Remove Python comments and docstrings from code."""
        # Remove single-line comments
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        
        # Remove multi-line strings (docstrings)
        code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
        
        return code

    def _get_nesting_level(self, code: str) -> int:
        """Calculate maximum nesting depth of control structures."""
        lines = code.split('\n')
        max_depth = 0
        current_depth = 0
        
        for line in lines:
            stripped = line.lstrip()
            if not stripped:
                continue
                
            # Calculate indentation level
            indent = len(line) - len(stripped)
            
            # Check for control structures
            if re.match(r'(if|elif|else|for|while|with|try|except|finally|def|class):', stripped):
                current_depth = indent // 4 + 1
                max_depth = max(max_depth, current_depth)
        
        return max_depth

    def _calculate_cyclomatic_complexity(self, code: str) -> int:
        """Calculate cyclomatic complexity for PySpark code."""
        # Decision points
        if_count = len(re.findall(r'\bif\b', code))
        elif_count = len(re.findall(r'\belif\b', code))
        for_count = len(re.findall(r'\bfor\b', code))
        while_count = len(re.findall(r'\bwhile\b', code))
        except_count = len(re.findall(r'\bexcept\b', code))
        
        # Logical operators
        and_count = len(re.findall(r'\band\b', code))
        or_count = len(re.findall(r'\bor\b', code))
        
        # PySpark-specific decision points
        filter_count = len(re.findall(r'\.filter\(|\.where\(', code))
        case_when_count = len(re.findall(r'when\(.*,.*\)', code))
        
        decision_points = (if_count + elif_count + for_count + while_count + 
                          except_count + and_count + or_count + 
                          filter_count + case_when_count)
        
        return max(1, decision_points + 1)
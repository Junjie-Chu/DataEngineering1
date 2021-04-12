# Scalability 可扩展性
## 理论
### horizontal
加入更多节点
### vertical
提高某个节点的硬件配置
### strong
给定fixed size的工作负载,增加工作资源,比较所花费的时间.

Amdahl定律:  
1个处理器串行计算时间/n个处理器并行计算时间  
f表示串行部分时间所占比例，p表示并行的处理器个数  
加速比S(p)=1/(f+(1-f)/p)  
当p充分大时，S(p)趋向于1/f，所以，并行处理器的数量在达到充分大时，已经不能有效改善总体的处理性能。  

### weak
工作负载增加,工作资源也增加,比较所花费的时间.也可以理解为相同时间下,所完成的工作的总量.    
- 1G -> 1 worker
- 2G -> 2 workers
- NG -> N workers
- ...  

Gustafson定律:  
p个处理器并行计算量/1个处理器的串行计算量  
Ws表示串行部分负载量，Wp表示并行部分负载量，W=Ws+Wp，f表示串行负载量所占比例  
加速比S(p)=(Ws+p*Wp)/(Ws+Wp)  
=(f*W+p*(1-f)*W)/(f*W+(1-f)*W)  
=(f+p(1-f))/1=f+p(1-f)  
P越大，计算量增加越大，计算精度越高
  
## code of examples
### weak scalability
```python
from pyspark.sql import SparkSession
# 8 cores
spark_session = SparkSession\
        .builder\
        .master("spark://192.168.2.181:7077") \
        .appName("weak_scaling_8_core")\
        .config("spark.dynamicAllocation.enabled", True)\
        .config("spark.shuffle.service.enabled", True)\
        .config("spark.cores.max", 8)\
        .getOrCreate()

spark_context = spark_session.sparkContext
# 加载8份数据
df = spark_session.read\
    .option("header", "true")\
    .csv(['hdfs://192.168.2.181:9000/user/ubuntu/songs_collection/*', 'hdfs://192.168.2.181:9000/user/ubuntu/songs_collection1/*', 'hdfs://192.168.2.181:9000/user/ubuntu/songs_collection2/*'
          , 'hdfs://192.168.2.181:9000/user/ubuntu/songs_collection3/*', 'hdfs://192.168.2.181:9000/user/ubuntu/songs_collection4/*', 'hdfs://192.168.2.181:9000/user/ubuntu/songs_collection5/*'
          , 'hdfs://192.168.2.181:9000/user/ubuntu/songs_collection6/*', 'hdfs://192.168.2.181:9000/user/ubuntu/songs_collection7/*'])
          
# 创建名为duration的新列,转换数据类型为float  
df = df.withColumn('Duration', df['Duration'].cast("float"))
df = df.filter(df['Duration'] >= 240)
print("Amount of songs longer than 240 sec: "+str(df.count()))

# Release cores and stop application.
spark_context.stop()
```
### strong scalability
```
from pyspark.sql import SparkSession
# 3 cores
spark_session = SparkSession\
        .builder\
        .master("spark://192.168.2.181:7077") \
        .appName("strong_scaling_3_core")\
        .config("spark.dynamicAllocation.enabled", True)\
        .config("spark.shuffle.service.enabled", True)\
        .config("spark.cores.max", 3)\
        .getOrCreate()

spark_context = spark_session.sparkContext
# 固定size的数据
df = spark_session.read\
    .option("header", "true")\
    .csv('hdfs://192.168.2.181:9000/user/ubuntu/*')

df = df.withColumn('Duration', df['Duration'].cast("float"))
df = df.filter(df['Duration'] >= 240)
print("Amount of songs longer than 240 sec: "+str(df.count()))

# Release cores and stop application.
spark_context.stop()
```

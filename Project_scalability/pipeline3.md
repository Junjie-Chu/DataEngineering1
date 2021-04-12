# HDFS的备份和恢复
## 一、配置：
secondary namenoded的配置,它的配置共两步：  
1. 集群配置文件conf/master中添加secondarynamenode的机器
2. 修改/添加 hdfs-site.xml中如下属性：
```
	<property>
		<name>dfs.http.address</name>
		<value>192.168.1.11:50070</value>
		<description>
		The address and the base port where the dfs namenode web ui will listen on.
		If the port is 0 then the server will start on a free port.
		</description>
	</property>
 
	<property>
		<name>dfs.secondary.http.address</name>
		<value>192.168.1.12:50090</value>
		<description>
		The secondary namenode http server address and port.
		If the port is 0 then the server will start on a free port.
		</description>
	</property>
```
这两项配置OK后，启动集群。其他配置参考官方文档.    
进入secondary namenode 机器，检查fs.checkpoint.dir（core-site.xml文件，默认为${hadoop.tmp.dir}/dfs/namesecondary）目录同步状态是否和namenode一致的。  
如果不配置第二项则,secondary namenode同步文件夹永远为空.  

## 二、配置检查:
配置完成之后，我们需要检查一下是否成功。我们可以通过查看运行secondarynamenode的机器上文件目录来确定是否成功配置。    
首先输入jps查看是否存在secondarynamenode进程。如果存在，在查看对应的目录下是否有备份记录。    
该目录一般存在于hadoop.tmp.dir/dfs/namesecondary/下面。  

## 三、恢复：
1. 配置完成了，如何恢复。首先我们kill掉namenode进程，然后将hadoop.tmp.dir目录下的数据删除掉。制造master挂掉情况。
2. 在配置参数dfs.name.dir指定的位置建立一个空文件夹； 
把检查点目录的位置赋值给配置参数fs.checkpoint.dir； 
3. 启动namenode的时候采用hadoop namenode –importCheckpoint（见官方文档）;
4. 如果namenode的IP配置有修改，手动重启各datanode节点.

## 四、总结：
1. secondarynamenode可以配置多个，master文件里面多写几个。
2. 如果要恢复数据是需要手动拷贝到namenode机器上的。不是自动的（参看上面写的恢复操作）。
3. Secondary NameNode会定期合并fsimage和edits日志，将edits日志文件大小控制在一个限度下.  
合并的时机是由2个配置参数决定的：  
fs.checkpoint.period，指定连续两次检查点的最大时间间隔， 默认值是1小时。    
fs.checkpoint.size定义了edits日志文件的最大值，一旦超过这个值会导致强制执行检查点（即使没到检查点的最大时间间隔）。默认值是64MB。镜像备份的周期时间是可以修改的。core-site.xml中的fs.checkpoint.period值。  
如果宕机发生,宕机到上次备份点之间的数据会丢失.  
4. secondarynamenode的数据恢复必然会丢失数据,有其他两种方法:
- 在hdfs-site.xml中，配置多个name的dir到不同的磁盘分区上：
```
<property>
    <name>dfs.name.dir</name>
    <value>/pvdata/hadoopdata/name/,/opt/hadoopdata/name/</value>
</property>
```
- Jounral nodes
1. 在一个典型的HA集群中，每个NameNode是一台独立的服务器。在任一时刻，只有一个NameNode处于active状态，另一个处于standby状态。其中，active状态的NameNode负责所有的客户端操作，standby状态的NameNode处于从属地位，维护着数据状态，随时准备切换。 
2. 两个NameNode为了数据同步，会通过一组称作JournalNodes的独立进程进行相互通信。当active状态的NameNode的命名空间有任何修改时，会告知大部分的JournalNodes进程。standby状态的NameNode有能力读取JNs中的变更信息，并且一直监控edit log的变化，把变化应用于自己的命名空间。standby可以确保在集群出错时，命名空间状态已经完全同步了
3. 为了确保快速切换，standby状态的NameNode有必要知道集群中所有数据块的位置。为了做到这点，所有的datanodes必须配置两个NameNode的地址，发送数据块位置信息和心跳给他们两个。 
4. 对于HA集群而言，确保同一时刻只有一个NameNode处于active状态是至关重要的。否则，两个NameNode的数据状态就会产生分歧，可能丢失数据，或者产生错误的结果。为了保证这点，JNs必须确保同一时刻只有一个NameNode可以向自己写数据。 
![image](https://user-images.githubusercontent.com/65893273/114420212-b5370f80-9be6-11eb-8c2a-903b2c3b5544.png)    
宕机内存元数据一致性回放SNN机制（高可用）
- 第一步：通知hdfs客户端，我要上传一份文件。（提前设置副本）
- 第二步：更新Active NameNode(ANN)的内存元数据，并写一份edits log到JournalNodes集群上，另一份写在本地。
- 第三步：Standby NameNode （SNN）实时读取JournalNodes中更新的 edits log，更新Standby NameNode内存元数据，并每隔一段时间（SNN上有一个线程StandbyCheckpointer），元数据写入到磁盘的fsimage文件中，并同步到Active NameNode。
- 第四步：一旦Active NameNode宕机，Standby NameNode 直接读取最近更新的edits log（不会太多）和 fsimage文件，进行内存中回放，即可实现快速恢复使用。
- 第五步：如果没有宕机，hdfs客户端负责分布式写副本即可。

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

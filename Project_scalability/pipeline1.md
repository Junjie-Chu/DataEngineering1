# 项目流程 1

## 工具准备
版本控制git,任务分配git project  
云计算:Spark+HDFS  
交互式编程:jupyter notebook
3台VM(后期扩展到5台) on OpenStack    

## Launch VM  
### VM setup
Currently, 3 VM's setup with 20gb volume, 2 VCPUS with 2 GB ram.  

### Fixed IPs for VM:
* Node 0: 192.168.2.216
* Node 1: 192.168.2.58
* Node 2: 192.168.2.10

### Floating IPs for VM:
* Node 0: 130.238.29.209
* Node 1: 130.238.29.139
* Node 2: 130.238.29.7

## 安装HDFS
**Step 1:** 更新已经安装的包. As always when launching a new linux instance, we need to run the commands below to update all installed packages on the machine. Do this on all instances.
- ```sudo apt-get update```
- ```sudo apt-get upgrade ```

**Step 2:** From the master node (node 0), run the below commands. The following commands setup so that the master node have passwordless login (ssh) to the worker nodes.
- ```ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa``` - Generates new key. "ssh-keygen -t rsa P “” -f ~/.ssh/id_rsa"不提示直接生成密钥,不需要按回车了.'.pub'是公钥,另一个是私钥.
- ```cat .ssh/id_rsa.pub >> ~/.ssh/authorized_keys``` - Append the new key to the authorized keys. "cat"连接文件打印到标准输出. 这里是将公钥添加到authoried_keys文件的末尾.
- ```scp -i team_19.pem .ssh/authorized_keys ubuntu@192.168.2.58:/home/ubuntu/.ssh/authorized_keys``` - Copy the new key to node1, 正常操作流程是将.pub复制到node1上,再在node1上执行cat.
- ```scp -i team_19.pem .ssh/authorized_keys ubuntu@192.168.2.10:/home/ubuntu/.ssh/authorized_keys``` - Copy the new key to node2, 重复node1的过程.

**Step 3:** Add all nodes to /etc/hosts on the master node.
- ```sudo nano /etc/hosts``` 'nano'是文本编辑器,也可以用vim或者vi. Edit and add the text below:
```
192.168.2.216 master
192.168.2.58 worker-node1
192.168.2.10 worker-node2
```

**Step 4:** Install JDK1.8 on all nodes. 在所有节点上安装Hadoop依赖的Java
- ```sudo apt-get -y install openjdk-8-jdk-headless``` - Installs JDK1.8
- ```java -version``` - Checks if the install was successful. 

**Step 5:** Install Hadoop on all nodes. 在所有节点上安装Hadoop
- ```sudo wget -P ~ https://mirrors.sonic.net/apache/hadoop/common/hadoop-3.2.1/hadoop-3.2.1.tar.gz```
- ```tar -xzf hadoop-3.2.1.tar.gz```
- ```mv hadoop-3.2.1 hadoop```
- ```sudo rm hadoop-3.2.1.tar.gz```

**Step 6:** Hadoop configuration on all nodes. 在所有节点上配置.
- ```nano ~/.bashrc``` - Edits file, add the text below.编辑环境变量.
```
export HADOOP_HOME=/home/ubuntu/hadoop
export PATH=$PATH:$HADOOP_HOME/bin
export PATH=$PATH:$HADOOP_HOME/sbin
export HADOOP_MAPRED_HOME=${HADOOP_HOME}
export HADOOP_COMMON_HOME=${HADOOP_HOME}
export HADOOP_HDFS_HOME=${HADOOP_HOME}
export YARN_HOME=${HADOOP_HOME}
```
- ```source ~/.bashrc``` - Reloads the env variables.重载环境变量.

**Step 7:** Hadoop cluster configuration, do this on the master node then copy to the worker nodes.在主节点上配置,然后复制到其他节点.
- ```nano ~/hadoop/etc/hadoop/hadoop-env.sh``` - Add/Edit the below text.

```export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64```

- ```nano ~/hadoop/etc/hadoop/core-site.xml``` - Edit file, add text below.
```xml
<configuration>
	<property>
		<name>fs.defaultFS</name>
		<value>hdfs://192.168.2.216:9000</value>
	</property>
</configuration>
```
- ```nano ~/hadoop/etc/hadoop/hdfs-site.xml``` - Edit file, add text below.
```xml
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>3</value>
    </property>
    <property>
        <name>dfs.namenode.name.dir</name>
        <value>file:///usr/local/hadoop/hdfs/data</value>
    </property>
    <property>
        <name>dfs.datanode.data.dir</name>
        <value>file:///usr/local/hadoop/hdfs/data</value>
    </property>
</configuration>
```
- ```nano ~/hadoop/etc/hadoop/yarn-site.xml``` - Edit file, add text below.
```xml
<configuration>
    <property>
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
    </property>
    <property>
        <name>yarn.nodemanager.aux-services.mapreduce.shuffle.class</name>
        <value>org.apache.hadoop.mapred.ShuffleHandler</value>
    </property>
    <property>
       <name>yarn.resourcemanager.hostname</name>
       <value>192.168.2.216</value>
    </property>
</configuration>
```
Copy the 3 files to the nodes.
- ```scp ~/hadoop/etc/hadoop/hdfs-site.xml ubuntu@LAN_IP_FOR_NODE:~/hadoop/etc/hadoop/hdfs-site.xml ```
- ```scp ~/hadoop/etc/hadoop/core-site.xml ubuntu@LAN_IP_FOR_NODE:~/hadoop/etc/hadoop/core-site.xml ```
- ```scp ~/hadoop/etc/hadoop/yarn-site.xml ubuntu@LAN_IP_FOR_NODE:~/hadoop/etc/hadoop/yarn-site.xml ```

ONLY ON MASTER, edit file, add text below.
- ```nano ~/hadoop/etc/hadoop/mapred-site.xml```
```xml
<configuration>
	<property>
		<name>mapreduce.jobtracker.address</name>
		<value>192.168.2.216:54311</value>
	</property>
	<property>
		<name>mapreduce.framework.name</name>
		<value>yarn</value>
	</property>
</configuration>
```

**Step 8:** Create data folder on ALL nodes.
- ```sudo mkdir -p /usr/local/hadoop/hdfs/data```
- ```sudo chown ubuntu:ubuntu -R /usr/local/hadoop/hdfs/data``` chown更改文件夹及所有子目录的所有者
- ```chmod 700 /usr/local/hadoop/hdfs/data``` 修改文件权限

**Step 9:** Create master and worker files on ALL nodes, I created them on the master node then using SCP to transfer to the worker nodes.
- ```nano ~/hadoop/etc/hadoop/masters``` - Edit and add the LAN IP of the master node.
- ```nano ~/hadoop/etc/hadoop/workers``` - Edit and add the LAN IP's of all worker nodes. HDFS集群里添加节点或者删除节点在这里操作.

**Step 10:** Format HDFS and Start Hadoop Cluster, run these commands on the master node.
- ```hdfs namenode -format``` - Formatting
- ```start-dfs.sh``` - Starting hdfs

Now run the following command on all nodes to verifiy that the hdfs start was successful.
- ```jps``` - The master node should be running NameNode and SecondaryNameNode. The workers should run DataNode.

Now the hdfs should be properly setup. To connect to the web gui edit your ~/.ssh/config file. Add the following:
```
	Host 130.238.29.209
  		User ubuntu
  		# modify this to match the name of your key
  		IdentityFile ~/.ssh/team_19.pem
  		# HDFS namenode web gui
  		LocalForward 9870 192.168.2.216:50070
```
Now you should be able to connect to the hdfs web gui by typing http://localhost:9870 in your browser, on your local machine. (This assumes the proper security group is added to the master.)

## 安装SPARK
**Step 1:** 安装
- 1.download: spark-3.1.1-bin-hadoop2.7.tgz from official website.
- 2.在master节点上创建文件夹，并将安装包解压到里面  
```
  mkdir /usr/local/spark
  tar xzf spark-3.1.1-bin-hadoop2.7.tgz
  mv spark-3.1.1-bin-hadoop2.7 /usr/local/spark/
```
- 3.scp将spark拷贝到其他slave节点,注意路径和master一致
- 4.在每个节点设置环境变量
```
export SPARK_HOME=/usr/lib/spark
export PATH=.:$HADOOP_HOME/bin:$JAVA_HOME/bin:$SPARK_HOME/bin:$PATH
```
此时,local模式安装完(本地单机)  
**Step 2:** 配置  
*在master节点配置Spark:*

- 复制   
进入 spark 解压目录，需要配置 conf/slaves，conf/spark-env.sh 两个文件. 注意这两个文件是不存在的，需要从模板 cp 复制一下.
```
cp slaves.template slaves
cp spark-env.sh.template spark-env.sh
```

- slaves   
末尾去掉 localhost，加上以下内容  
```
worker-node1
worker-node2
```

- spark-env.sh   
加上以下内容:  
```
export JAVA_HOME=/usr/lib/jvm/jre-1.8.0-openjdk.x86_64
export SPARK_MASTER_IP=master
export SPARK_MASTER_PORT=7077
export SPARK_WORKER_MEMORY=1G
```
SPARK_MASTER_IP/PORT 设置 spark 的主节点和端口；    
SPARK_WORKER_MEMORY 表示计算时使用的内存，在条件范围内越大越好，spark 是基于内存的计算.    
slaves,spark-env等配置根据需要修改.  
如果driver的内存不够用,会导致超出响应时间报错. 
一般来说,一个VM,其内存75%可以被Spark使用.  也就是说2g内存,最多1.5g可以使用.  
起初,设置master节点也是slave节点,同时还是driver节点.在运行时, 数据量稍大就会超出响应时间.排查下来问题在于内存较小.  
最简单的解决办法是不把master用作slave.  
最好的解决方法是更换master节点为高性能的VM.  
*向其他节点远程下发配置:*  
```
scp -r conf/ root@worker-node1:/usr/lib/spark
scp -r conf/ root@worker-node2:/usr/lib/spark
```

**Step 3:** 启动Spark
```
cd /usr/lib/spark/sbin
./start-all.sh
```
停止就是对应的 stop-all.sh  

# 项目流程 2

## 安装配置jupyter book

Spark applications will run in the cluster, but the 'driver' application will run on the master.  
Then visit the driver via the local computer.  

### Step 1: Configure some port forwarding
The web GUIs for Spark and HDFS are not open publicly, so we'll need to configure some port forwarding so that we can access them via the TCP ports.  


To do this, create or modify the file ~/.ssh/config on the local (laptop) computer by adding a section like the one shown below:  
Replace 130.238.x.y and ~/.ssh/id_rsa with master's floating IP and key path appropriately:  
```
Host 130.238.x.y
  User ubuntu
  # modify this to match the name of your key
  IdentityFile ~/.ssh/my_key.pem
  # Spark master web GUI
  LocalForward 8080 192.168.xx.yy:8080
  # HDFS namenode web gui
  LocalForward 9870 192.168.xx.yy:9870
  # python notebook
  LocalForward 8888 localhost:8888
  # spark applications
  LocalForward 4040 localhost:4040
  LocalForward 4041 localhost:4041
  LocalForward 4042 localhost:4042
  LocalForward 4043 localhost:4043
  LocalForward 4044 localhost:4044
  LocalForward 4045 localhost:4045
  LocalForward 4046 localhost:4046
  LocalForward 4047 localhost:4047
  LocalForward 4048 localhost:4048
  LocalForward 4049 localhost:4049
```
Notes:
- If get a warning about an "UNPROTECTED PRIVATE KEY FILE!" - to fix this, change the permissions on your key file to 600.
chmod 600 ~/.ssh/mykey.pem

With these settings, we can connect to the master host like this (without any additional parameters):  
```
ssh 130.238.x.y
```
此时,本地计算机连接到master不用密码,master连接到node不需要密码,但是两者使用的密钥不同.  
因为端口映射,所以此时在本地计算机访问localhost:8080相当于访问130.238.x.y:8080,而130.238.x.y在内网被映射到192.138.xx.yy,即相当于访问192.168.xx.yy:8080  
And when you access localhost:8080 in your browser, it will be forwarded to 192.168.xx.yy:8080 - the Web GUI of the Spark master.  

- Check the Spark and HDFS cluster is operating by opening these links in your browser
        http://localhost:8080
        http://localhost:9870

For HDFS, try Utilities > Browse to see the files on the cluster.  

### Step 2: Install the Python Notebook in driver Node (master node)

#### Env variable so the workers know which Python to use...
```
echo "export PYSPARK_PYTHON=python3" >> ~/.bashrc
source ~/.bashrc
```
#### install git
```
sudo apt-get install -y git
```
#### install python dependencies, start notebook

#### install the python package manager 'pip' -- it is recommended to do this directly 
```
sudo apt-get install -y python3-pip
```
#### check the version -- this is a very old version of pip:
```
python3 -m pip --version
```
#### install pyspark (the matching version as the cluster), and some other useful deps
```
python3 -m pip install pyspark==3.0.1 --user
python3 -m pip install pandas --user
python3 -m pip install matplotlib --user
```

#### clone the examples from the lectures to test, so we have a copy to experiment with
git clone https://github.com/benblamey/jupyters-public.git

#### install jupyterlab
```
python3 -m pip install jupyterlab
```
#### start the notebook!
```
python3 -m jupyterlab
```
Follow the instructions you see -- copy the 'localhost' link into your browser.  

#### Now finish!

- open the GUI in your web browser like this (e.g.):
http://localhost:4040


### Samples
- Start the application with dynamic allocation enabled, a timeout of no more than 30 seconds, and a cap on CPU cores:
```
spark_session = SparkSession\
        .builder\
        .master("spark://192.168.2.113:7077") \
        .appName("blameyben_lecture1_simple_example")\
        .config("spark.dynamicAllocation.enabled", True)\
        .config("spark.shuffle.service.enabled", True)\
        .config("spark.dynamicAllocation.executorIdleTimeout","30s")\
        .config("spark.executor.cores",2)\
        .config("spark.driver.port",9998)\
        .config("spark.blockManager.port",10005)\
        .getOrCreate()
```

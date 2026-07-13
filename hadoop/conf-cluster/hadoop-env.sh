# Hadoop 环境变量（三节点每台机器 $HADOOP_HOME/etc/hadoop/hadoop-env.sh 需一致）
# 安装脚本会写入 /etc/profile.d/hadoop.sh；此处供手工覆盖参考

export JAVA_HOME=${JAVA_HOME:-/usr/lib/jvm/java-8-openjdk-amd64}
export HADOOP_OS_TYPE=${HADOOP_OS_TYPE:-$(uname -s)}

# 企业实践：为 NameNode / DataNode 预留堆内存（按机器规格调整）
export HDFS_NAMENODE_OPTS="-Xms512m -Xmx1024m"
export HDFS_DATANODE_OPTS="-Xms512m -Xmx1024m"
export YARN_RESOURCEMANAGER_OPTS="-Xms512m -Xmx1024m"
export YARN_NODEMANAGER_OPTS="-Xms512m -Xmx1024m"

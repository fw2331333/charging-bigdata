# MySQL 远程配置与建库（Windows 宿主机）

> 适用环境：Windows 宿主机 MySQL + VirtualBox 虚拟机 Hadoop（NAT 网关 `10.0.2.2`）  
> 账号：`root` / `123456`  
> 安装路径：`E:\mysql-8.4.8-winx64`

---

## 一、整体目标

让虚拟机里的 Hadoop / Python ETL 能通过 `10.0.2.2:3306` 连接 Windows 上的 MySQL，并把 MapReduce 结果写入 `charging_bigdata` 库。

需要完成四件事：

1. **建库建表**（执行 `sql/schema.sql`）
2. **授权远程 root**（执行 `sql/allow_root_remote.sql`）
3. **MySQL 监听所有网卡**（`my.ini` 中 `bind-address=0.0.0.0`）
4. **Windows 防火墙放行 TCP 3306**

---

## 二、建库建表（从建库开始）

### 2.1 确认 MySQL 服务已启动

1. 按 `Win + R`，输入 `services.msc`，回车
2. 找到服务名 **MySQL**，状态应为 **正在运行**
3. 若未运行：右键 → **启动**

或在 PowerShell 中：

```powershell
Get-Service MySQL
```

### 2.2 执行建表脚本

项目 SQL 文件：

| 文件 | 作用 |
|------|------|
| `sql/schema.sql` | 创建数据库 `charging_bigdata`、7 张 MR 结果表、3 个 BI 视图 |
| `sql/allow_root_remote.sql` | 创建 `root@'%'` 并授权 |

**方式 A：CMD（推荐）**

```cmd
E:\mysql-8.4.8-winx64\bin\mysql.exe -uroot -p123456 < "F:\项目2资料\charging-bigdata\sql\schema.sql"
E:\mysql-8.4.8-winx64\bin\mysql.exe -uroot -p123456 < "F:\项目2资料\charging-bigdata\sql\allow_root_remote.sql"
```

**方式 B：MySQL 命令行交互**

```cmd
E:\mysql-8.4.8-winx64\bin\mysql.exe -uroot -p123456
```

```sql
SOURCE F:/项目2资料/charging-bigdata/sql/schema.sql;
SOURCE F:/项目2资料/charging-bigdata/sql/allow_root_remote.sql;
```

### 2.3 验证建库结果

```cmd
E:\mysql-8.4.8-winx64\bin\mysql.exe -uroot -p123456 -e "SHOW TABLES FROM charging_bigdata;"
```

应看到 7 张表：

- `t_voltage_current`（v1）
- `t_cell_voltage_range`（v2）
- `t_temperature`（v3）
- `t_energy_capacity`（v4）
- `t_charge_current_stats`（v5）
- `t_voltage_current_relation`（v6）
- `t_soc_temperature`（v7）

以及 3 个视图：`v_voltage_current`、`v_temperature`、`v_soc_temperature`。

验证远程用户：

```cmd
E:\mysql-8.4.8-winx64\bin\mysql.exe -uroot -p123456 -e "SELECT user,host FROM mysql.user WHERE user='root';"
```

应包含：

| user | host |
|------|------|
| root | localhost |
| root | % |

---

## 三、配置 my.ini（bind-address=0.0.0.0）

### 3.1 找到配置文件

MySQL 8.4 在 Windows 上按以下顺序查找配置（找到第一个即使用）：

1. `C:\Windows\my.ini`
2. `C:\my.ini`
3. `E:\mysql-8.4.8-winx64\my.ini` ← **本项目使用此路径**

查看当前生效的绑定地址：

```cmd
E:\mysql-8.4.8-winx64\bin\mysql.exe -uroot -p123456 -e "SHOW VARIABLES LIKE 'bind_address';"
```

- `*` 或 `0.0.0.0`：已监听所有网卡，虚拟机可连
- `127.0.0.1`：仅本机，需修改配置

### 3.2 创建 / 编辑 my.ini

用**管理员身份**打开记事本，编辑：

```
E:\mysql-8.4.8-winx64\my.ini
```

写入（或确认包含）以下内容：

```ini
[mysqld]
# 监听所有网卡，允许虚拟机通过 10.0.2.2 访问
bind-address=0.0.0.0
port=3306
basedir=E:/mysql-8.4.8-winx64
datadir=E:/mysql-8.4.8-winx64/data
max_connections=200
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci

[client]
port=3306
default-character-set=utf8mb4
```

> **说明**：MySQL 8.4 默认 `bind_address=*` 已等价于监听所有地址；写入 `my.ini` 是为了重启后配置持久化。

### 3.3 重启 MySQL 服务

**图形界面：**

1. `Win + R` → `services.msc`
2. 找到 **MySQL** → 右键 → **重新启动**

**PowerShell（需管理员）：**

```powershell
Restart-Service MySQL
```

### 3.4 确认端口监听

```cmd
netstat -an | findstr 3306
```

应看到：

```text
TCP    0.0.0.0:3306           0.0.0.0:0              LISTENING
```

若只有 `127.0.0.1:3306`，说明 `bind-address` 未生效，请检查 `my.ini` 路径并重新启动服务。

---

## 四、Windows 防火墙放行 TCP 3306

### 4.1 图形界面（详细步骤）

1. 按 `Win + S`，搜索 **Windows Defender 防火墙**，打开
2. 左侧点击 **高级设置**（或搜索「具有高级安全性的 Windows Defender 防火墙」）
3. 左侧选择 **入站规则**
4. 右侧点击 **新建规则…**
5. **规则类型**：选择 **端口** → 下一步
6. **协议和端口**：
   - 选择 **TCP**
   - 选择 **特定本地端口**，输入 `3306` → 下一步
7. **操作**：选择 **允许连接** → 下一步
8. **配置文件**：勾选 **域**、**专用**、**公用**（全选）→ 下一步
9. **名称**：输入 `MySQL Server 3306` → 完成

### 4.2 命令行（需管理员 PowerShell / CMD）

```cmd
netsh advfirewall firewall add rule name="MySQL Server 3306" dir=in action=allow protocol=TCP localport=3306 profile=any
```

查看是否已添加：

```cmd
netsh advfirewall firewall show rule name="MySQL Server 3306"
```

### 4.3 若仍连不上

- 确认 VirtualBox 网络为 **NAT**（默认网关 `10.0.2.2` 即宿主机）
- 临时关闭防火墙测试（仅调试用，测完恢复）：
  ```cmd
  netsh advfirewall set allprofiles state off
  ```
- 第三方安全软件（360、火绒等）也可能拦截 3306，需单独放行

---

## 五、虚拟机侧连通性测试

在 Ubuntu 虚拟机中执行：

```bash
# Ubuntu 18.04 任选其一（推荐第一个）
sudo apt-get update
sudo apt-get install -y mysql-client
# 若提示找不到包，改用：
# sudo apt-get install -y mysql-client-5.7
# 或：sudo apt-get install -y mariadb-client

# 测试连接
mysql -h 10.0.2.2 -uroot -p123456 charging_bigdata -e "SELECT 1 AS ok;"
```

成功输出：

```text
+----+
| ok |
+----+
|  1 |
+----+
```

---

## 六、运行 ETL 流水线入库

MapReduce 已在 HDFS 跑通后，在虚拟机执行：

```bash
cd /media/sf_cs-/charging-bigdata
# 首次需要 pymysql（Ubuntu 18.04 用 apt 最快）
sudo apt-get update
sudo apt-get install -y python3-pymysql
SKIP_MR=1 bash scripts/run-pipeline.sh
```

`SKIP_MR=1` 表示跳过 MR，只执行 HDFS → MySQL 入库。

配置文件 `config/pipeline.env` 关键项：

```env
MYSQL_HOST=10.0.2.2
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=123456
MYSQL_DATABASE=charging_bigdata
```

### 验证入库数据

Windows 本机：

```cmd
E:\mysql-8.4.8-winx64\bin\mysql.exe -uroot -p123456 charging_bigdata -e "SELECT COUNT(*) FROM t_voltage_current; SELECT COUNT(*) FROM t_soc_temperature;"
```

或在虚拟机：

```bash
mysql -h 10.0.2.2 -uroot -p123456 charging_bigdata -e "SHOW TABLES;"
```

---

## 七、后端 FastAPI 连接（本机）

`backend/.env` 使用本机地址：

```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=123456
MYSQL_DATABASE=charging_bigdata
```

启动后端后，BI 接口即可读取 MySQL 中的 MR 汇总数据。

---

## 八、常见问题

| 现象 | 原因 | 处理 |
|------|------|------|
| `Access denied for user 'root'@'10.0.2.x'` | 未执行 `allow_root_remote.sql` | 重新执行授权脚本 |
| `Can't connect to MySQL server` | 防火墙未放行或 bind-address 为 127.0.0.1 | 检查第四节、第三节 |
| `Host 'xxx' is not allowed` | root 仅有 localhost | `CREATE USER 'root'@'%' ...` |
| 重启服务失败 | 非管理员权限 | 以管理员运行 PowerShell |
| `my.ini` 不生效 | 路径不对 | 确认服务读取的是 `E:\mysql-8.4.8-winx64\my.ini` |

---

## 九、安全提示（实践环境）

- `root@'%'` 密码为弱口令 `123456`，**仅用于本机实训**，勿暴露到公网
- `config/pipeline.env` 和 `backend/.env` 已加入 `.gitignore`，勿提交密码
- 生产环境应使用专用 ETL 账号 + 强密码 + 仅授权必要库表

---

## 十、快速检查清单

- [ ] `charging_bigdata` 库及 7 张表已创建
- [ ] `root@'%'` 已存在
- [ ] `bind_address` 为 `*` 或 `0.0.0.0`
- [ ] `netstat` 显示 `0.0.0.0:3306 LISTENING`
- [ ] 防火墙入站规则已放行 TCP 3306
- [ ] 虚拟机 `mysql -h 10.0.2.2` 测试通过
- [ ] `SKIP_MR=1 bash scripts/run-pipeline.sh` 入库成功

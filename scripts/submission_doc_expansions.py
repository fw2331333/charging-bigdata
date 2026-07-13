# -*- coding: utf-8 -*-
"""文档后几章扩写内容（对齐公众监督模板篇幅）。"""
from __future__ import annotations

from docx_builder import add_bullets, add_h, add_p, add_placeholder_figure, add_table


def expand_outline_ch4(doc) -> None:
    """概要设计第4章：各模块实现说明（对齐模板每节 200+ 字）。"""
    add_h(doc, "4.1 登录鉴权模块实现", 2)
    add_p(
        doc,
        "运营管理员在 LoginView.vue 输入邮箱与密码，前端 axios 调用 POST /api/v1/auth/login。"
        "AuthService 根据 email 查询 sys_user，使用 passlib bcrypt 校验 password_hash；"
        "通过后 JwtService 签发 access_token（含 sub、role、exp）与随机 refresh_token。"
        "refresh_token 的 SHA256 哈希写入 sys_refresh_token 表，前端 Pinia auth store 持久化双令牌。"
        "Router beforeEach 检查 meta.requiresAuth，未登录重定向 /login；"
        "axios 响应拦截器在 401 时自动 POST /auth/refresh 轮换令牌后重试原请求。",
    )
    add_p(
        doc,
        "注册流程：RegisterView 提交邮箱与用户名，后端创建待验证用户并写入 sys_email_verification_token，"
        "EmailService 通过 SMTP 发送验证链接；用户访问 /set-password 完成设密并置 email_verified=1。"
        "管理员账号 role=admin，可访问 /bi/cache/invalidate、/predict/reload-models、/assistant/reindex。"
        "个人资料修改走 sys_profile_otp 邮箱验证码，防止越权改密。",
    )
    add_placeholder_figure(doc, "图4-1 登录鉴权时序图", "用户-LoginView-Nginx-AuthAPI-AuthService-MySQL")

    add_h(doc, "4.2 MapReduce 批处理与入库模块实现", 2)
    add_p(
        doc,
        "数据分析师将四份 CSV 上传 HDFS /Car/ 后，在 Master 节点执行 hadoop jar cbp-mr.jar com.cbp.mr.JobRunner。"
        "JobRunner 顺序提交 v1~v7：v1 按小时键聚合 pack_voltage 与 charge_current 双均值；"
        "v2 统计单体电压 hourly max/min；v3 按时间点记录温度极值；v4 平均可用能量与容量；"
        "v5 充电电流均值与峰值；v6 保留时间点电压电流对；v7 按 SOC 十分位分段统计温度均值。"
        "输出统一为 key\\tmetric1\\tmetric2 文本，存放于 /Car/output/vN/part-r-00000。",
    )
    add_p(
        doc,
        "load_mr_to_mysql.py 通过 WebHDFS 或本地路径读取 part-r-00000，按 TAB 分隔解析字段，"
        "对 t_voltage_current 等七表执行 INSERT ... ON DUPLICATE KEY UPDATE，保证重复灌数幂等。"
        "脚本读取 pipeline.env 中的 MYSQL_HOST、库名与账号，与 Docker 演示环境或集群侧 MySQL 桥接一致。"
        "入库完成后可调用 POST /bi/cache/invalidate-pipeline 清空 FastAPI 进程内 BI 缓存。",
    )
    add_placeholder_figure(doc, "图4-2 MR 批处理入库流程图", "HDFS→YARN→MR→ETL→MySQL")

    add_h(doc, "4.3 BI 展示模块实现", 2)
    add_p(
        doc,
        "Web 端 MrBiView.vue 在 onMounted 时根据 bi_chart_view 配置并行请求 GET /api/v1/bi/* 系列接口。"
        "BiRepository 对 t_voltage_current、t_temperature 等表执行参数化 SQL，BiService 将结果 JSON 化并写入内存缓存。"
        "前端 AsyncMrEchart 组件将 record_hour 格式化为可读横轴，构建双轴折线、柱状与热力图 option。"
        "Datart BI 通过 JDBC 连接同一 MySQL 库，读取 v_voltage_current 等视图配置大屏；"
        "分享页 URL 配置于前端环境变量 VITE_DATART_DASHBOARD_URL，首页卡片可新窗口打开。",
    )
    add_placeholder_figure(doc, "图4-3 BI 查询时序图", "用户-Vue3-BiAPI-BiService-MySQL-缓存")

    add_h(doc, "4.4 机器学习预测模块实现", 2)
    add_p(
        doc,
        "train_all_models.py 从 nvv2t_md.csv 读取充电会话特征，对费用预测比较 LinearRegression 与 XGBoost，"
        "按 RMSE 选优保存 fee_model.pkl；同时训练时长回归、平台分类、SOC 回归模型至 analytics/output/models/。"
        "FastAPI 启动时 PredictService 加载四个 joblib 模型；用户在各 PredictView Tab 填写表单后 "
        "POST /predict/fee|duration|platform|soc，服务层完成特征向量变换并返回 predicted_* 与 algorithm 字段。"
        "管理员 POST /predict/reload-models 可在不重启容器的情况下热加载磁盘上新训练的 pkl 文件。",
    )
    add_placeholder_figure(doc, "图4-4 费用预测时序图", "用户-PredictView-API-PredictService-pkl")

    add_h(doc, "4.5 智能助手模块实现", 2)
    add_p(
        doc,
        "AssistantDrawer 组件将用户问题 POST 至 /api/v1/assistant/chat/stream，后端以 SSE 流式返回。"
        "AssistantService 先用 Chroma 向量库检索 Top-K 文档片段（索引范围含 docs/、sql/ 注释与 README），"
        "再拼接 System Prompt 调用 DeepSeek 兼容 API 生成回答；前端逐块渲染 Markdown。"
        "管理员 POST /assistant/reindex 可在项目文档更新后重建 bge-small-zh Embedding 索引。"
        "助手不直接查询 HDFS 实时数据，但可回答表结构、部署命令与 API 说明类问题，辅助技术说明与运维答疑。",
    )
    add_placeholder_figure(doc, "图4-5 智能助手时序图", "用户-AssistantAPI-RAG-LLM-SSE")


def expand_srs_mid_chapters(doc) -> None:
    """SRS 第6~7章扩写（页面交互与非功能各小节多段）。"""
    add_h(doc, "6.6 智能助手页", 2)
    add_p(
        doc,
        "助手面板支持固定于右侧抽屉，输入框支持多行文本与 Enter 发送。"
        "流式响应以 SSE 方式追加至消息列表，助手消息支持代码块与列表 Markdown 渲染。"
        "网络异常时展示重试按钮；管理员可在后台重建 RAG 索引以更新问答知识库。",
    )
    add_h(doc, "6.7 MR BI 内嵌页", 2)
    add_p(
        doc,
        "mr-bi 路由隐藏默认页头，七张 MR 图按 bi_chart_view 配置栅格排列，"
        "每张图支持全屏展开与刷新；数据为空时展示 el-empty 并提示检查 ETL 是否完成。",
    )


def expand_srs_ch7_extra(doc) -> None:
    add_h(doc, "7.6 易用性需求", 2)
    add_p(
        doc,
        "登录页提供演示账号提示；表单校验错误信息中文化且就地展示；"
        "分析页图表支持缩放、数据点 tooltip 与图例切换；预测页展示模型名称增强可解释性。",
    )
    add_h(doc, "7.7 可测试性需求", 2)
    add_p(
        doc,
        "提供 /health 与 /health/ready 探针；Swagger /docs 支持接口调试；"
        "scripts/verify-pipeline.sh 可自动检查 HDFS 文件数、MySQL 表行数与 API 连通性，作为上线前自检项。",
    )


def expand_srs_late_chapters(doc) -> None:
    """SRS 第8~9章：验收、测试、附录。"""
    add_h(doc, "第8章 完成标准与测试需求", 1)
    add_h(doc, "8.1 质量确认原则", 2)
    add_p(
        doc,
        "系统验收以「功能完整、数据真实、文档齐全、演示可用」为原则。"
        "功能确认对照本文档 FR-01~FR-08 逐条核查；数据确认要求 MR 七表、ADS 五表存在非空记录且与 HDFS 批处理输出一致；"
        "文档确认要求需求规格、概要设计、数据库设计、数据字典（xls）、接口文档、部署手册与实训报告交叉引用一致；"
        "演示确认要求在浏览器可完成登录、查看分析图表、执行四项预测，公网环境 http://115.29.194.137:8080 可访问。",
    )
    add_h(doc, "8.2 功能确认用例", 2)
    add_table(
        doc,
        ["编号", "确认项", "操作步骤", "预期结果"],
        [
            ["AT-01", "HDFS 数据准备", "hdfs dfs -ls /Car", "列出 4 个 CSV"],
            ["AT-02", "MR v1~v7", "JobRunner 全量执行", "七目录 part-r-00000 非空"],
            ["AT-03", "MySQL 入库", "load_mr_to_mysql.py", "七表行数>0，可重复执行"],
            ["AT-04", "ADS 五表", "Spark/Python ETL", "t_soc_hourly 等有数据"],
            ["AT-05", "用户登录", "POST /auth/login", "返回 Token 对"],
            ["AT-06", "未授权访问", "无 Token 访问 /bi", "HTTP 401"],
            ["AT-07", "BI 查询", "GET /bi/voltage-current", "JSON 时序数组"],
            ["AT-08", "费用预测", "POST /predict/fee", "含 predicted_fee"],
            ["AT-09", "智能助手", "POST /assistant/chat/stream", "SSE 流式文本"],
            ["AT-10", "Docker 部署", "docker compose up", "三服务 healthy"],
        ],
    )
    add_h(doc, "8.3 非功能确认", 2)
    add_p(
        doc,
        "性能：在演示数据集下，BI 接口缓存命中后 P95 响应时间不超过 2 秒；"
        "单次 ML 预测接口响应不超过 500 毫秒；MapReduce 七任务总耗时在课程数据规模内不超过 30 分钟。"
        "安全：sys_user.password_hash 字段不得出现明文密码；业务 API 除登录与健康检查外均需 Bearer JWT；"
        "管理员接口须 role=admin。可靠性：重复执行入库脚本不产生重复业务键记录；"
        "Refresh Token 轮换后旧令牌不可再次使用。兼容性：Chrome、Edge 最新版下页面布局正常，分辨率不低于 1280×720。",
    )
    add_h(doc, "8.4 测试环境与数据", 2)
    add_p(
        doc,
        "测试环境包括：三节点 Hadoop 集群（HDFS+YARN）、MySQL 8.0 charging_bigdata、"
        "Docker Compose 云演示环境（mysql/backend/frontend）。"
        "测试数据为四个课程 CSV：dsv13r1.csv、dsv13r2.csv、nvv2t.csv、nvv2t_md.csv，"
        "存放于 F:\\项目2资料\\数据集\\，上传 HDFS /Car/ 后不得修改字段顺序与分隔符。"
        "回归测试在每次 MR 作业或入库脚本变更后执行 AT-02~AT-08 子集。",
    )
    add_h(doc, "8.5 交付物清单", 2)
    add_bullets(
        doc,
        [
            "项目源码 charging-bigdata（不含 dataset 与 .env）；",
            "需求规格说明书、概要设计说明书、数据库设计说明书 Word；",
            "数据字典 xls（本库全部表字段）；",
            "接口文档、部署手册、实训报告册；",
            "用例图/流程图/时序图/ER 图 PNG；",
            "页面效果图与演示视频（可选）。",
        ],
    )

    add_h(doc, "第9章 附录", 1)
    add_h(doc, "9.1 需求追踪矩阵（摘录）", 2)
    add_table(
        doc,
        ["FR 编号", "设计文档", "实现模块", "测试用例"],
        [
            ["FR-01", "概要设计 3.3", "hdfs dfs -put", "AT-01"],
            ["FR-02", "概要设计 8.1", "mapreduce/JobRunner", "AT-02"],
            ["FR-03", "数据库设计", "load_mr_to_mysql.py", "AT-03"],
            ["FR-06", "概要设计 9.2", "train_all_models.py", "AT-08"],
            ["FR-07", "概要设计 6.x", "frontend/views", "AT-07"],
            ["FR-08", "概要设计 4.1", "backend/auth", "AT-05/06"],
        ],
    )
    add_h(doc, "9.2 缩略语", 2)
    add_table(
        doc,
        ["缩略语", "全称", "说明"],
        [
            ["CBP", "Charging Bigdata Platform", "本项目产品代号"],
            ["SRS", "Software Requirements Specification", "软件需求规格说明书"],
            ["MR", "MapReduce", "Hadoop 批处理"],
            ["ADS", "Application Data Service", "应用汇总层"],
            ["JWT", "JSON Web Token", "访问令牌"],
            ["RAG", "Retrieval-Augmented Generation", "检索增强生成"],
            ["SSE", "Server-Sent Events", "服务端推送流"],
        ],
    )
    add_h(doc, "9.3 待决问题", 2)
    add_p(
        doc,
        "邮件 SMTP 在部分校园网环境下需额外配置，现场演示可跳过注册邮件流程，使用种子账号登录。"
        "Datart BI 为独立进程，若分享页缓存导致图表不刷新，需 Ctrl+F5 强刷或重启 datart 容器。"
        "三节点集群在仅有两台物理机时可降为双节点（replication=2），须在部署文档中说明与课程要求的差异。",
    )


def expand_outline_late_chapters(doc) -> None:
    """概要设计第5~7章扩写（对齐模板：ER、页面、非功能各小节多段）。"""
    # 在第5章原内容后追加细化（调用方在 add_h 第5章 之后插入本函数前半）
    pass  # 由 expand_outline_ch5/ch6/ch7 分函数


def expand_outline_ch5(doc) -> None:
    add_h(doc, "5.1 MR 域实体说明", 2)
    add_p(
        doc,
        "MR 域以时间键或 SOC 桶为粒度存储聚合指标，七张表在逻辑上均来源于 HDFS dsv13r1.csv 的同一份明细，"
        "彼此无数据库外键约束，通过 record_hour、record_time、soc_bucket 在应用层与 BI 大屏按时间轴联动。"
        "t_voltage_current 与 t_charge_current_stats 均含充电电流字段但统计口径不同：前者与组电压配对求小时均值，"
        "后者单独统计小时均值与峰值，供不同图表使用。",
    )
    add_p(
        doc,
        "t_cell_voltage_range 记录每小时单体电压极值，用于发现单体不一致风险；"
        "t_temperature 以 yyyyMMddHHmmss 为键保留细粒度温度波动；"
        "t_energy_capacity 反映可用能量与容量趋势；"
        "t_voltage_current_relation 保留散点级电压电流对，供关系分析；"
        "t_soc_temperature 按 SOC 十分位分段统计热特性，支撑电池热管理分析。",
    )
    add_h(doc, "5.2 ADS 域实体说明", 2)
    add_p(
        doc,
        "ADS 五表由 Python/Spark 脚本从 dsv13r2.csv、nvv2t.csv 聚合写入，面向 Web 分析页与 Datart 大屏。"
        "t_soc_hourly 支撑 SOC 折线图；t_charging_daily 与 t_charging_monthly 支撑充电频次分析；"
        "t_charge_rate_hourly 按一天 24 小时统计平均充电速率；"
        "t_soc_heatmap 以 (record_day, hour_key) 联合唯一键存储二维热力图数据。",
    )
    add_h(doc, "5.3 认证域实体说明", 2)
    add_p(
        doc,
        "sys_user 为认证中心实体，username 与 email 唯一；sys_refresh_token 与 sys_user 为 1:N，"
        "存储 Refresh Token 哈希支持轮换吊销；sys_email_verification_token 支持注册验证与密码重置；"
        "sys_profile_otp 支持已登录用户修改密码时的邮箱验证码；"
        "sys_token_blacklist 可选记录已登出 Access Token 的 jti，用于有状态黑名单扩展。",
    )
    add_h(doc, "5.4 逻辑关系 R01~R17", 2)
    add_table(
        doc,
        ["编号", "左实体", "右实体", "基数", "说明"],
        [
            ["R01~R07", "HDFS dsv13r1", "MR 七表", "1:N", "批处理产出"],
            ["R08~R12", "HDFS dsv13r2/nvv2t", "ADS 五表", "1:N", "ETL 聚合"],
            ["R13", "sys_user", "sys_refresh_token", "1:N", "多设备登录"],
            ["R14", "sys_user", "sys_email_verification_token", "1:N", "邮件令牌"],
            ["R15~R17", "MR 表", "BI 视图", "1:1", "v_* 简化查询"],
        ],
    )


def expand_outline_ch6(doc) -> None:
    add_h(doc, "6.1 Web 分析子系统界面", 2)
    add_p(
        doc,
        "分析子系统采用左侧导航 + 右侧图表区布局。顶栏高度 56px，含 Logo、模块菜单、语言切换与用户头像下拉。"
        "左侧菜单按业务分组：充电行为（bda1）、SOC 分析（bda2）、充电时长（bda3）、充电速率（bda4）、"
        "性能报告（bda5）、MR BI 大屏（mr-bi）。右侧内容区最小宽度 960px，图表卡片垂直排列，"
        "每张卡片含标题、工具栏（刷新/全屏）与 ECharts 画布，最小高度 320px。",
    )
    add_p(
        doc,
        "充电次数页（bda1）上方为日期范围筛选，下方并排日充电折线与月充电折线，"
        "数据来自 t_charging_daily、t_charging_monthly。SOC 页（bda2）含折线图与热力图 Tab，"
        "热力图横轴为 0~23 时，纵轴为日期，颜色映射 avg_soc。"
        "充电速率页（bda4）展示 24 小时平均速率折线。性能报告页（bda5）以表格+图表展示电池分类结果。",
    )
    add_h(doc, "6.2 预测子系统界面", 2)
    add_p(
        doc,
        "预测子系统采用顶部 Tab 切换四项任务：SOC、时长、费用、平台。"
        "每个 Tab 左侧为 Element Plus 表单，字段标签与训练特征一致，含单位提示与必填校验；"
        "右侧为结果卡片，展示预测值、模型名称（linear_regression/xgboost 等）与提交时间。"
        "移动端（宽度<768px）表单与结果上下堆叠，Tab 可横向滚动。",
    )
    add_h(doc, "6.3 BI 大屏与智能助手界面", 2)
    add_p(
        doc,
        "MR BI 页（mr-bi）采用 2×4 或 3×3 栅格铺满视口，七张 MR 图按 bi_chart_view.sort_order 排列，"
        "隐藏默认页头以沉浸式展示。Datart 外链在新窗口打开，分辨率建议 1920×1080。"
        "智能助手以右侧抽屉或底部面板形式出现，对话区滚动展示历史消息，"
        "用户消息右对齐蓝色气泡，助手消息左对齐灰色气泡并支持 Markdown 代码块；"
        "流式输出时显示闪烁光标，输入框支持 Enter 发送、Shift+Enter 换行。",
    )


def expand_outline_ch7(doc) -> None:
    add_h(doc, "7.1 性能设计说明", 2)
    add_p(
        doc,
        "BI 层在 bi_service 实现进程内 dict 缓存，键为 SQL 与参数哈希，TTL 与手动失效并存；"
        "ETL 完成后调用 /bi/cache/invalidate-pipeline 批量清空，避免脏读。"
        "预测层模型在应用启动时一次性 joblib.load，推理仅做向量变换，避免每次请求磁盘 IO。"
        "前端对 ECharts 实例按需创建，路由 keepAlive 缓存已访问分析页组件状态。"
        "MR 层通过 Combiner 减少 Shuffle 数据量，YARN 内存参数按数据规模调优。",
    )
    add_h(doc, "7.2 可靠性设计说明", 2)
    add_p(
        doc,
        "入库脚本对七张 MR 表使用 INSERT ... ON DUPLICATE KEY UPDATE，支持发布前重复灌数。"
        "Docker Compose 为 mysql 配置 healthcheck，backend depends_on condition service_healthy。"
        "Refresh Token 刷新流程在数据库层使用事务：吊销旧令牌与插入新令牌原子完成。"
        "HDFS 副本数设为 2（双节点集群）或 3（三节点），防止 DataNode 单点丢块。",
    )
    add_h(doc, "7.3 安全设计说明", 2)
    add_p(
        doc,
        "密码全生命周期使用 bcrypt 哈希，注册与改密接口永不记录明文。"
        "JWT_SECRET、SMTP、LLM_API_KEY 仅通过环境变量注入，.env.docker 不入 Git。"
        "业务 API 使用 OAuth2 Password Bearer，Access Token 短有效期降低泄露风险。"
        "CORS_ORIGINS 白名单限制浏览器来源；管理员接口统一 require_admin 依赖校验 role 字段。",
    )
    add_h(doc, "7.4 可维护性设计说明", 2)
    add_p(
        doc,
        "后端严格 api → services → repositories 分层，禁止在 endpoint 中拼接 SQL。"
        "MR 作业通过 JobRunner 统一调度，新增 v8 仅需 Java 类 + 表 DDL + 入库映射。"
        "SQL 迁移脚本按序号存放 sql/migrations/，Docker init 与手工升级共用。"
        "文档由 generate_submission_docs_full.py 与 generate_data_dictionary_xls.py 统一生成，保证版本一致。",
    )
    add_h(doc, "7.5 可移植性设计说明", 2)
    add_p(
        doc,
        "应用层 FastAPI 无状态，可水平扩容多实例 behind Nginx；JWT 校验不依赖单机 Session。"
        "BI 可视化可切换 Datart、DataEase 或纯 Vue ECharts，只要 JDBC/SQL 指向同一 MySQL。"
        "智能助手 LLM 与 Embedding 通过配置切换 OpenAI 兼容接口与本地模型。"
        "MapReduce 可渐进迁移 Spark，只要保持 MySQL 表结构契约不变。",
    )
    add_h(doc, "7.6 其他非功能性设计说明", 2)
    add_p(
        doc,
        "可用性：表单校验错误就地提示；图表空数据展示 el-empty 引导用户检查 ETL。"
        "兼容性：前端支持 Chrome/Edge 最新两个大版本；后端 Python 3.11+；MR 编译目标 JDK 8。"
        "国际化：前端 locale store 支持中英文切换，API 错误消息可扩展 i18n。"
        "可测试性：/health、/health/ready 探针供 CI 与 Docker 使用；Swagger /docs 支持接口调试。",
    )


def expand_training_late_chapters(doc) -> None:
    """东软实训报告第七~九章扩写。"""
    add_h(doc, "七、项目总结", 1)
    add_h(doc, "7.1 项目成果概述", 2)
    add_p(
        doc,
        "新能源充电桩大数据分析项目（CBP）已完成从原始 CSV 到 Web 展示的端到端链路："
        "HDFS 四文件存储、MapReduce v1~v7 七项电池指标批处理、MySQL charging_bigdata 持久化、"
        "ADS 五表汇总、四项机器学习在线预测、Vue3+FastAPI 全栈 Web、JWT 鉴权、"
        "Docker 云部署与 RAG 智能助手扩展。公网演示地址 http://115.29.194.137:8080 稳定运行，"
        "满足需求规格说明书规定的全部 P0 指标。",
    )
    add_h(doc, "7.2 技术难点与突破", 2)
    add_p(
        doc,
        "难点一：无表头 CSV 字段解析。通过 RecordParser 统一下标与坏行 Counter，七个 MR 作业复用 BatteryMapper 基类，"
        "避免重复解析逻辑。难点二：双节点 Hadoop 与 Windows 宿主机 MySQL 跨网 ETL。"
        "通过 pipeline.env 配置 JDBC 桥接 IP、清理 dfs/data 解决 ClusterID 冲突。"
        "难点三：JWT Refresh 并发刷新导致令牌失效，在 auth_service 中用事务与行锁保证单次轮换。"
        "难点四：Datart RC 版本分享页缓存，通过强刷与 invalidate BI cache 接口解决。",
    )
    add_h(doc, "7.3 经验与教训", 2)
    add_p(
        doc,
        "文档应先于编码冻结接口与表结构，可减少联调返工。"
        "Hadoop 集群 hosts 与 127.0.1.1 主机名冲突是常见坑，须统一使用 hadoop-master 等固定主机名。"
        "Docker 多服务启动顺序依赖 healthcheck，不可省略 mysql 就绪等待。"
        "现场演示应准备 HDFS/MR/MySQL 截图备用，防止网络波动。",
    )
    add_h(doc, "7.4 个人收获（请填写）", 2)
    add_p(
        doc,
        "【请填写姓名】通过本项目掌握了 MapReduce 编程模型、FastAPI 分层架构、Vue3 组合式 API、"
        "MySQL 建模与 UPSERT 策略、Docker Compose 部署及技术文档编写规范。"
        "最大的收获是能够独立排查 HDFS→MR→MySQL→API→浏览器全链路数据断点。",
    )
    add_p(
        doc,
        "【请填写姓名】同学主要负责【请填写模块】，在实现过程中深入学习了【请填写技术点】，"
        "遇到【请填写困难】后通过【请填写解决方法】成功解决，"
        "体会到团队协作与文档先行对项目进度的重要性。",
    )

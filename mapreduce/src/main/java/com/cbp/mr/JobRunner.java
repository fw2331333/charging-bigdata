package com.cbp.mr;

import com.cbp.mr.v1.V1VoltageCurrentHourly;
import com.cbp.mr.v2.V2CellVoltageRange;
import com.cbp.mr.v3.V3TemperatureTrend;
import com.cbp.mr.v4.V4EnergyCapacityTrend;
import com.cbp.mr.v5.V5ChargeCurrentStats;
import com.cbp.mr.v6.V6VoltageCurrentRelation;
import com.cbp.mr.v7.V7SocTemperature;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;

/**
 * MapReduce 批处理编排器：顺序执行 v1~v7，结果写入 HDFS 分区目录。
 *
 * <p>设计约定：
 * <ul>
 *   <li>计算层只产出 HDFS 文件，不直连 MySQL（入库由 ETL 层负责）</li>
 *   <li>每个任务输出 {@code {outputBase}/vN/part-r-00000}，供 analytics/etl 消费</li>
 *   <li>单任务失败时继续执行后续任务，最终按失败数返回退出码</li>
 * </ul>
 *
 * <p>用法：
 * <pre>
 *   hadoop jar charging-mapreduce-1.0.0.jar /Car/dsv13r1.csv /Car/output
 * </pre>
 */
public class JobRunner {

    /** 与 analytics/etl/mr_tasks.MR_ETL_TASKS 的 code 字段保持一致 */
    private static final Tool[] TASKS = {
            new V1VoltageCurrentHourly(),
            new V2CellVoltageRange(),
            new V3TemperatureTrend(),
            new V4EnergyCapacityTrend(),
            new V5ChargeCurrentStats(),
            new V6VoltageCurrentRelation(),
            new V7SocTemperature()
    };

    private static final String[] CODES = {"v1", "v2", "v3", "v4", "v5", "v6", "v7"};

    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("Usage: JobRunner <hdfs-input> <hdfs-output-base>");
            System.err.println("Example: JobRunner /Car/dsv13r1.csv /Car/output");
            System.exit(1);
        }

        String input = args[0];
        String outputBase = trimSlash(args[1]);
        Configuration conf = new Configuration();
        int failed = 0;

        for (int i = 0; i < TASKS.length; i++) {
            String code = CODES[i];
            String output = outputBase + "/" + code;
            System.out.println("==== Running " + code + " ====");
            int status = ToolRunner.run(conf, TASKS[i], new String[]{input, output});
            if (status != 0) {
                System.err.println("Task failed: " + code);
                failed++;
            }
        }

        System.exit(failed == 0 ? 0 : 1);
    }

    private static String trimSlash(String path) {
        if (path.endsWith("/")) {
            return path.substring(0, path.length() - 1);
        }
        return path;
    }
}

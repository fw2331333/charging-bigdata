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
 * 批量运行 v1~v7 共七个 MapReduce 任务（输入为 HDFS 上的 dsv13r1.csv）。
 */
public class JobRunner {

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

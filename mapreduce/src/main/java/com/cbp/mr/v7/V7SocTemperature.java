package com.cbp.mr.v7;

import com.cbp.mr.util.BatteryMapper;
import com.cbp.mr.util.BatteryStatusStatsReducer;
import com.cbp.mr.util.BatteryStatusUtil;
import com.cbp.mr.util.FieldIndex;
import com.cbp.mr.util.JobBuilder;
import com.cbp.mr.util.RecordParser;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;

import java.io.IOException;

/** v7：按电池状态统计最高/最低温度均值与方差 → t_soc_temperature */
public class V7SocTemperature extends Configured implements Tool {

    public static class V7Mapper extends BatteryMapper {
        @Override
        protected void mapRecord(String[] fields, Context context) throws IOException, InterruptedException {
            double soc = RecordParser.parseDouble(fields[FieldIndex.SOC], 0D);
            double maxTemp = RecordParser.parseDouble(fields[FieldIndex.MAX_TEMPERATURE], 0D);
            double minTemp = RecordParser.parseDouble(fields[FieldIndex.MIN_TEMPERATURE], 0D);
            context.write(
                    createKey(BatteryStatusUtil.fromSoc(soc)),
                    createValue(maxTemp + "," + minTemp)
            );
        }
    }

    @Override
    public int run(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("Usage: V7SocTemperature <input> <output>");
            return 1;
        }
        Job job = JobBuilder.createJob(getConf(), V7SocTemperature.class,
                "v7_battery_status_temperature", V7Mapper.class, BatteryStatusStatsReducer.class);
        JobBuilder.bindIo(job, getConf(), args[0], args[1]);
        return job.waitForCompletion(true) ? 0 : 1;
    }

    public static void main(String[] args) throws Exception {
        System.exit(ToolRunner.run(new Configuration(), new V7SocTemperature(), args));
    }
}

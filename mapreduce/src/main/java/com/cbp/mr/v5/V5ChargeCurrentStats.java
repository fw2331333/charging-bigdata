package com.cbp.mr.v5;

import com.cbp.mr.util.AvgMaxCombiner;
import com.cbp.mr.util.AvgMaxReducer;
import com.cbp.mr.util.BatteryMapper;
import com.cbp.mr.util.FieldIndex;
import com.cbp.mr.util.JobBuilder;
import com.cbp.mr.util.RecordParser;
import com.cbp.mr.util.TimeKeyUtil;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;

import java.io.IOException;

/** v5：按小时统计充电电流均值与最大值 → t_charge_current_stats */
public class V5ChargeCurrentStats extends Configured implements Tool {

    public static class V5Mapper extends BatteryMapper {
        @Override
        protected void mapRecord(String[] fields, Context context) throws IOException, InterruptedException {
            double current = RecordParser.parseDouble(fields[FieldIndex.CHARGE_CURRENT], 0D);
            context.write(
                    createKey(TimeKeyUtil.toHourKey(fields[FieldIndex.RECORD_TIME])),
                    createValue(AvgMaxReducer.metricValue(current))
            );
        }
    }

    @Override
    public int run(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("Usage: V5ChargeCurrentStats <input> <output>");
            return 1;
        }
        Job job = JobBuilder.createJob(getConf(), V5ChargeCurrentStats.class,
                "v5_charge_current_stats", V5Mapper.class, AvgMaxReducer.class);
        JobBuilder.setCombinerIfPresent(job, AvgMaxCombiner.class);
        JobBuilder.bindIo(job, getConf(), args[0], args[1]);
        return job.waitForCompletion(true) ? 0 : 1;
    }

    public static void main(String[] args) throws Exception {
        System.exit(ToolRunner.run(new Configuration(), new V5ChargeCurrentStats(), args));
    }
}

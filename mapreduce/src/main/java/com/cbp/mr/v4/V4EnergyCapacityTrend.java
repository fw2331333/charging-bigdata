package com.cbp.mr.v4;

import com.cbp.mr.util.Avg2Combiner;
import com.cbp.mr.util.Avg2Reducer;
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

/** v4：按小时统计平均可用能量与可用容量 → t_energy_capacity */
public class V4EnergyCapacityTrend extends Configured implements Tool {

    public static class V4Mapper extends BatteryMapper {
        @Override
        protected void mapRecord(String[] fields, Context context) throws IOException, InterruptedException {
            double energy = RecordParser.parseDouble(fields[FieldIndex.AVAILABLE_ENERGY], 0D);
            double capacity = RecordParser.parseDouble(fields[FieldIndex.AVAILABLE_CAPACITY], 0D);
            context.write(
                    createKey(TimeKeyUtil.toHourKey(fields[FieldIndex.RECORD_TIME])),
                    createValue(Avg2Reducer.pairValue(energy, capacity))
            );
        }
    }

    @Override
    public int run(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("Usage: V4EnergyCapacityTrend <input> <output>");
            return 1;
        }
        Job job = JobBuilder.createJob(getConf(), V4EnergyCapacityTrend.class,
                "v4_energy_capacity_trend", V4Mapper.class, Avg2Reducer.class);
        JobBuilder.setCombinerIfPresent(job, Avg2Combiner.class);
        JobBuilder.bindIo(job, getConf(), args[0], args[1]);
        return job.waitForCompletion(true) ? 0 : 1;
    }

    public static void main(String[] args) throws Exception {
        System.exit(ToolRunner.run(new Configuration(), new V4EnergyCapacityTrend(), args));
    }
}

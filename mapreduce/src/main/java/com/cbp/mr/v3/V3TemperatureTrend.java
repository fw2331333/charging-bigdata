package com.cbp.mr.v3;

import com.cbp.mr.util.BatteryMapper;
import com.cbp.mr.util.FieldIndex;
import com.cbp.mr.util.JobBuilder;
import com.cbp.mr.util.MaxMinCombiner;
import com.cbp.mr.util.MaxMinReducer;
import com.cbp.mr.util.RecordParser;
import com.cbp.mr.util.TimeKeyUtil;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;

import java.io.IOException;

/** v3：按时间点统计温度最高/最低值 → t_temperature */
public class V3TemperatureTrend extends Configured implements Tool {

    public static class V3Mapper extends BatteryMapper {
        @Override
        protected void mapRecord(String[] fields, Context context) throws IOException, InterruptedException {
            double maxTemp = RecordParser.parseDouble(fields[FieldIndex.MAX_TEMPERATURE], 0D);
            double minTemp = RecordParser.parseDouble(fields[FieldIndex.MIN_TEMPERATURE], 0D);
            context.write(
                    createKey(TimeKeyUtil.toTimePointKey(fields[FieldIndex.RECORD_TIME])),
                    createValue(MaxMinReducer.pairValue(maxTemp, minTemp))
            );
        }
    }

    @Override
    public int run(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("Usage: V3TemperatureTrend <input> <output>");
            return 1;
        }
        Job job = JobBuilder.createJob(getConf(), V3TemperatureTrend.class,
                "v3_temperature_trend", V3Mapper.class, MaxMinReducer.class);
        JobBuilder.setCombinerIfPresent(job, MaxMinCombiner.class);
        JobBuilder.bindIo(job, getConf(), args[0], args[1]);
        return job.waitForCompletion(true) ? 0 : 1;
    }

    public static void main(String[] args) throws Exception {
        System.exit(ToolRunner.run(new Configuration(), new V3TemperatureTrend(), args));
    }
}

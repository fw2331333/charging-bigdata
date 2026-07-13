package com.cbp.mr.v6;

import com.cbp.mr.util.BatteryMapper;
import com.cbp.mr.util.FieldIndex;
import com.cbp.mr.util.JobBuilder;
import com.cbp.mr.util.RecordParser;
import com.cbp.mr.util.TimeKeyUtil;
import com.cbp.mr.util.VoltageCurrentChangeRateReducer;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;

import java.io.IOException;

/** v6：按小时统计组电压与充电电流平均变化率（%） → t_voltage_current_relation */
public class V6VoltageCurrentRelation extends Configured implements Tool {

    public static class V6Mapper extends BatteryMapper {
        @Override
        protected void mapRecord(String[] fields, Context context) throws IOException, InterruptedException {
            String recordTime = fields[FieldIndex.RECORD_TIME];
            double voltage = RecordParser.parseDouble(fields[FieldIndex.PACK_VOLTAGE], 0D);
            double current = RecordParser.parseDouble(fields[FieldIndex.CHARGE_CURRENT], 0D);
            context.write(
                    createKey(TimeKeyUtil.toHourOfDayKey(recordTime)),
                    createValue(recordTime + "," + voltage + "," + current)
            );
        }
    }

    @Override
    public int run(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("Usage: V6VoltageCurrentRelation <input> <output>");
            return 1;
        }
        Job job = JobBuilder.createJob(getConf(), V6VoltageCurrentRelation.class,
                "v6_voltage_change_rate", V6Mapper.class, VoltageCurrentChangeRateReducer.class);
        JobBuilder.bindIo(job, getConf(), args[0], args[1]);
        return job.waitForCompletion(true) ? 0 : 1;
    }

    public static void main(String[] args) throws Exception {
        System.exit(ToolRunner.run(new Configuration(), new V6VoltageCurrentRelation(), args));
    }
}

package com.cbp.mr.v2;

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

/** v2：按小时统计单体电压最高/最低值 → t_cell_voltage_range */
public class V2CellVoltageRange extends Configured implements Tool {

    public static class V2Mapper extends BatteryMapper {
        @Override
        protected void mapRecord(String[] fields, Context context) throws IOException, InterruptedException {
            double maxCell = RecordParser.parseDouble(fields[FieldIndex.MAX_CELL_VOLTAGE], 0D);
            double minCell = RecordParser.parseDouble(fields[FieldIndex.MIN_CELL_VOLTAGE], 0D);
            context.write(
                    createKey(TimeKeyUtil.toHourKey(fields[FieldIndex.RECORD_TIME])),
                    createValue(MaxMinReducer.pairValue(maxCell, minCell))
            );
        }
    }

    @Override
    public int run(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("Usage: V2CellVoltageRange <input> <output>");
            return 1;
        }
        Job job = JobBuilder.createJob(getConf(), V2CellVoltageRange.class,
                "v2_cell_voltage_range", V2Mapper.class, MaxMinReducer.class);
        JobBuilder.setCombinerIfPresent(job, MaxMinCombiner.class);
        JobBuilder.bindIo(job, getConf(), args[0], args[1]);
        return job.waitForCompletion(true) ? 0 : 1;
    }

    public static void main(String[] args) throws Exception {
        System.exit(ToolRunner.run(new Configuration(), new V2CellVoltageRange(), args));
    }
}

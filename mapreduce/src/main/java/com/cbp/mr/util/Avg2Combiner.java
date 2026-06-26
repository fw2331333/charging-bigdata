package com.cbp.mr.util;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

import java.io.IOException;

/** Combiner：局部聚合双指标均值，中间格式 sum1,sum2,count */
public class Avg2Combiner extends Reducer<Text, Text, Text, Text> {

    private final Text outVal = new Text();

    @Override
    protected void reduce(Text key, Iterable<Text> values, Context context)
            throws IOException, InterruptedException {
        double sum1 = 0D;
        double sum2 = 0D;
        long count = 0L;

        for (Text value : values) {
            double[] partial = Avg2Reducer.parsePartial(value.toString());
            sum1 += partial[0];
            sum2 += partial[1];
            count += (long) partial[2];
        }

        if (count == 0L) {
            return;
        }
        outVal.set(sum1 + "," + sum2 + "," + count);
        context.write(key, outVal);
    }
}

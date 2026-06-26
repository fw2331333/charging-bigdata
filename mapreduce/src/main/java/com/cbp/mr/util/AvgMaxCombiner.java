package com.cbp.mr.util;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

import java.io.IOException;

/** Combiner：局部聚合单指标均值与最大值，中间格式 sum,count,max */
public class AvgMaxCombiner extends Reducer<Text, Text, Text, Text> {

    private final Text outVal = new Text();

    @Override
    protected void reduce(Text key, Iterable<Text> values, Context context)
            throws IOException, InterruptedException {
        double sum = 0D;
        double max = Double.NEGATIVE_INFINITY;
        long count = 0L;

        for (Text value : values) {
            double[] partial = AvgMaxReducer.parsePartial(value.toString());
            sum += partial[0];
            count += (long) partial[1];
            max = Math.max(max, partial[2]);
        }

        if (count == 0L) {
            return;
        }
        outVal.set(sum + "," + count + "," + max);
        context.write(key, outVal);
    }
}

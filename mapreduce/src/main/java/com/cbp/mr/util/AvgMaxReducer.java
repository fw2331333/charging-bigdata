package com.cbp.mr.util;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

import java.io.IOException;

/**
 * 单指标均值与最大值 Reducer。
 * Mapper 输出：current
 * Combiner 中间态：sum,count,max
 */
public class AvgMaxReducer extends Reducer<Text, Text, Text, Text> {

    private final Text outVal = new Text();

    @Override
    protected void reduce(Text key, Iterable<Text> values, Context context)
            throws IOException, InterruptedException {
        double sum = 0D;
        double max = Double.NEGATIVE_INFINITY;
        long count = 0L;

        for (Text value : values) {
            double[] partial = parsePartial(value.toString());
            sum += partial[0];
            count += (long) partial[1];
            max = Math.max(max, partial[2]);
        }

        if (count == 0L) {
            return;
        }
        outVal.set((sum / count) + "\t" + max);
        context.write(key, outVal);
    }

    public static double[] parsePartial(String raw) {
        String[] parts = raw.split(",");
        if (parts.length >= 3) {
            return new double[]{
                    RecordParser.parseDouble(parts[0], 0D),
                    RecordParser.parseDouble(parts[1], 0D),
                    RecordParser.parseDouble(parts[2], Double.NEGATIVE_INFINITY)
            };
        }
        double v = RecordParser.parseDouble(raw, 0D);
        return new double[]{v, 1D, v};
    }

    public static String metricValue(double current) {
        return String.valueOf(current);
    }
}

package com.cbp.mr.util;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

import java.io.IOException;

/**
 * 双指标均值 Reducer。
 * Mapper 输出：v1,v2
 * Combiner/Reducer 中间态：sum1,sum2,count
 * 最终输出：avg1 \t avg2
 */
public class Avg2Reducer extends Reducer<Text, Text, Text, Text> {

    private final Text outVal = new Text();

    @Override
    protected void reduce(Text key, Iterable<Text> values, Context context)
            throws IOException, InterruptedException {
        double sum1 = 0D;
        double sum2 = 0D;
        long count = 0L;

        for (Text value : values) {
            double[] partial = parsePartial(value.toString());
            sum1 += partial[0];
            sum2 += partial[1];
            count += (long) partial[2];
        }

        if (count == 0L) {
            return;
        }
        outVal.set((sum1 / count) + "\t" + (sum2 / count));
        context.write(key, outVal);
    }

    public static double[] parsePartial(String raw) {
        String[] parts = raw.split(",");
        if (parts.length >= 3) {
            return new double[]{
                    RecordParser.parseDouble(parts[0], 0D),
                    RecordParser.parseDouble(parts[1], 0D),
                    RecordParser.parseDouble(parts[2], 0D)
            };
        }
        if (parts.length == 2) {
            return new double[]{
                    RecordParser.parseDouble(parts[0], 0D),
                    RecordParser.parseDouble(parts[1], 0D),
                    1D
            };
        }
        return new double[]{0D, 0D, 0D};
    }

    public static String pairValue(double v1, double v2) {
        return v1 + "," + v2;
    }
}

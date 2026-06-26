package com.cbp.mr.util;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

import java.io.IOException;

/** Combiner：保留 max,min 逗号格式供下一阶段 Shuffle */
public class MaxMinCombiner extends Reducer<Text, Text, Text, Text> {

    private final Text outVal = new Text();

    @Override
    protected void reduce(Text key, Iterable<Text> values, Context context)
            throws IOException, InterruptedException {
        double maxFirst = Double.NEGATIVE_INFINITY;
        double minSecond = Double.POSITIVE_INFINITY;
        boolean found = false;

        for (Text value : values) {
            String[] parts = value.toString().split(",");
            if (parts.length < 2) {
                continue;
            }
            maxFirst = Math.max(maxFirst, RecordParser.parseDouble(parts[0], Double.NEGATIVE_INFINITY));
            minSecond = Math.min(minSecond, RecordParser.parseDouble(parts[1], Double.POSITIVE_INFINITY));
            found = true;
        }

        if (!found) {
            return;
        }
        outVal.set(maxFirst + "," + minSecond);
        context.write(key, outVal);
    }
}

package com.cbp.mr.util;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * 手册 §3.3.7：按电池状态统计最高/最低温度的平均值与方差。
 */
public class BatteryStatusStatsReducer extends Reducer<Text, Text, Text, Text> {

    private final Text outVal = new Text();

    @Override
    protected void reduce(Text key, Iterable<Text> values, Context context)
            throws IOException, InterruptedException {
        List<Double> maxTemps = new ArrayList<>();
        List<Double> minTemps = new ArrayList<>();
        for (Text value : values) {
            String[] parts = value.toString().split(",");
            if (parts.length < 2) {
                continue;
            }
            maxTemps.add(RecordParser.parseDouble(parts[0], 0D));
            minTemps.add(RecordParser.parseDouble(parts[1], 0D));
        }
        if (maxTemps.isEmpty()) {
            return;
        }

        double avgMax = average(maxTemps);
        double avgMin = average(minTemps);
        double varMax = variance(maxTemps, avgMax);
        double varMin = variance(minTemps, avgMin);

        outVal.set(avgMax + "\t" + avgMin + "\t" + varMax + "\t" + varMin);
        context.write(key, outVal);
    }

    private static double average(List<Double> values) {
        double sum = 0D;
        for (double v : values) {
            sum += v;
        }
        return sum / values.size();
    }

    private static double variance(List<Double> values, double mean) {
        if (values.size() <= 1) {
            return 0D;
        }
        double sumSq = 0D;
        for (double v : values) {
            double diff = v - mean;
            sumSq += diff * diff;
        }
        return sumSq / values.size();
    }
}

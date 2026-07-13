package com.cbp.mr.util;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

/**
 * 手册 §3.3.6：按小时键汇总，对时序记录计算组电压与充电电流变化率（%）。
 * 电压：相邻时刻变化率的算术平均；电流：对 |I| 计算变化率后再取平均（避免负号恒定值误判为 0）。
 */
public class VoltageCurrentChangeRateReducer extends Reducer<Text, Text, Text, Text> {

    private final Text outVal = new Text();

    @Override
    protected void reduce(Text key, Iterable<Text> values, Context context)
            throws IOException, InterruptedException {
        List<String[]> records = new ArrayList<>();
        for (Text value : values) {
            String[] parts = value.toString().split(",", 3);
            if (parts.length < 3) {
                continue;
            }
            records.add(parts);
        }
        if (records.isEmpty()) {
            return;
        }
        records.sort(Comparator.comparing(a -> a[0]));

        Double prevVoltage = null;
        Double prevCurrent = null;
        List<Double> voltageChanges = new ArrayList<>();
        List<Double> currentChanges = new ArrayList<>();

        for (String[] rec : records) {
            double voltage = RecordParser.parseDouble(rec[1], 0D);
            double current = RecordParser.parseDouble(rec[2], 0D);
            if (prevVoltage != null && prevVoltage != 0D) {
                voltageChanges.add((voltage - prevVoltage) / prevVoltage * 100D);
            }
            if (prevCurrent != null) {
                double absPrev = Math.abs(prevCurrent);
                double absCurrent = Math.abs(current);
                if (absPrev != 0D) {
                    currentChanges.add((absCurrent - absPrev) / absPrev * 100D);
                }
            }
            prevVoltage = voltage;
            prevCurrent = current;
        }

        double avgVoltageChange = average(voltageChanges);
        double avgCurrentChange = average(currentChanges);

        outVal.set(avgVoltageChange + "\t" + avgCurrentChange);
        context.write(key, outVal);
    }

    private static double average(List<Double> values) {
        if (values.isEmpty()) {
            return 0D;
        }
        double sum = 0D;
        for (double value : values) {
            sum += value;
        }
        return sum / values.size();
    }
}

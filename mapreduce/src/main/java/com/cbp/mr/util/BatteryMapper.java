package com.cbp.mr.util;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

import java.io.IOException;

/**
 * 电池数据 Mapper 基类：解析 dsv13r1 行，非法记录计入计数器后跳过。
 */
public abstract class BatteryMapper extends Mapper<Object, Text, Text, Text> {

    /** 计数器组名 */
    public static final String COUNTER_GROUP = "CBP";
    /** 坏记录计数器 */
    public static final String BAD_RECORD = "BAD_RECORD";

    private final Text outKey = new Text();
    private final Text outVal = new Text();

    protected Text createKey(String key) {
        outKey.set(key);
        return outKey;
    }

    protected Text createValue(String value) {
        outVal.set(value);
        return outVal;
    }

    @Override
    protected final void map(Object key, Text value, Context context) throws IOException, InterruptedException {
        String[] fields = RecordParser.parse(value);
        if (fields == null) {
            context.getCounter(COUNTER_GROUP, BAD_RECORD).increment(1L);
            return;
        }
        mapRecord(fields, context);
    }

    protected abstract void mapRecord(String[] fields, Context context) throws IOException, InterruptedException;
}

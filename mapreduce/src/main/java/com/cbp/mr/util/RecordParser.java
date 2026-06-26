package com.cbp.mr.util;

import org.apache.hadoop.io.Text;

/**
 * 解析 dsv13r1.csv 单行记录；字段不足或空行返回 null。
 */
public final class RecordParser {
    private RecordParser() {
    }

    public static String[] parse(Text value) {
        return parse(value.toString());
    }

    public static String[] parse(String line) {
        if (line == null) {
            return null;
        }
        String trimmed = line.trim();
        if (trimmed.isEmpty()) {
            return null;
        }
        String[] fields = trimmed.split(",", -1);
        if (fields.length < FieldIndex.MIN_FIELDS) {
            return null;
        }
        return fields;
    }

    public static double parseDouble(String raw, double defaultValue) {
        if (raw == null || raw.isEmpty()) {
            return defaultValue;
        }
        try {
            return Double.parseDouble(raw);
        } catch (NumberFormatException ex) {
            return defaultValue;
        }
    }
}

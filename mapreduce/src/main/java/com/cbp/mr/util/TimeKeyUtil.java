package com.cbp.mr.util;

/**
 * 时间键工具：record_time 格式为 yyyyMMddHHmmss（14 位）。
 */
public final class TimeKeyUtil {
    private TimeKeyUtil() {
    }

    /** 按小时聚合键：yyyyMMddHH */
    public static String toHourKey(String recordTime) {
        if (recordTime == null || recordTime.length() < 10) {
            return "unknown";
        }
        return recordTime.substring(0, 10);
    }

    /** 时间点键：yyyyMMddHHmmss */
    public static String toTimePointKey(String recordTime) {
        if (recordTime == null || recordTime.isEmpty()) {
            return "unknown";
        }
        return recordTime;
    }

    /** 手册 v6：日内小时键 HH（record_time 第 9~10 位） */
    public static String toHourOfDayKey(String recordTime) {
        if (recordTime == null || recordTime.length() < 10) {
            return "unknown";
        }
        return recordTime.substring(8, 10);
    }

    /** SOC 区间标签，如 10-20 */
    public static String toSocBucket(double soc) {
        int lower = ((int) Math.floor(soc / 10.0)) * 10;
        int upper = lower + 10;
        if (lower < 0) {
            lower = 0;
            upper = 10;
        }
        if (lower >= 100) {
            return "90-100";
        }
        return lower + "-" + upper;
    }
}

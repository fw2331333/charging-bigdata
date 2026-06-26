package com.cbp.mr.util;

/**
 * dsv13r1.csv 字段下标（无表头，数据由用户上传至 HDFS /Car/）。
 */
public final class FieldIndex {
    /** 记录 ID */
    public static final int ID = 0;
    /** 记录时间 yyyyMMddHHmmss */
    public static final int RECORD_TIME = 1;
    /** 荷电状态 SOC */
    public static final int SOC = 2;
    /** 电池包电压 */
    public static final int PACK_VOLTAGE = 3;
    /** 充电电流 */
    public static final int CHARGE_CURRENT = 4;
    /** 单体最高电压 */
    public static final int MAX_CELL_VOLTAGE = 5;
    /** 单体最低电压 */
    public static final int MIN_CELL_VOLTAGE = 6;
    /** 最高温度 */
    public static final int MAX_TEMPERATURE = 7;
    /** 最低温度 */
    public static final int MIN_TEMPERATURE = 8;
    /** 可用能量 */
    public static final int AVAILABLE_ENERGY = 9;
    /** 可用容量 */
    public static final int AVAILABLE_CAPACITY = 10;
    /** 最少字段数 */
    public static final int MIN_FIELDS = 11;

    private FieldIndex() {
    }
}

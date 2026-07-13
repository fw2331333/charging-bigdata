package com.cbp.mr.util;

/**
 * 手册 §3.3.7：按 SOC 划分电池状态。
 */
public final class BatteryStatusUtil {
    private BatteryStatusUtil() {
    }

    public static String fromSoc(double soc) {
        if (soc < 20D) {
            return "idle";
        }
        if (soc > 20D && soc < 50D) {
            return "charging";
        }
        return "discharging";
    }
}

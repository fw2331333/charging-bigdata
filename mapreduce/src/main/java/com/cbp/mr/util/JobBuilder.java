package com.cbp.mr.util;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

import java.io.IOException;

/**
 * MapReduce Job 构建工具：统一配置、绑定 HDFS 路径、运行前删除输出目录。
 */
public final class JobBuilder {
    private JobBuilder() {
    }

    public static Job createJob(Configuration conf, Class<?> driverClass, String jobName,
                                  Class<? extends Mapper> mapperClass,
                                  Class<? extends Reducer> reducerClass) throws IOException {
        Job job = Job.getInstance(conf, jobName);
        job.setJarByClass(driverClass);
        job.setMapperClass(mapperClass);
        job.setReducerClass(reducerClass);
        job.setMapOutputKeyClass(Text.class);
        job.setMapOutputValueClass(Text.class);
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);
        return job;
    }

    public static void bindIo(Job job, Configuration conf, String input, String output) throws IOException {
        deletePath(conf, output);
        FileInputFormat.addInputPath(job, new Path(input));
        FileOutputFormat.setOutputPath(job, new Path(output));
    }

    public static void setCombinerIfPresent(Job job, Class<? extends Reducer> combinerClass) {
        if (combinerClass != null) {
            job.setCombinerClass(combinerClass);
        }
    }

    public static void deletePath(Configuration conf, String hdfsPath) throws IOException {
        Path path = new Path(hdfsPath);
        FileSystem fs = path.getFileSystem(conf);
        if (fs.exists(path)) {
            fs.delete(path, true);
        }
    }
}

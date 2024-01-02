---
layout: post
title: "Configuring Apache Spark to oversubscribe the # of cpu cores"
categories: []
tags:
 - Azure
 - Databricks
 - Apache Spark
 - Big Data
---

Apache Spark by default allocates 1 executor per CPU available on the system, so a 16 core VM will have 16 executors available. This is a sane default setting, each Thread will have a full cpu core available. Azure Databricks follows this convention. 

However when your workload is not CPU-bound, but IO or memory bound it could make sense to change this. 

You can easily override the number of cores by setting `SPARK_WORKER_CORES` as env variable. So a `Standard_F16` can run 64 Spark tasks in parallel instead of just 16. 

Setting this in Databricks is very simple: 

1. Open the cluster configuration page
2. Select Advanced Options
3. Under `Environment Variables` add `SPARK_WORKER_CORES=64`

More information:
- [Apache Spark Standalone configuration](https://spark.apache.org/docs/latest/spark-standalone.html)

We are not done yet. Picking the correct over-committing core ratio requires carefully watching the CPU metrics, especially watch the CPU utilization before and after. 
---
title: Announcing EventHubs ReIngest
tags: 
 - azure
 - microsoft
 - eventhubs
 - spark
 - kappa architecture
excerpt: >
  When building a [Kappa Architecture](https://www.oreilly.com/ideas/questioning-the-lambda-architecture) replaying 
  historic events is an important property of the system. EventHub and IoTHub support [EventHub Capture](https://docs.microsoft.com/en-us/azure/event-hubs/event-hubs-capture-overview) a way to automatically 
  archive all incoming messages on [Azure Blob](https://azure.microsoft.com/services/storage/blobs/) 
  or [Azure Data Lake Store](https://azure.microsoft.com/services/data-lake-store/), this takes care of the archiving part.

  To replay those messages back onto an EventHub (preferably a different one!) I created 
  _[nathan-gs/eventhubs-reingest](https://github.com/nathan-gs/eventhubs-reingest)_, a Spark based application that 
  reads the Avro messages, sorts, repartitions (by random chance) and writes them as fast 
  as possible to EventHub. 

---

When building a [Kappa Architecture](https://www.oreilly.com/ideas/questioning-the-lambda-architecture) replaying 
historic events is an important property of the system. EventHub and IoTHub support [EventHub Capture](https://docs.microsoft.com/en-us/azure/event-hubs/event-hubs-capture-overview) a way to automatically 
archive all incoming messages on [Azure Blob](https://azure.microsoft.com/services/storage/blobs/) 
or [Azure Data Lake Store](https://azure.microsoft.com/services/data-lake-store/), this takes care of the archiving part.

To replay those messages back onto an EventHub (preferably a different one!) I created 
_[nathan-gs/eventhubs-reingest](https://github.com/nathan-gs/eventhubs-reingest)_, a Spark based application that 
reads the Avro messages, sorts, repartitions (by random chance) and writes them as fast 
as possible to EventHub. 

### Other sources

Not only [EventHub Capture Avro messages](https://docs.microsoft.com/en-us/azure/event-hubs/event-hubs-capture-overview#exploring-the-captured-files-and-working-with-avro) are supported, any Spark SQL or Hive datasource. Just specify a `query` as part of the configuration. Take a look at the 
[README](https://github.com/nathan-gs/eventhubs-reingest) for more information.


## Performance

On a:
* 3 worker node HDI cluster
* a target EventHub
  * 12 partitions
  * 12 throughput units
* 5.6gb of capture files, with some small and some large events:
  * 1,592 blobs
  * 5,616,207,929 bytes
  
We manage to process the data in `15 minutes`. 

#### Throughput in mb
{% include post_img img="nr_of_mb.png" alt="Incoming Megabytes"  %}
{% include post_img img="nr_of_mb_min.png" alt="Incoming Megabytes per Minute"  %}


#### Throughput in msg/s
{% include post_img img="nr_msgs.png" alt="Incoming Messages"  %}
{% include post_img img="nr_msgs_min.png" alt="Incoming Messages per Minute"  %}

#### Distribution of Spark taks
{% include post_img img="spark_summary.png" alt="Spark Task Distribution"  %}

Do notice that the task time is highly correlated with the input size.
{% include post_img img="spark_min_related_to_size.png" alt="Spark Task Distribution, related to size"  %}


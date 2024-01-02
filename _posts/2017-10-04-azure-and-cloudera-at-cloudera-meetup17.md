---
layout: post
title: "Cloudera, Azure and Big Data at Cloudera Meetup '17 "
categories: [presentations]
tags:
- Azure
- Big Data
- Apache Spark
---

[Big Industries](http://bigindustries.be) hosted an evening of [Cloudera in the Cloud](https://www.meetup.com/Belgium-Cloudera-User-Group/events/240605775/). 
I presented on "Cloudera, Azure and Big Data", showcasing how well Cloudera integrates with Azure data services, and how easy it is to deploy the full power of Cloudera's enterprise data hub, as well as using [Cloudera Altus on Azure](https://vision.cloudera.com/introducing-cloudera-altus-on-microsoft-azure/). 


{% include slideshare code='h1Fw1vmfv5uVlM' aspect_ratio='16:9' %}

### The Demo

Millions of events, published by a set of [Connected Vehicle simulators](https://github.com/kvaes/TasmanianTraders-IoT-ConnectedVehicle) running on [Azure Container Instances](https://azure.microsoft.com/en-us/services/container-instances/). The events flowed through EventHubs and are archived on [Azure Data Lake Store](https://azure.microsoft.com/en-us/services/data-lake-store/).
[Cloudera Enterprise Data Hub](https://azuremarketplace.microsoft.com/en-us/marketplace/apps/cloudera.clouderaedh) connects to the Data Lake and exposes them as Hive/Spark SQL tables. 
As final step a simple dashboard using [Power BI](https://powerbi.com) was created.


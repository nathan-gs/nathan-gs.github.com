---
layout: post
title: Predicting Occupancy on the Belgian railroads, based on spitsgids/iRail data, using Azure ML.
excerpt: >
    [Pieter Colpaert](https://twitter.com/pietercolpaert), the **#opendata** specialist in Belgium did a call to the community to try and predict which train will have high occupancy.
    <br/>
    I am not a Data Scientist, but decided to give it a try on [Azure Machine Learning](https://studio.azureml.net/), [my employer’s](https://microsoft.be/) Machine Learning offer in the Cloud. I used the free version to create this. Using Azure ML you can use the build in algorithms, or use Python or R scripts. We also have Jupyter notebooks available to quickly explore the data.

tags:
- Azure
- Machine Learning
- Big Data
- AI
---

*This post first appeared on [medium.com](https://medium.com/@nathan.gs/predicting-occupancy-on-the-belgian-railroads-based-on-spitsgids-irail-data-using-azure-ml-95aa89f22620).*

[Pieter Colpaert](https://twitter.com/pietercolpaert), the **#opendata** specialist in Belgium did a call to the community to try and predict which train will have high occupancy.

<blockquote class="twitter-tweet" data-lang="en"><p lang="en" dir="ltr">Any machine learning experts that want to help me to predict occupancy on Belgian trains? Ground truth available: <a href="https://t.co/5MWsmBkHkw">https://t.co/5MWsmBkHkw</a></p>&mdash; Pieter Colpaert (@pietercolpaert) <a href="https://twitter.com/pietercolpaert/status/792311571565387776?ref_src=twsrc%5Etfw">October 29, 2016</a></blockquote>
<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>


I am not a Data Scientist, but decided to give it a try on [Azure Machine Learning](https://studio.azureml.net/), [my employer’s](https://microsoft.be/) Machine Learning offer in the Cloud. I used the free version to create this. Using Azure ML you can use the build in algorithms, or use Python or R scripts. We also have Jupyter notebooks available to quickly explore the data.

## Reading & exploring the data

Pieter made available a [json dataset](https://gtfs.irail.be/nmbs/feedback/occupancy-until-20161029.newlinedelimitedjsonobjects), which contain following fields:
- querytype
- querytime
- user_agent
- post.connection
- post.from
- post.date
- post.vehicle
- post.occupancy
- post.to

#### Reading in the data

To read in the data I am going to use an simple R script, because it’s a json, that we also need to flatten. Just add [Execute R Script](https://msdn.microsoft.com/en-us/library/azure/dn905952.aspx) as the first block. The json is not a valid json, it’s [ndjson](http://ndjson.org/) so we need to use the stream_in method of jsonlite.

```r
library(jsonlite)
library(plyr)

con <- url("http://gtfs.irail.be/nmbs/feedback/occupancy-until-20161029.newlinedelimitedjsonobjects")
mydata <- flatten(jsonlite::stream_in(con), recursive=TRUE)
data.set = mydata

maml.mapOutputPort("data.set")
```

The data now looks like:

{% include post_img img="1.png"  %}

#### Converting querytime to DateTime

We are going to convert the querytime to a DateTime, using [Edit Metadata](https://msdn.microsoft.com/en-us/library/azure/dn905986.aspx), launch the column selector and select the *querytime* field, as field type select *DateTime*. No need to insert the *format*.

#### Extracting the hour, the quarter, the day of the week and making a readable label.

Using [Apply SQL Transformation](https://msdn.microsoft.com/en-us/library/azure/dn905914.aspx), which allows you to use the full SQLite syntax to do transformations, aggregations on your data. We use following script, unfortunately we need to do a [few tricks](http://stackoverflow.com/a/35060424) because there is no LPAD in SQLite.

```sql
select 
time(strftime('%H', ts) || ':' || substr((cast(strftime('%M', ts) / 15 as int) * 15) || '0', 1, 2)) as [time],
strftime('%w', ts) as [day_of_week],
substr([post.occupancy], 27) as [label],
 * 
from t1;
```

We are converting the DateTime to a Hour:Quarter combination, because we want to have more overlap. We also extract the day of week, because weekend vs non-weekend might have a big impact.

#### As last step we are going to extract only the fields we need

Using [Select Columns in Dataset](https://msdn.microsoft.com/en-us/library/azure/dn905883.aspx) we are going to extract the features + label (all fields) we think are relevant. 
I used the following: 
- post.from
- post.to
- time
- day_of_week
- label

#### Our data now looks like this

One of the advantages of using Azure ML is quickly looking at how the data looks like. Seeing the distributions inside an individual column, etc.

{% include post_img img="2.png"  %}

The flow of our operations, should now look similar to this:

{% include post_img img="3.png"  %}


## Training a classification model

We are going to try a multi-class classification model, to see where we get. Classification is supervised learning, so we first need to split our data in a training and test set.

#### Splitting the data in training and test
Using the [Split Data](https://msdn.microsoft.com/en-us/library/azure/dn905969.aspx) block, I’m going to divide the data in two parts 60% as training, and 40% as test set.

#### Add the model and test it

I first tried with a [Multiclass Decision Forest](https://msdn.microsoft.com/en-us/library/azure/dn906015.aspx), and I've left all the options to the defaults. Next step I added [Train Model](https://msdn.microsoft.com/en-us/library/azure/dn906044.aspx), as input I use the training set and the model, I also selected the *label* column as the label. We can visualize the trees that are constructed, by selecting *Visualize*.

{% include post_img img="4.png"  %}

#### Score the model

Now we are going to apply our model, using [Score Model](https://msdn.microsoft.com/en-us/library/azure/dn905995.aspx). Here we combine the *Trained Model*, with the *test dataset*. We can now see what’s Azure ML classifying:

{% include post_img img="5.png"  %}

#### As final step we are going to measure the performance of the model

Using [Evaluate Model](https://msdn.microsoft.com/en-us/library/azure/dn905915.aspx) we can quickly measure the performance of our models, and even compare multiple algorithms.

{% include post_img img="6.png"  %}

It doesn't look like we are able to accurately predict occupancy yet. Let’s see if we use a different algorithm we get better results.

#### Our flow looks now like this

{% include post_img img="7.png" alt="Azure ML flow"  %}

## Comparing Models and Algorithms

Let’s try using a second algorithm and see if we can get better results.

Copy the [Train Model](#add-the-model-and-test-it) and [Score Model](#score-the-model) steps.

#### Add a [Multi-class Neural Network](https://msdn.microsoft.com/en-us/library/azure/dn906030.aspx) (or another one)

Connect the algorithm to the second *Train Model* block, that’s it.

#### Connect the second *Score Model* to *Evaluate Model*. 

We can now quickly compare the accuracies of both models.

{% include post_img img="8.png" alt="Azure ML model comparisons"  %}

## Our pipeline now looks as follows

{% include post_img img="9.png" alt="Azure ML pipeline"  %}

## Bonus: a REST api

Create a [Prediction Web Service](https://azure.microsoft.com/en-us/documentation/articles/machine-learning-walkthrough-5-publish-web-service/), to quickly create a REST interface that takes in a single record and outputs the classified value.

#### Select the Train Model model, you want to use

Select the *Train Model* block you want to use, and click on *SET UP WEB SERVICE*.

#### A second tab is created, called **Predictive Experiment**

Add a *Web service input*, and connect it to the first *Edit Metadata* block. 
Add a *Web service output* to the *Score Model* block.

{% include post_img img="10.png" alt="Azure ML REST service"  %}

**You now have a web service.**

## Conclusion

Although the model performance is quite low, I hope I have showed you how easy it is to get started with [Azure ML](https://studio.azureml.net). 
We can improve this model in a few ways:
- By Increasing the amount of data
    - <http://graph.spitsgids.be/connections/?departureTime=2016-10-29T20%3A20>
    - <https://api.irail.be/logs>
- As well as the variety of the data
    - weather 
        - <http://opendata.meteo.be/>
        - <https://openweathermap.org/>
    - events
        - <http://www.uitdatabank.be/2/Home/IndexTemp>
    
Do let me know if you improve the performance, and how. I might do a follow up myself.

#### Update

* I just saw that [@Gillesvdwiele](https://twitter.com/Gillesvdwiele) [blogged on it](https://medium.com/@gillesvandewiele/very-nice-read-nathan-51b4f3b8dfba) as well. He added _weather_ and _vehicle_ type and reached better results.
* [@peeterskris](https://twitter.com/peeterskris) from [dataminded.be](https://dataminded.be) also created a [blog post](https://dataminded.be/blog/predicting-occupancy-nmbs-trains).
* Apperantly even a [kaggle competition](https://www.kaggle.com/c/train-occupancy-prediction/discussion/27549) exists.



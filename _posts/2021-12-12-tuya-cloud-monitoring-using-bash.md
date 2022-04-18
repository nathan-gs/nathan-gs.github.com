---
layout: post
title: "Tuya Cloud: monitoring using bash"
categories: []
tags:
 - Tuya
 - IoT
 - NixOs
---

Connecting to the [Tuya Cloud](https://iot.tuya.com/), to monitor a set of home IoT devices. Recently I bought a set of Silvercrest/Lidl Homesmart devices. 

Tuya provides a REST API, however there are definitely some quirks when authenticating and signing the request. So I created some `bash` functions at [nathan-gs/tuya-cloud-bash](https://github.com/nathan-gs/tuya-cloud-bash). 

Usage is very much simplified.  
```bash
TUYA_CLIENT_ID=""
TUYA_SECRET=""
TUYA_BASE_URL="https://openapi.tuyaeu.com"

source tuya.sh

TUYA_ACCESS_TOKEN=$(tuya_get_token $TUYA_CLIENT_ID $TUYA_SECRET "$TUYA_BASE_URL")
tuya $TUYA_CLIENT_ID $TUYA_SECRET "$TUYA_BASE_URL" $TUYA_ACCESS_TOKEN get '/v1.0/iot-01/associated-users/devices?last_row_key='
```

Looking at the [signing part](https://github.com/nathan-gs/tuya-cloud-bash/blob/main/tuya.sh#L26-L32), we see we need to create a new string:
```
$TUYA_CLIENT_ID # client ID
$TUYA_ACCESS_TOKEN # Access Token
Timestamp # Timestamp in Milliseconds
GET # Method in uppercase
hash(body) # Hash of the body
hash(headers) # Hash of special headers
path # Url path parth
```

which can be signed using:
```bash
echo -ne "$signatureToSign" | openssl dgst -sha256 -hmac "$secret" | awk '{print $2}'
```

I also added a small Tuya Cloud Prometheus text exporter: [nathan-gs/tuya-cloud-bash/tuya_prometheus_exporter.sh](https://github.com/nathan-gs/tuya-cloud-bash/blob/main/tuya_prometheus_exporter.sh), which can be used to automatically collect all numeric metrics.
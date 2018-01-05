---
layout: post
title: 'Passing a PHP session between subdomains'
categories: 
excerpt: >
    Sometimes you need to have access to the same session between multiple subdomains. Eg. a user logs in at the main website, but should also have access to the forums subdomain. Ideally you implement a check from the subdomain to the main domain, but this isn’t always possible.  However, sharing a session between multiple domains is not possible.
tags: [php]
---

Sometimes you need to have access to the same session between multiple subdomains. Eg. a user logs in at the main website, but should also have access to the forums subdomain. Ideally you implement a check from the subdomain to the main domain, but this isn’t always possible.  However, sharing a session between multiple domains is not possible.

It’s possible to set a cookie domain for your sessions. Instead of the default of _www.example.org_ cookie domain set it to _.example.org_.

You can set the cookie domain, using [session_set_cookie_params](http://php.net/manual/en/function.session-set-cookie-params.php). It needs to happen before the _session_start()_.

eg. Put this at the top of your php pages that need to have shared sessions.
{% highlight php linenos %}
session_set_cookie_params ( 
    time() + 3600,      // $lifetime
    '/',                // $path 
    '.example.org'
);

{% endhighlight %}


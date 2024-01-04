---
title: "Tags in Jekyll: a Word Cloud"
tags: 
 - Web Development
 - Jekyll
---

On my Jekyll based blog I want to add Word Cloud on the [tags page](/tags/). A word cloud, with the size of the words based on the number of times the tag was used in a post. I used a similar approach in my [CV](/cv/#skills). A word cloud can add value to your tags page by making it more attractive, interactive, and informative. 

> This is the second post in a series on _Tags in Jekyll_, check [Tags in Jekyll: the Setup](/2024/01/03/tags-in-jekyll/) and [Tags in Jekyll: related posts](/2024/01/05/tags-in-jekyll-related-posts/).

### Setting up jQcloud

Making use of a of [jQCloud](https://github.com/lucaong/jQCloud) and the latest `jQuery` (I'm using these because of the implementation I already done on my CV page).

Just add the following to your page.

```html
<script src="//cdnjs.cloudflare.com/ajax/libs/jquery/3.7.1/jquery.min.js" integrity="sha512-v2CJ7UaYy4JwqLDIrZUI/4hqeoQieOmAZNXBeQyjo21dadnwR+8ZaIJVT8EE2iyI61OV8e6M8PP2/4hpQINQ/g==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
<script src="//cdnjs.cloudflare.com/ajax/libs/jqcloud/1.0.4/jqcloud.min.js" integrity="sha512-kKFIFIYZ70cs9AxqGnLqwhm1t0DI3vwiIGGe2r0zulHVgpDYvW3QZuIqsFzgbqmEsq1no2YCBJ7O99t8kmVu2A==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>

<div class="wordcloud" style="height: 400px; width: 90%"></div>
```

### Calculating the weights per tag and adding it

{% raw %}
```liquid
{% for tag in site.tags %}
$(document).ready(function () {
    
    var tags = [];
    {% for tag in site.tags %}
        {% assign tag_slug = tag[0] | sluggify %}                    
        {% assign weight = site.tags[tag_slug] | size %}
        {% assign title = tag[0] %}
        tags.push({
            text: "{{ title }}",
            weight: '{{ weight }}',
            link: '{% include tag_url tag=title %}'
        });
    {% endfor %}


    $('.wordcloud').jQCloud(tags, {
        'shape': 'rectangular'
    });    
});
{% endfor %}
```
{% endraw %}

> __7__:        Based on the tag and tag_slug from __6__, we can quite easily find the corresponding size. <br>
> __8__:        the title is just the first item of the `tag` <br>
> __12__:       Making use of the `tag_url` include, we created in the [Tags in Jekyll: the setup](/2024/01/03/tags-in-jekyll/) post.
>
> __17-19__:    We add the newly created array to the jQCloud function.

I created a new `tags.html` file, for instructions related to [css](https://github.com/lucaong/jQCloud#custom-css-guidelines) follow the docs.

### Conclusion

It's fairly easy to add a word cloud based on your tags, taking into account the weights. 

{% include post_img img="wordcloud.png" alt="A word cloud listening the tags of this website" %}
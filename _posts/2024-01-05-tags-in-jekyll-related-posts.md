---
title: "Tags in Jekyll: related posts"
tags: 
 - Web Development
 - Jekyll
---

Related posts are a great way to increase the engagement and retention of your blog readers. They help you showcase your other relevant and valuable content that might otherwise be overlooked or forgotten. They also improve the navigation and user experience of your blog, as they provide easy and intuitive links to explore more topics of interest. Moreover, related posts can boost your SEO and traffic, as they create more internal links and keywords for your site, and reduce the bounce rate and increase the dwell time of your visitors. In this post, I will show you how to add related posts to your Jekyll blog based on the tag functionality. 

> This is the third post in a series on _Tags in Jekyll_, check [Tags in Jekyll: the Setup](/2024/01/03/tags-in-jekyll/) and [Tags in Jekyll: a Word Cloud](/2024/01/04/tags-in-jekyll-wordcloud/).

### The code and implementation

We are assuming more common tags is a closer match to the content, so we want to sort this higher. We are looping multiple times over the posts and checking it. Unfortunately it does add a bit of calculations, so generating your content will be slower (but only during generation, not during browsing). I created an include `_includes/post_related.html`:

{%raw%}
```liquid
{% assign page = include.page %}
{% assign tags_match_min = include.tags_match_min | default: 3 %}
{% assign related_post_count = 1 %}
{% assign related_posts = "" | split: "|" %}
{% assign max_posts = include.max_posts | default: 6 %}
<ul class="post-list">
{% for min_tags in (1..tags_match_min) reversed %}    
    {% for post in site.posts %}
        {% if related_post_count <= max_posts and post.url != page.url %}
            {%- comment %}# Calculate related_tags {% endcomment %}
            {% assign related_tags = 0 %}
            {% for tag in page.tags %}
                {% if post.tags contains tag %}
                    {% assign related_tags = related_tags | plus: 1 %}
                {% endif %}
            {% endfor %}
            
            {% if related_tags >= min_tags %}
                {% unless related_posts contains post.url %}
                    {%- assign related_post_count = related_post_count | plus: 1 -%}
                    {%- assign url_arr = post.url | split: "|" -%}
                    {%- assign related_posts = related_posts | concat: url_arr %}
                    
                    <li>
                        <span class="post-meta">
                            {{ post.date }}
                            {%- if post.tags -%}
                                <span class="tags">
                                    {% for tag in post.tags %}            
                                        {{ tag }}
                                    {% endfor %}
                                </span>
                            {%- endif -%}
                        </span>
                    
                        <p>
                            <a href="{{ post.url | relative_url }}">
                                {{ post.title | escape }}
                            </a>
                        </p>
                    </li>
                {% endunless %}
            {% endif %}
        {% endif %}   
    {% endfor %}     
{% endfor %}
</ul>
```
{%endraw%}

A big challenge is dealing with the limitations of `liquid`, like not being able to directly create a new `array` (you need to use `split`). 

On my `post.html` template I include it like this:

{%raw%}
```liquid
<footer class="post-footer post-related">
    <h2>Related posts</h2>
    {% include related_posts.html page=page %}
</footer>
``` 
{%endraw%}

### Alternatives

There is a plugin [jsware/jekyll-related-posts](https://github.com/jsware/jekyll-related-posts) available who implements post relationship slightly differently. And of course after finishing the implmentation (& blog post) you spot a similar way by [webjeda.com](https://blog.webjeda.com/jekyll-related-posts/).

### Conclusion

In conclusion, related posts are a useful feature to have on your Jekyll blog, as they can help you increase the engagement and retention of your blog readers. By showing them other relevant and valuable content, you can improve the navigation and user experience of your blog, as well as your SEO and traffic. 

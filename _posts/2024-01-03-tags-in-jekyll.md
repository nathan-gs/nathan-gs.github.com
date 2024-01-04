---
title: "Tags in Jekyll: the setup"
tags: 
 - Web Development
 - Jekyll
last_modified_at: "2024-01-04"
---

Jekyll has support for [tags and categories](https://jekyllrb.com/docs/posts/#tags-and-categories), however using the Tag functionality comes with certain gotcha's if you want to maintain Github Pages compatibility. 

The goals are

- smoother discovery of related content
- a visual overview of top tags
- The ability to add some extra content to my tags pages.

This is the first post in a series on Tags in Jekyll, check [Tags in Jekyll: Word Cloud](/2024/01/04/tags-in-jekyll-wordcloud/). 


### Defining Tags

At the top of your `posts` page, you can definte them. The tags for this post are defined in the front matter:

{% raw %}
```yaml
---
layout: post
title: "Tags in Jekyll: the setup"
tags: 
 - Web Development
 - Jekyll
---

```
{% endraw %}

### Creating Tag pages

There are 2 main approaches, one using the [pattex/jekyll-tagging](https://github.com/pattex/jekyll-tagging) plugin. The other one using a [collections](https://www.siteleaf.com/blog/tag-pages-in-jekyll-and-siteleaf/#the-collection-approach). I recommend on reading [Jekyll Collections](https://ben.balter.com/2015/02/20/jekyll-collections/). The second approach has the advantage of being Jekyll native. 

In `_config.yml` create a new collection `post_tags` and some defaults, and a corresponding `_post_tags` folder. 

```yaml
collections:
  post_tags:
    permalink: /tags/:name/
    output: true

defaults:
  - scope:
      path: ''
      type: post_tags
    values:
      permalink: "/tags/:name/"
      layout: tag
```

The disadvantage of this model, is having to create a file for each tag in the `_post_tags` folder. To know which ones are missing I have this small `_site_tags_missing.txt` file I generate. It will loop over all the found `site.tags` and see if there is a `post_tag` with the corresponding `title` (which also means my tag name can be different then the url).

#### Content for a tag page

{% raw %}
```liquid
---
permalink: /_site_tags_missing.txt
---
{% if jekyll.environment != 'production' %}
{%- assign post_tags = site.post_tags | map: "title" -%}
{%- for tag in site.tags -%}
    {%- if post_tags contains tag[0] -%}
    {% else %}
{{ tag[0] }}
    {%- endif -%}
{%- endfor -%}
{% endif %}    
```
{% endraw %}

Inside the `_post_tags` folder I have a series of files, one for each `tag`. The filename will become the `/tags/FILENAME` url, and the `title` attribute the name. This allows the `#Web Development` tag to become `/tags/webdev/`. Any content is rendered on the tag page. 

{% raw %}
```liquid
---
title: Home Assistant
---
[Home Assistant](https://www.home-assistant.io/) is a versatile and open source platform that lets you control your home devices and services. It works great with [#Zigbee]({% include tag_url tag="Zigbee" %}) on [#NixOS]({% include tag_url tag="NixOS" %}).
```
{% endraw %}

#### A layout for the tag pages

Let's start styling the layout of the individual tag page. I want to give an overview of all the posts tagged.  I created a custom `tag.html` layout in the `_layouts` folder.

{% raw %}
```html
---
layout: base
---
<article class="post">
    <header class="post-header">
        <h1 class="post-title">{{ page.title | escape }}</h1>
    </header>

    <div class="post-content">
        {{ content }}
        {% assign tag = page.title | sluggify %}
        {% assign tag_posts = site.tags[tag] %}
        <ul class="post-list">
            {% for post in tag_posts %}
            <li>
                {% assign date_format = site.minima.date_format | default: "%b %-d, %Y" %}
                <span class="post-meta">
                    {{ post.date | date: date_format }}
                    {%- if post.tags -%}
                    <span class="tags">
                        {% for tag in post.tags %}            
                            {% if tag == page.title %}
                            {% else %}
                            <a href="{% include tag_url tag=tag %}">#{{ tag }}</a> 
                            {% endif %}
                        {% endfor %}
                      </span>
                    {%- endif -%}
                </span>

                <h4>
                    <a href="{{ post.url | relative_url }}">{{ post.title | escape }}</a>
                </h4>
            </li>
            {% endfor %}
        </ul>

        Browse more <a href="/tags">tags</a>.


    </div>
</article>
```
{% endraw %}

An example of this can be viewed at [/tags/ai](/tags/ai). In the posts overview I also want to highlight the other tags for the particular post, this is accomplished line `22-26`. I'm using a little helper include, `_includes/tag_url` to make sure I link to an existing `post_tag` (and fallback to `/tags` if not).

{% raw %}
```liquid
{%- capture url -%}
    {% for pt in site.post_tags %}
        {% if pt.title == include.tag %}
            {{ pt.url | relative_url }}
        {% endif %}
    {% endfor %}
{%- endcapture -%}
{{ url | strip | default: "/tags/" | relative_url}}
```
{% endraw %}

### Linking to the tags

Before (or after) the title, as part of the `post-meta` I added following code.

{%raw%}
```liquid
{% assign date_format = site.minima.date_format | default: "%b %-d, %Y" %}
<span class="post-meta">
  <span class="date">{{ post.date | date: date_format }}</span>
  {%- if post.tags -%}
  <span class="tags">
    {% for tag in post.tags %}            
      <a href="{% include tag_url tag=tag %}">#{{ tag }}</a>
    {% endfor %}
    </span>
  {%- endif -%}
</span>
```
{%endraw%}

## Conclusion

Having a pure Jekyll & liquid version is possible, but takes some efforts and head scratching. Especially how liquid filters work. I recommend you to read the [Liquid Docs](https://shopify.github.io/liquid/) before starting. This blog is fully on [GitHub](https://github.com/nathan-gs/nathan-gs.github.com), so take a peak. 
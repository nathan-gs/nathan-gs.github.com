---
title: "Making SlideShare iframes responsive, using CSS"
---

While reviving my blog I wanted a way to embed my [presentations]({% link presentations.html %}), by default the SlideShare embed code uses a fixed width and height.

eg. 
{% highlight html linenos %}
<iframe src="//www.slideshare.net/slideshow/embed_code/key/h1Fw1vmfv5uVlM" 
    width="595" 
    height="485" 
    frameborder="0" 
    marginwidth="0" 
    marginheight="0" 
    scrolling="no" 
    style="border:1px solid #CCC; border-width:1px; margin-bottom:5px; max-width: 100%;" 
    allowfullscreen> 
</iframe> 
{% endhighlight %}

Unfortunately using a fixed `width` and `height` does not work well on a responsive website. Luckily I found [a solution for Youtube videos](https://stackoverflow.com/a/17465040), using pure css.

With some CSS it's very easy to make slideshare embeds that scale the height in relation to the actual width.

You need to add an outer `<div>`, with `0 height`, and `100% width`, and a `padding-bottom` as percentage of the aspect ratio (eg <em>9 / 16 = 56.25%</em>) with an extra padding of `38px` for the slide navigation.

#### The embed code now looks like this

{% highlight html linenos %}
<div class="iframe-slideshare-16x9">    
    <iframe src="//www.slideshare.net/slideshow/embed_code/key/h1Fw1vmfv5uVlM" 
        frameborder="0" 
        marginwidth="0" 
        marginheight="0" 
        scrolling="no" 
        allowfullscreen> 
    </iframe>
</div>
{% endhighlight %}

#### The CSS looks like this

{% highlight css linenos %}
.iframe-slideshare-4x3 {
    padding-bottom: calc(75% + 38px);
}

.iframe-slideshare-16x9 {
    padding-bottom: calc(56.25% + 38px);
}

.iframe-slideshare-16x9,
.iframe-slideshare-4x3,
{
    position: relative;
    width: 100%;
    height: 0;
}

.iframe-slideshare-16x9 iframe,
.iframe-slideshare-4x3 iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border:1px solid #CCC; 
}

{% endhighlight %} 

I added two variations because I have slides in `16:9` and `4:3` aspect ratio's.

#### The end result

{% include slideshare code='h1Fw1vmfv5uVlM' aspect_ratio='16:9' %}

### Browser Support

The CSS `calc()` function is according to [w3schools](https://www.w3schools.com/cssref/func_calc.asp) supported since:

|<i class="fab fa-chrome fa-fw"> </i> Chrome | <i class="fab fa-edge fa-fw"> </i> Edge | <i class="fab fa-internet-explorer fa-fw"> </i> IE | <i class="fab fa-firefox fa-fw"> </i> Firefox | <i class="fab fa-safari fa-fw"> </i> Safari | <i class="fab fa-opera fa-fw"> </i> Opera |
|-----:|----:|----:|-----:|----:|-----:|
| 26.0 | all | 9.0 | 16.0 | 7.0 | 15.0 |
| -webkit 19.0 |  |  | -moz 4.0 | -webkit 6.0 | | 

## Conclusion

Using plain CSS it is very easy to make responsive iframes that keep the aspect ratio, on mobile, tablet and desktop.

## Update 12/12/2021

Slideshare changed their layout, so instead of a `38px` extra margin, use `58px`. 
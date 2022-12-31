---
layout: post
title: "Single Page Website: changing the location hash based on the position in the page"
categories: 
tags:
 - Javascript
 - Website
---

While switching from **Google Analytics** to [PiWik](https://piwik.pro/) I wanted to improve tracking of my [cv](/cv) page, a _single page website_ or _single page application_. I want to switch the `#` hash of the `url` while scrolling through the page. 

Within the page, I have several sections with anchors usign `<a name="">`, eg: `<section><h2><a name="experience"></a>Experience</h2> ... </section>`. 

Let's take a look at the code:

{% highlight javascript linenos %}
{% raw %}
window.addEventListener('load', () => {
    const headings = document.querySelectorAll('section h2 a[name]');

    document.addEventListener('scroll', (e) => {
        headings.forEach(ha => {
            const rect = ha.getBoundingClientRect();
            if(rect.top > 0 && rect.top < 450) {                    
                const location = window.location.toString().split('#')[0];
                const oldHash = window.location.hash;
                hash = '#' + ha.name;
                if (ha.name == "introduction") {
                    hash = "";
                } 
                if (hash != oldHash) {
                    history.replaceState(null, null, location + hash);
                }
            }
        });
    });
});
{% endraw %}
{% endhighlight %}

This code listens for the `load` event on the window object, which is fired when the whole page has finished loading. When the event is fired, the code selects all the `a[name]` elements that are children of h2 elements that are children of section elements on the page. These `a[name]` elements will be used as the anchor links for our smooth scrolling.

Next, the code sets up a `scroll` event listener on the document object, which is fired whenever the user scrolls the page. When the event is fired, the code iterates over each of the `a[name]` elements that were selected earlier and gets the bounding client rectangle for each element. The bounding client rectangle is an object that represents the size and position of an element relative to the viewport.

If the top of the bounding client rectangle is greater than `0` and less than `450`, the code updates the URL hash to match the name attribute of the current `a[name]` element. The hash is the part of the URL that comes after the `#` symbol. 

If the name attribute is `"introduction"`, we are at the top, so let's set an empty hash. 

Finally, the code replaces the current entry in the browser's history with the updated URL, using the `replaceState` method of the `history` object. This updates the URL in the address bar without creating a new entry in the history.

PiWik automatically detects these hash changes and tracks these as seperate page views, more at [How to track a single-page application (SPA) from PiWik](https://help.piwik.pro/support/collecting-data/how-to-track-a-single-page-application/).


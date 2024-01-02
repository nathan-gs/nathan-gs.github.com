---
layout: post
title: "Single Page Website: changing the url hash based on the position in the page"
categories: 
tags:
 - Web Development
redirect_from:
  - /2022/12/31/single-page-website-changing-location-hash-based-on-position-in-page
---

While switching from **Google Analytics** to [PiWik](https://piwik.pro/) I wanted to improve tracking of my [cv](/cv) page, a _single page website_ or _single page application_. I want to switch the `#` hash of the `url` while scrolling through the page. I was inspired by [How To Update URL Hash On Scroll (With Table Of Contents) on Stackoverflow](https://stackoverflow.com/questions/58127310/how-to-update-url-hash-on-scroll-with-table-of-contents) and by [ChatGPT](https://chat.openai.com) suggesting the [Intersection Observer API](https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API) api.

Within the page, I have several sections with anchors using `<a name="">`, eg: `<section><a name="experience"></a><h2>Experience</h2> ... </section>`. 

We will implement smooth scrolling anchor links using the _Intersection Observer API_.

```javascript
window.addEventListener('load', () => {
    const headings = document.querySelectorAll('section > a[name]');

    const ioOptions = {
        threshold: 0.85
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const location = window.location.toString().split('#')[0];
                const oldHash = window.location.hash;

                aEntry = entry.target.querySelector('a[name]');
                hash = '#' + aEntry.name;
                if (aEntry.name == "introduction") {
                    hash = "";
                } 
                if (hash != oldHash) {
                    history.replaceState(null, null, location + hash);
                }
            }
        });
    }, ioOptions);

    headings.forEach(ha => {
        observer.observe(ha.parentElement);
    });
});
```

This code listens for the `load` event on the window object, which is fired when the whole page has finished loading. When the event is fired, the code selects all the `a[name]` elements that are immediate children of section elements. These `a[name]` elements will be used as the anchor links for our smooth scrolling.

Next, the code creates an `options` object with a `threshold` property, which specifies the percentage of the element's size that must be in view before the `IntersectionObserver` callback is triggered. In this case, the callback will be triggered when the element is at least 75% in view.

The code then creates a new `IntersectionObserver` instance, passing in a callback function and the options object as arguments. The callback function is executed whenever an element being observed by the observer enters or leaves the viewport.

The code then iterates over each of the `a[name]` elements that were selected earlier and calls the `observe` method on the `IntersectionObserver` instance, passing in each element as an argument. This tells the observer to start watching the element for intersection events.

When an element is intersecting the viewport, the `IntersectionObserver` callback is triggered and the code selects the first `a[name]` element within the `entry.target` element using the `querySelector` method. The code then updates the URL hash to match the name attribute of the `a[name]` element. The hash is the part of the URL that comes after the `#` symbol. If the name attribute is `"introduction"`, the code sets the hash to an empty string instead (because we are at the top of the page).

Finally, the code replaces the current entry in the browser's history with the updated URL, using the `replaceState` method of the `history` object. This updates the URL in the address bar without creating a new entry in the history.

PiWik automatically detects these hash changes and tracks these as separate page views, more at [How to track a single-page application (SPA) from PiWik](https://help.piwik.pro/support/collecting-data/how-to-track-a-single-page-application/).


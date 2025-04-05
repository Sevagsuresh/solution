from django import template

register = template.Library()

@register.filter
def youtube_embed(url):
    if 'watch?v=' in url:
        return url.replace('watch?v=', 'embed/')
    if 'youtu.be/' in url:  # Handle shortened URLs
        return url.replace('youtu.be/', 'youtube.com/embed/')
    return url
from django import template

register = template.Library()

@register.inclusion_tag('blog-tags/header.html', takes_context=True)
def header(context):
	return {'header_title': context['title']}


@register.inclusion_tag('blog-tags/single-post.html')
def single_post(post):
	return {'post': post}
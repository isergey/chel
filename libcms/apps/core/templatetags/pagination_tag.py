# -*- coding: utf-8 -*-

from django import template

register = template.Library()

def base_pagination(context, page, begin_pages=2, end_pages=2, before_current_pages=5, after_current_pages=5):
    # Digg-like pages
    before = max(page.number - before_current_pages - 1, 0)
    after = page.number + after_current_pages
    begin = list(list(page.paginator.page_range)[:begin_pages])
    middle = list(list(page.paginator.page_range)[before:after])
    end = list(list(page.paginator.page_range)[-end_pages:])
    last_page_number = end[-1]

    def collides(firstlist, secondlist):
        """ Returns true if lists collides (have same entries)

        >>> collides([1,2,3,4],[3,4,5,6,7])
        True
        >>> collides([1,2,3,4],[5,6,7])
        False
        """
        return any(item in secondlist for item in firstlist)

    # If middle and end has same entries, then end is what we want
    if collides(middle, end):
        end = list(range(max(last_page_number - before_current_pages - after_current_pages, 1), last_page_number+1))
        middle = []

    # If begin and middle ranges has same entries, then begin is what we want
    if collides(begin, middle):
        begin = list(range(1, min(before_current_pages + after_current_pages, last_page_number)+1))
        middle = []

    # If begin and end has same entries then begin is what we want
    if collides(begin, end):
        begin = list(range(1, last_page_number+1))
        end = []

    return {'page' : page,
            'begin' : begin,
            'middle' : middle,
            'end' : end,
            'request':context['request']}

@register.inclusion_tag('pagination/pagination_tag.html', takes_context=True)
def pagination(context, page, begin_pages=2, end_pages=2, before_current_pages=5, after_current_pages=5):
    return base_pagination(context, page, begin_pages=1, end_pages=1, before_current_pages=2, after_current_pages=3)

@register.inclusion_tag('pagination/admin_pagination_tag.html', takes_context=True)
def admin_pagination(context, page, begin_pages=2, end_pages=2, before_current_pages=3, after_current_pages=3):
    return base_pagination(context, page, begin_pages, end_pages, before_current_pages, after_current_pages)
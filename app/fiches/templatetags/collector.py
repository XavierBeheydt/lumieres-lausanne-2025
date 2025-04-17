# -*- coding: utf-8 -*-
#
#    Copyright (C) 2010-2012 Université de Lausanne, RISET
#    < http://www.unil.ch/riset/ >
#
#    This file is part of Lumières.Lausanne.
#    Lumières.Lausanne is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Lumières.Lausanne is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    This copyright notice MUST APPEAR in all copies of the file.
#
from django import template
from django.template import TemplateSyntaxError
from django.db import models

from django.contrib.auth.models import User, AnonymousUser
#from django.template.loader import get_template, render_to_string
#from urlparse import urlparse
#from django.core.urlresolvers import resolve, Resolver404
#from django.utils.encoding import smart_str, force_unicode
#from django.utils.dateformat import format
#from django.utils.html import urlize
#from django.utils.safestring import mark_safe
#from django.conf import settings
#
#import datetime, re, time

register = template.Library()


# @register.filter
# def editable_projects(user):
#     """
#     Return the list of the projects the user can edit
#     """
#     from django.contrib.auth.models import User, AnonymousUser
#     if not isinstance(user, User) and not isinstance(user, AnonymousUser):
#         raise template.TemplateSyntaxError("argument should be a User")
    
#     projs = set()
#     #for g in user.get_profile().get_usergroups():
#     for g in user.profile.get_usergroups():
#         projs |= set(g.group_projects.all())
#     return set(user.member_projects.all()) | set(user.project_set.all()) | projs


@register.filter
def editable_projects(user):
    """
    Return the list of the projects the user can edit
    """
    if not isinstance(user, (User, AnonymousUser)):
        raise template.TemplateSyntaxError("argument should be a User")
    
    if isinstance(user, AnonymousUser) or not hasattr(user, 'profile'):
        return set()
    
    projs = set()
    for g in user.profile.get_usergroups():
        projs |= set(g.group_projects.all())
    
    return set(user.member_projects.all()) | set(user.project_set.all()) | projs
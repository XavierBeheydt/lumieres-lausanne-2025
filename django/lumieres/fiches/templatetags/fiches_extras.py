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
from django.template.loader import get_template
from django.template import TemplateSyntaxError
import urllib.parse as urlparse
#from django.core.urlresolvers import resolve, Resolver404
from django.urls import resolve, Resolver404
from django.utils.encoding import smart_str, force_str
from django.utils.dateformat import format
from django.utils.html import urlize
from django.utils.safestring import mark_safe
#from django.conf import settings

from django.contrib.auth.models import User, AnonymousUser
from fiches.models import UserGroup

import re, time
register=template.Library()

# http://www.djangosnippets.org/snippets/847/
@register.filter
def in_group2(user, groups):
    """Returns a boolean if the user is in the given group, or comma-separated
    list of groups.

    Usage::

        {% if user|in_group:"Friends" %}
        ...
        {% endif %}

    or::

        {% if user|in_group:"Friends,Enemies" %}
        ...
        {% endif %}

    """
    group_list = force_str(groups).split(',')
    return bool(user.groups.filter(name__in=group_list).values('name'))

@register.filter
def startswith(string, needle):
    try:
        return string.startswith(needle)
    except:
        return ""

@register.filter
def decodeHtmlEntities(string):
    entity_re = re.compile("&(#?)(\d{1,5}|\w{1,8});")
    
    def substitute_entity(match):
        #from htmlentitydefs import name2codepoint as n2cp
        from html.entities import name2codepoint
        ent = match.group(2)
        if match.group(1) == "#":
            #return unichr(int(ent))
            try:
                return chr(int(ent))
            except ValueError:
                return match.group()
        else:
            #cp = n2cp.get(ent)
            cp = cp = name2codepoint.get(ent)
    
            if cp:
                #return unichr(cp)
                return chr(cp)
            else:
                return match.group()
    
    return entity_re.subn(substitute_entity, string)[0]


# @register.filter
# def field_verbose_name(model,field):
#     try:
#         output = filter(lambda f: f.name == field, model._meta._fields())[0].verbose_name
#     except:
#         output = ""
#     return output

@register.filter
def field_verbose_name(model,field):
    try:
        #output = filter(lambda f: f.name == field, model._meta._fields())[0].verbose_name
        field_object = next(f for f in model._meta.get_fields() if f.name == field)
        output = field_object.verbose_name
    except (StopIteration, AttributeError):
        output = ""
    return output

@register.filter
def meta(value,arg):
    try:
        return smart_str(value._meta.__getattribute__(arg))
    except:
        return ""


@register.filter
def date_f(model,param):
    try:
        (field,format_str,sep) = param.split('|')
    except ValueError:
        field = param
        format_str = 'dmY'
        sep = '.'
    
    try:
        model_field = model.__getattribute__(field)
    except:
        return "error 1"
    
    output = ""
    if model_field:
        output = model_field
        field_format = model.__getattribute__("%s_f" % field)
        if field_format:
            user_format = sep.join([c for c in format_str if c in field_format])
        else:
            user_format = sep.join([c for c in format_str])
        
        try:
            output = format( model.__getattribute__(field), user_format )
        except:
            output = "error 2"
        
    return output

@register.filter
def date_biblio(model,param):
    try:
        model_field = model.__getattribute__(param)
    except:
        return "[s.d.]"
    if model_field:
        field_format = model.__getattribute__("%s_f" % param)
        if field_format:
            field_format = field_format.replace('-', ' ').replace('m', 'F').replace('%', '')
            return format(model_field, field_format)
        else:
            return model_field
    return "[s.d.]"

@register.filter
def substract(value, arg):
    """Substract the arg from the value."""
    return int(value) - int(arg)
substract.is_safe = False


@register.filter
def split(value,token):
    if not token:
        return value
    else:
        return ("%s"%value).split(token)

@register.filter
def attr(value,token):
    if not token:
        return value
    else:
        return [ item.__getattribute__(token) for item in value ]
 

RE_A_TAG = re.compile(r'(<a[^>]+>).*(</a>)')
@register.filter
def urlizename(url, name="link"):
    urlized = RE_A_TAG.sub(r'\1%s\2'%name, urlize(url))
    return mark_safe(urlized)


RE_HREF  = re.compile(r'href="([^"]+)"')
@register.filter
def docfileinfo(value):
    from fiches.models import DocumentFile
    #output = value
    anchors = re.compile(r'<a[^>]+>.*</a>').findall(value)
    for a in anchors:
        url = RE_HREF.search(a)
        if url:
            try:
                view, args, kwargs = resolve(urlparse(url.group(1))[2])
                docfile_key = kwargs['documentfile_key']
                docfile = DocumentFile.objects.get(slug=docfile_key)
                value = value.replace(a,"%s [%s]" % (a, template.defaultfilters.filesizeformat(docfile.file.size)))
            except Resolver404:
                pass
            except:
                #raise
                pass
    
    return mark_safe(value)
 
 
@register.filter
def truncatechars(value,token):
    max_len = int(token)
    if len(value) > max_len:
        value = value[:(max_len-3)] + "..."
    return value
 

@register.filter
def truncate_chars(s, num, end_text='...'):
    """Truncates a string after a certain number of characters but don't truncate words.
    Takes an optional argument of what should be used to notify that the string has been
    truncated, defaults to ellipsis (...)"""
    s = force_str(s)
    length = int(num)
    if len(s.strip()) <= length:
        return s
    s = s.strip()
    words = s[:length].split()
    if len(words)>1:
        words = words[:-1]
    if not words[-1].endswith(end_text):
        words.append(end_text)
    return u' '.join(words)


@register.filter
def access_grouplist(value, token=""):
    """
    Return the list of all UserGroup, a user is member of.
    Not the same as user.usergroup_set.all() as it has to look also
    for the auth.Group the are listed in the UserGroup, the user can be member of
    those auth.Group. Not that easy to explain hum...
    """
    if not isinstance(value, User) and not isinstance(value, AnonymousUser):
        #raise template.TemplateSyntaxError, "value should be a User"
        raise TemplateSyntaxError("value should be a User")
    user = value
    group_list = UserGroup.objects.filter(groups__in=user.groups.all()) | user.usergroup_set.all()
    if token == 'as_id':
        group_list = [g.id for g in group_list]
    else:
        group_list = list(group_list)
    return group_list


@register.filter
def access_strict(df, token, any_login=False):
    """
    Return True if ACModel.user_acces is strictly validated. Always TRUE for staff members (user.is_staff == True )
    i.e access_public == True | access_owner == user | access_groups IN user.usergroups
    """
    
    if not isinstance(token, User) and not isinstance(token, AnonymousUser):
        raise TemplateSyntaxError("argument should be a User")
    user = token
    return user.is_staff | df.user_access(user, any_login=any_login)

@register.filter
def access_lazy(df, token):
    """
    Return True if ACModel.user_acces is validated for any_login
    i.e: ! user.isAnonymous() | access_public == True | access_owner == user | access_groups IN user.usergroups
    """
    return access_strict(df, token, any_login=True)


@register.filter
def df_access(df, token):
    """
    Original filter for access control checking. 
    Was mainly used for Document File, but now we try to generilise it's use
    
    DEPRECATED, use access_lazy instead
    """
    return access_lazy(df, token)



class TooltipLinkNode(template.Node):
    def __init__(self, id):
        if re.match(r'^"[a-zA-Z0-9_-]+"$', id):
            self.id = id[1:-1]
        else:
            self.id = None
            self.id_to_be_resolved = template.Variable(id)
        
    def render(self, context):
        try:
            if self.id is None:
                tooltip_id = self.id_to_be_resolved.resolve(context)
            else:
                tooltip_id = self.id
            return '<span class="tooltiplink"><a href="#%s" class="tooltiplink">?</a></span>' % tooltip_id
#            return '<span class="tooltiplink ui-state-default"><a href="#%s" class="ui-icon ui-icon-help"></a></span>' % tooltip_id
        except template.VariableDoesNotExist:
            return ""


@register.tag("tooltiplink")
def tooltiplink(parser, token):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise TemplateSyntaxError("%r tag requires one argument" % token.contents.split()[0])
    
#    if not re.match(r'^[a-zA-Z0-9_-]+$', arg):
#        raise template.TemplateSyntaxError, "%r tag argument is incorrect, only [a-zA-Z0-9_-] char accepted" % tag_name
#    
    return TooltipLinkNode(arg)



class TimestampNode(template.Node):
    def __init__(self, token):
        self.token = token
    def render(self,context):
        val = "timestamp %s: %s" % (str(self.token).ljust(40), time.time())
        return ""
    
@register.tag("timestamp")
def timstamp(parser, token):
    return TimestampNode(token.split_contents()[1])


from django.core.cache import cache 
# class BiblioRefNode(template.Node):
#     def __init__(self, template_filename='fiches/bibliography_references/biblio_template.html'):
#         self.template = get_template(template_filename)
#     def render(self, context):
#         ref_key = 'lumieres__biblioref__%s' % context['ref'].id
#         ref_string = cache.get(ref_key)
#         if ref_string is None:
#             ref_string = self.template.render(context)
#             cache.set(ref_key, ref_string, 60 * 60 * 24 * 3)  # 3 jours
#             print (ref_string)
#         return ref_string

class BiblioRefNode(template.Node):
    def __init__(self, template_filename='fiches/bibliography_references/biblio_template.html'):
        self.template = get_template(template_filename)
        
    def render(self, context):
        ref = context.get('ref')
        if not ref:
            return ''
        
        ref_key = f'lumieres__biblioref__{ref.id}'
        #ref_key = 'lumieres__biblioref__%s' % context['ref'].id
        ref_string = cache.get(ref_key)
        if ref_string is None:
            # Ensure context is a dictionary
            context_dict = context.flatten() if hasattr(context, 'flatten') else dict(context)
            ref_string = self.template.render(context_dict)
            cache.set(ref_key, ref_string, 60 * 60 * 24 * 3)  # Cache for 3 days
        return ref_string
        
@register.tag(name='biblioref')
def biblioref(parser, token):
    try:
        # Splitting by None == splitting by spaces.
        tag_name, template_filename = token.contents.split(None, 1)
        kwargs = {'template_filename':template_filename}
    except ValueError:
        kwargs = {}
    return BiblioRefNode(**kwargs)

# @register.tag(name='biblioref')
# def biblioref(parser, token):
#     try:
#         tag_name, template_filename = token.contents.split(None, 1)
#     except ValueError:
#         raise template.TemplateSyntaxError("'{% biblioref %}' tag requires exactly one argument.")

#     return BiblioRefNode(template_filename)

class ACCheckNode(template.Node):
    def __init__(self, object_to_be_checked, user_to_check, var_name=None):
        self.object_to_be_checked = template.Variable(object_to_be_checked)
        self.user_to_check = template.Variable(user_to_check)
        self.var_name = var_name
    def render(self, context):
        user_access = self.object_to_be_checked.resolve(context).user_access(self.user_to_check.resolve(context))
        if self.var_name:
            context[self.var_name] = user_access
            return ""
        else:
            return user_access
    
@register.tag(name="ac_check")
def do_ac_check(parser, token):
#    try:
#        tag_name, object_to_be_checked, user_to_check = token.split_contents()
#    except ValueError:
#        raise template.TemplateSyntaxError, "%r tag requires exactly two arguments" % token.contents.split()[0]
#    return ACCheckNode(object_to_be_checked, user_to_check)

    try:
        # Splitting by None == splitting by spaces.
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise TemplateSyntaxError("%r tag requires arguments" % token.contents.split()[0])
    m = re.search(r'^(.\w+)\s+(\w+?)$', arg)
    if m:
        object_to_be_checked, user_to_check = m.groups()
        var_name = None
    else:
        m = re.search(r'^(.*?)\s+(.*?)\s+as\s+(\w+)$', arg)
        if not m:
            raise TemplateSyntaxError("%r tag had invalid arguments" % tag_name)
        object_to_be_checked, user_to_check, var_name = m.groups()
        
    return ACCheckNode(object_to_be_checked, user_to_check, var_name)

@register.tag(name='captureas')
def do_captureas(parser, token):
    try:
        tag_name, args = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("'captureas' node requires a variable name.")
    nodelist = parser.parse(('endcaptureas',))
    parser.delete_first_token()
    return CaptureasNode(nodelist, args)

class CaptureasNode(template.Node):
    def __init__(self, nodelist, varname):
        self.nodelist = nodelist
        self.varname = varname

    def render(self, context):
        output = self.nodelist.render(context)
        context[self.varname] = output
        return ''

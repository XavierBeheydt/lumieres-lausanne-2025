'''
MySQL group_concat with aggregates

by Matthew Somerville
http://www.mail-archive.com/django-users@googlegroups.com/msg74611.html
[ Message text ]
Hi,

I have the model described at 
http://docs.djangoproject.com/en/dev/topics/db/models/#intermediary-manytomany 
on which I have multiple rows in Membership with the same Person and 
Group (say they're a bit flaky, and leave and rejoin a few times ;) ). I 
wanted to print out a paginated list of groups someone is in, with all 
their joining dates in each group result.

I decided to try the new aggregate functionality. Here's my view:

    from aggregates import Concatenate
    groups = person.group_set
        .annotate(Concatenate('membership__date_joined'))
        .order_by('name')
    page = Paginator(groups, 10).page(1)

And my Concatenate class looks like this:

    from django.db.models import Aggregate
    from django.db.models.sql.aggregates import Aggregate as AggregateSQL
    from django.db.models import DecimalField

    class ConcatenateSQL(AggregateSQL):
       sql_function = 'GROUP_CONCAT'
       def __init__(self, col, separator='|', source=None, **extra):
          self.sql_template = "%%(function)s(%%(field)s ORDER BY 
%%(field)s SEPARATOR '%s')" % separator
          c = DecimalField() # XXX
          super(ConcatenateSQL, self).__init__(col, source=c, **extra)

    class Concatenate(Aggregate):
       name = 'Concatenate'
       def add_to_query(self, query, alias, col, source, is_summary):
          aggregate = ConcatenateSQL(col, separator=' / ', 
is_summary=is_summary)
          query.connection.ops.check_aggregate_support(aggregate)
          query.aggregates[alias] = aggregate

This works lovely, so the only issue I found was that I had to use a 
fake DecimalField() in order for the result from the database to get 
past the call to convert_values() in django/db/backends/__init__.py 
(called from django/db/models/sql/query.py in resolve_aggregate()). This 
function appears to only want numbers/datetimes to go in, and in this 
case I'm obviously returning text. Not sure what to suggest as a 
solution, as there are presumably other things going on of which I'm not 
aware, but the above works for me :)

ATB,
Matthew
[ end Message text ]
'''
# from django.db.models import Aggregate
# from django.db.models.sql.aggregates import Aggregate as AggregateSQL
# from django.db.models import DecimalField

from django.db import models

class ConcatenateSQL(models.Aggregate):
   function = 'GROUP_CONCAT'
   
   def __init__(self, col, separator='|', **extra):
      self.sql_template = "%(function)s(DISTINCT %(field)s ORDER BY %(field)s SEPARATOR '%s')" % separator
      super().__init__(col, **extra)

class Concatenate(models.Aggregate):
   name = 'Concatenate'
   
   def add_to_query(self, query, alias, col, source, is_summary):
      aggregate = ConcatenateSQL(col, separator='|', is_summary=is_summary)
      query.aggregates[alias] = aggregate


# class ConcatenateSQL(AggregateSQL):
#    sql_function = 'GROUP_CONCAT'
#    def __init__(self, col, separator='|', source=None, **extra):
#       self.sql_template = "%%(function)s(DISTINCT %%(field)s ORDER BY %%(field)s SEPARATOR '%s')" % separator
#       c = DecimalField() # XXX
#       super(ConcatenateSQL, self).__init__(col, source=c, **extra)

# class Concatenate(Aggregate):
#    name = 'Concatenate'
#    def add_to_query(self, query, alias, col, source, is_summary):
#       aggregate = ConcatenateSQL(col, separator='|', is_summary=is_summary)
#       # Commented out this line for compatibility with 1.2 12831
#       #query.connection.ops.check_aggregate_support(aggregate)
#       query.aggregates[alias] = aggregate
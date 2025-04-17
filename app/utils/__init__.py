#from django.utils.log import getLogger
import logging
from django.conf import settings

if not settings.DEBUG:
    dbg_logger = logging.getLogger('django')
else:
    try:
        dbg_logger = logging.getLogger('lumieres.debug')
    except:
        dbg_logger = logging.getLogger('django')



# ## Taken from http://www.djangosnippets.org/snippets/1282/
# from django.db.models.query import CollectedObjects
# from django.db.models.fields.related import ForeignKey
# 
# def duplicate(obj, value=None, field=None, exclude_models=[]):
#     """
#     Duplicate all related objects of `obj`. 
#     If one of the duplicate
#     objects has an FK to another duplicate object
#     update that as well. Return the duplicate copy
#     of `obj`.  
#     """
#     collected_objs = CollectedObjects()
#     obj._collect_sub_objects(collected_objs)
#     related_models = collected_objs.keys()
#     root_obj = None
#     # Traverse the related models in reverse deletion order.
#     for model in reversed(related_models):
#         if model.__name__ in exclude_models: break
#         
#         # Find all FKs on `model` that point to a `related_model`.
#         fks = []
#         for f in model._meta.fields:
#             if isinstance(f, ForeignKey) and f.rel.to in related_models:
#                 fks.append(f)
#         # Replace each `sub_obj` with a duplicate.
#         sub_obj = collected_objs[model]
#         for pk_val, obj in sub_obj.iteritems():
#             for fk in fks:
#                 fk_value = getattr(obj, "%s_id" % fk.name)
#                 # If this FK has been duplicated then point to the duplicate.
#                 if fk_value in collected_objs[fk.rel.to]:
#                     dupe_obj = collected_objs[fk.rel.to][fk_value]
#                     setattr(obj, fk.name, dupe_obj)
#             # Duplicate the object and save it.
#             obj.id = None
#             if value and field:
#                 setattr(obj, field, value)
#             obj.save()
#             if root_obj is None:
#                 root_obj = obj
#     return root_obj

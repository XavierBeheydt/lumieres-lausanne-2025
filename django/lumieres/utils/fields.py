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
from django.db import models
from django.utils.encoding import smart_str
import pickle

class DictField(models.Field):
    """DictField is a TextField that contains pickled dictionaries."""

    # Use the Python 3 style for defining metaclasses.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        """Convert the database value to a Python dictionary."""
        if value is None:
            return value
        # try:
        #     return pickle.loads(smart_str(value))
        # except ValueError:
        #     return value
        try:
            return pickle.loads(value.encode('latin1'))  # Using bytes directly
        except (pickle.PickleError, ValueError):
            return value
    
    def to_python(self, value):
        #"""Convert the value to a Python dictionary."""
        """Unpickle our string value to Dict after we load it from the DB."""

        if value == "":
            return None

        elif isinstance(value, dict):
            return value

        try:
            if isinstance(value, str):  # Use `str` in Python 3 instead of `basestring`.
                return pickle.loads(smart_str(value))
        except (ValueError, pickle.UnpicklingError):
            return value

        return value

        # try:
        #     return pickle.loads(smart_str(value))
        # except ValueError:
        #     return value
        # try:
        #     print ("to_python called")
        #     return pickle.loads(value.encode('latin1'))  # Using bytes directly
        # except (pickle.PickleError, ValueError):
        #     return value

    def get_db_prep_save(self, value, connection):
        """Pickle our Dict object to a string before we save."""
        if isinstance(value, dict):
            value = pickle.dumps(value)
        else:
            return None
        
        return super(DictField, self).get_db_prep_save(value, connection)
    
    # def get_prep_value(self, value):
    #     """Prepare the value for saving to the database."""
    #     print ("get_prep_value called")
    #     if value is None:
    #         print("get_prep_value value is None")
    #         return value
    #     else:
    #         print("get_prep_value value is not None")
    #     # if not isinstance(value, dict):
    #     #     raise ValueError("Expected a dictionary, got {}".format(type(value)))
    #     # return pickle.dumps(value)
    #     if not isinstance(value, dict):
    #         raise ValueError(f"Expected a dictionary, got {type(value)}")
    #     return pickle.dumps(value).decode('latin1')  # Convert bytes back to a string

    # def get_internal_type(self):
    #     return "TextField"  # Maps to a text field in the database

# class DictField(models.TextField):
#     """DictField is a textfield that contains pickled dictionaries."""
    
#     # Used so to_python() is called
#     __metaclass__ = models.SubfieldBase
    
#     def to_python(self, value):
#         """Unpickle our string value to Dict after we load it from the DB"""
#         if value == "":
#             return None

#         try:
#             if isinstance(value, basestring):
#                 return pickle.loads(smart_str(value))
#         except ValueError:
#             return value

#         return value
    
#     def get_db_prep_save(self, value, connection):
#         """Pickle our Dict object to a string before we save"""
#         #assert isinstance(value, dict)
#         if isinstance(value, dict):
#             value = pickle.dumps(value)
#         else:
#             return None
        
#         return super(DictField, self).get_db_prep_save(value, connection)

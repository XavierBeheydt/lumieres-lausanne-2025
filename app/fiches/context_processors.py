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

def fiches(request):
    context_extra = {}
    context_extra.update({'display_collector': True})
    context_extra.update({
        'DOCTYPE' : {
           'LIVRE': 1,
           'CHAPITRE_LIVRE': 2,
           'ARTICLE_REVUE': 3,
           'ARTICLE_DICO': 4,
           'MANUSCRIT': 5,
        }
    })
    #context_extra.update({'LAYOUT_VERSION': request.COOKIES.get('layoutversion', "2")})
    return context_extra
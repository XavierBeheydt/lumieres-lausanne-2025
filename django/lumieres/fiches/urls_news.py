# -*- coding: utf-8 -*-
#
#    Copyright (C) 2013 Florian Steffen
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
from django.urls import path
from fiches.views.news import index, display_news

urlpatterns = [
    # URL principal pour les News
    path('', index, name='news-index'),
    
    # Afficher une News sépécifique par ID
    path('<int:news_id>/', display_news, name='news-display'),
]

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
from django.shortcuts import render, get_object_or_404
from fiches.models import News
from django.http import HttpResponseForbidden


def index(request):
    news = News.objects.filter(published=True)
    #news = News.objects.filter(published=True).order_by('-created_on')  # Order by created_on descending
    #print("printing news query...")
    #print(news.query)  # Print the raw SQL query


    #for n in news:
        #print(n.created_on)  # Print the dates to check order

    context = {'news': news }
    return render(request, 'fiches/news/index.html', context)
    
def display_news(request, news_id):
    news = get_object_or_404(News, pk=news_id)
    
    if not news.published and (not request.user.is_authenticated() or not request.user.has_perm('fiches.change_news')):
        return HttpResponseForbidden("Access denied")
        
    context = {'news': news }
    return render(request, 'fiches/news/display.html', context)
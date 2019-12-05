"""tendies URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from .views import (
    get_stock_tick_data, 
    delete_stock_tick_data, 
    insert_stock_tick_data, 
    get_subreddit_sentiment_disagreement, 
    get_sentiment_popularity_correlation, 
    get_moving_volatility,
    get_sentiment_count
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'tick_data', 
        get_stock_tick_data, 
        name='get_stock_tick_data'
    ),
    path(
        'delete_tick_data',
        delete_stock_tick_data,
        name='delete_stock_tick_data'
    ),
    path(
        'insert_tick_data',
        insert_stock_tick_data,
        name='insert_stock_tick_data'
    ),
    path(
        'subreddit_sentiment_disagreement',
        get_subreddit_sentiment_disagreement,
        name='get_subreddit_sentiment_disagreement'
    ),
    path(
        'sentiment_popularity_correlation',
        get_sentiment_popularity_correlation,
        name='get_sentiment_popularity_correlation'
    ),
    path(
        'moving_volatility',
        get_moving_volatility,
        name='get_moving_volatility'
    ),
    path(
        'sentiment_count',
        get_sentiment_count,
        name='get_sentiment_count'
    )
]

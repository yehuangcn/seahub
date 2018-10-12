# Copyright (c) 2012-2018 Seafile Ltd.
from django.conf.urls import url

from seahub.api3.dir import DirView

urlpatterns = [
    url(r'^repos/(?P<repo_id>[-0-9-a-f]{36})/dir/$', DirView.as_view(), name='api2-repos-dir'),
]

# Copyright (c) 2012-2016 Seafile Ltd.
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from django.utils.translation import ugettext as _
from django.http import HttpResponse

from seahub.utils.ms_excel import write_xls
from seahub.api2.authentication import TokenAuthentication
from seahub.api2.throttling import UserRateThrottle
from seahub.api2.endpoints.admin.statistics import (
    check_parameter, get_init_data
)
from seahub.utils import get_org_traffic_by_day
from seahub.utils.timeutils import datetime_to_isoformat_timestr, UTC_TIME_OFFSET


def get_admin_org_stats_traffic_data(start_time, end_time, org_id):

    op_type_list = ['web-file-upload', 'web-file-download',
                    'sync-file-download', 'sync-file-upload',
                    'link-file-upload', 'link-file-download']
    init_count = [0] * 6
    init_data = get_init_data(start_time, end_time,
                              dict(zip(op_type_list, init_count)))

    for e in get_org_traffic_by_day(org_id, start_time, end_time,
                                    UTC_TIME_OFFSET):
        dt, op_type, count = e
        init_data[dt].update({op_type: count})

    res_data = []
    for k, v in init_data.items():
        res = {'datetime': datetime_to_isoformat_timestr(k)}
        res.update(v)
        res_data.append(res)

    return sorted(res_data, key=lambda x: x['datetime'])


class AdminOrgStatsTraffic(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    throttle_classes = (UserRateThrottle,)
    permission_classes = (IsAdminUser,)

    @check_parameter
    def get(self, request, start_time, end_time, *args, **kwargs):
        org_id = kwargs['org_id']

        res_data = get_admin_org_stats_traffic_data(start_time, end_time,
                org_id)

        return Response(res_data)


class AdminOrgStatsTrafficExcel(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    throttle_classes = (UserRateThrottle,)
    permission_classes = (IsAdminUser,)

    @check_parameter
    def get(self, request, start_time, end_time, *args, **kwargs):

        data_list = []
        head = [_("Time"), _("Upload"), _("Download")]
        org_id = kwargs['org_id']
        res_data = get_admin_org_stats_traffic_data(start_time, end_time,
                org_id)

        for data in res_data:

            upload_data = data['web-file-upload'] + \
                    data['sync-file-upload'] + data['link-file-upload']
            download_data = data['web-file-download'] + \
                    data['sync-file-download'] + data['link-file-download']
            row = [data['datetime'], upload_data, download_data]
            data_list.append(row)

        excel_name = _("Total Traffic")
        wb = write_xls(excel_name, head, data_list)

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=%s.xlsx' % excel_name
        wb.save(response)

        return response

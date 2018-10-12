# Copyright (c) 2012-2018 Seafile Ltd.
import stat
import logging

from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from seahub.api2.throttling import UserRateThrottle
from seahub.api2.authentication import TokenAuthentication
from seahub.api2.utils import api_error

from seahub.views import check_folder_permission
from seahub.utils import  normalize_dir_path
from seahub.utils.timeutils import timestamp_to_isoformat_timestr
from seahub.base.templatetags.seahub_tags import email2nickname, \
        email2contact_email

from seaserv import seafile_api

logger = logging.getLogger(__name__)

class DirView(APIView):
    """
    Support uniform interface for directory operations, including
    create/delete/rename/list, etc.
    """
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, )
    throttle_classes = (UserRateThrottle, )

    def get(self, request, repo_id, format=None):
        """ Get dir info.

        Permission checking:
        1. user with either 'r' or 'rw' permission.
        """

        # recource check
        repo = seafile_api.get_repo(repo_id)
        if not repo:
            error_msg = 'Library %s not found.' % repo_id
            return api_error(status.HTTP_404_NOT_FOUND, error_msg)

        path = request.GET.get('path', '/')
        path = normalize_dir_path(path)

        dir_id = seafile_api.get_dir_id_by_path(repo_id, path)
        if not dir_id:
            error_msg = 'Folder %s not found.' % path
            return api_error(status.HTTP_404_NOT_FOUND, error_msg)

        # permission check
        permission = check_folder_permission(request, repo_id, path)
        if not permission:
            error_msg = 'Permission denied.'
            return api_error(status.HTTP_403_FORBIDDEN, error_msg)

        # get dir info
        # TODO
        # dir_obj = seafile_api.get_dirent_by_path(repo_id, path)
        dir_info = {
            'permission': permission,
        }

        # get sub folder/file list
        username = request.user.username
        try:
            dirents = seafile_api.list_dir_with_perm(repo_id, path, dir_id, username, -1, -1)
        except Exception as e:
            logger.error(e)
            error_msg = 'Internal Server Error'
            return api_error(status.HTTP_500_INTERNAL_SERVER_ERROR, error_msg)

        dir_list = []
        file_list = []
        for dirent in dirents:

            entry = {}
            entry["name"] = dirent.obj_name
            entry["permission"] = dirent.permission

            if stat.S_ISDIR(dirent.mode):
                entry["type"] = "dir"
                dir_list.append(entry)
            else:
                entry["type"] = "file"
                entry["last_modified"] = timestamp_to_isoformat_timestr(dirent.mtime)
                entry['modifier_email'] = dirent.modifier
                entry["size"] = dirent.size
                entry["is_locked"] = dirent.is_locked
                entry["lock_owner"] = dirent.lock_owner or ''
                entry["lock_time"] = dirent.lock_time
                file_list.append(entry)

        # Use dict to reduce memcache fetch cost in large for-loop.
        contact_email_dict = {}
        nickname_dict = {}

        modifier_set = set([x['modifier_email'] for x in file_list])
        lock_owner_set = set([x['lock_owner'] for x in file_list])
        for e in modifier_set | lock_owner_set:
            if e not in contact_email_dict:
                contact_email_dict[e] = email2contact_email(e)
            if e not in nickname_dict:
                nickname_dict[e] = email2nickname(e)

        for e in file_list:
            e['modifier_name'] = nickname_dict.get(e['modifier_email'], '')
            e['modifier_contact_email'] = contact_email_dict.get(e['modifier_email'], '')

            e['lock_owner_name'] = nickname_dict.get(e['lock_owner'], '')
            e['lock_owner_contact_email'] = contact_email_dict.get(e['lock_owner'], '')

        dir_list.sort(lambda x, y: cmp(x['name'].lower(), y['name'].lower()))
        file_list.sort(lambda x, y: cmp(x['name'].lower(), y['name'].lower()))

        dir_info['dirent_list'] = dir_list + file_list

        return Response(dir_info)

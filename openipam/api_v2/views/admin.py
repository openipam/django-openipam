
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.admin.models import LogEntry
from ..serializers.admin import LogEntrySerializer, EmailLogSerializer
from openipam.log.models import EmailLog
from ..permissions import APIAdminPermission


class LogEntryList(APIView):
    permission_classes = [APIAdminPermission]

    def get(self, request, format=None):
        print(f'\nrequest: {request}')
        limit = 25
        page = request.query_params.get('page') or 1
        logs = LogEntry.objects.all().order_by('-action_time')
        logs = logs[int(page)*limit:(int(page)+1)*limit]
        serializer = LogEntrySerializer(logs, many=True)
        return Response(serializer.data)


class HostLogsList(APIView):
    permission_classes = [APIAdminPermission]

    def get(self, request, format=None):
        print(f'\nrequest: {request}')
        limit = 25
        page = request.query_params.get('page') or 1
        logs = LogEntry.objects.filter(content_type__model='host').order_by('-action_time')
        logs = logs[int(page)*limit:(int(page)+1)*limit]
        serializer = LogEntrySerializer(logs, many=True)
        return Response(serializer.data)


class EmailLogsList(APIView):
    permission_classes = [APIAdminPermission]

    def get(self, request, format=None):
        print(f'\nrequest: {request}')
        limit = 25
        page = request.query_params.get('page') or 1
        logs = EmailLog.objects.order_by('-when')
        logs = logs[int(page)*limit:(int(page)+1)*limit]
        serializer = EmailLogSerializer(logs, many=True)
        return Response(serializer.data)


class DnsLogsList(APIView):
    permission_classes = [APIAdminPermission]

    def get(self, request, format=None):
        print(f'\nrequest: {request}')
        limit = 25
        page = request.query_params.get('page') or 1
        logs = LogEntry.objects.filter(content_type__model='dnsrecord').order_by('-action_time')
        logs = logs[int(page)*limit:(int(page)+1)*limit]
        serializer = LogEntrySerializer(logs, many=True)
        return Response(serializer.data)


class AddressLogsList(APIView):
    permission_classes = [APIAdminPermission]

    def get(self, request, format=None):
        print(f'\nrequest: {request}')
        limit = 25
        page = request.query_params.get('page') or 1
        logs = LogEntry.objects.filter(content_type__model='address').order_by('-action_time')
        logs = logs[int(page)*limit:(int(page)+1)*limit]
        serializer = LogEntrySerializer(logs, many=True)
        return Response(serializer.data)


class UserLogsList(APIView):
    permission_classes = [APIAdminPermission]

    def get(self, request, format=None):
        print(f'\nrequest: {request}')
        limit = 25
        page = request.query_params.get('page') or 1
        logs = LogEntry.objects.filter(content_type__model='user').order_by('-action_time')
        logs = logs[int(page)*limit:(int(page)+1)*limit]
        serializer = LogEntrySerializer(logs, many=True)
        return Response(serializer.data)

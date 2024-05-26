from rest_framework import serializers


class SetTimerInputSerializer(serializers.Serializer):
    hours = serializers.IntegerField()
    minutes = serializers.IntegerField()
    seconds = serializers.IntegerField()
    web_url = serializers.URLField()

    class Meta:
        fields = ["hours", "minutes", "seconds", "web_url"]


class SetTimerOutputSerializer(serializers.Serializer):
    task_uuid = serializers.UUIDField(read_only=True)
    status = serializers.CharField(read_only=True)
    time_left = serializers.CharField(read_only=True)

    class Meta:
        fields = ["task_uuid", "time_left"]

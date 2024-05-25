from rest_framework import serializers


class SetTimerInputSerializer(serializers.Serializer):
    hours = serializers.IntegerField()
    minutes = serializers.IntegerField()
    seconds = serializers.IntegerField()
    web_url = serializers.URLField()

    class Meta:
        fields = ["hours", "minutes", "seconds", "web_url"]


class SetTimerOutputSerializer(serializers.ModelSerializer):
    task_id = serializers.UUIDField(source="id", read_only=True)
    time_left = serializers.CharField(source="get_time_left_display", read_only=True)

    class Meta:
        fields = ["id", "time_left"]

from rest_framework import serializers


class SetTimerInputSerializer(serializers.Serializer):
    hours = serializers.IntegerField(help_text="Number of hours to wait before sending the request.", min_value=0)
    minutes = serializers.IntegerField(help_text="Number of minutes to wait before sending the request.", min_value=0)
    seconds = serializers.IntegerField(help_text="Number of seconds to wait before sending the request.", min_value=0)
    web_url = serializers.URLField(help_text="URL to send the request to.")

    class Meta:
        fields = ["hours", "minutes", "seconds", "web_url"]


class SetTimerOutputSerializer(serializers.Serializer):
    task_id = serializers.IntegerField(read_only=True)
    time_left_in_seconds = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ["task_id", "time_left_in_seconds"]

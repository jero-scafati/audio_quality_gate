from rest_framework import serializers
from .models import AudioAnalysis

class AudioAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioAnalysis
        fields = ['id', 'file', 'uploaded_at', 'processed', 'is_multispeaker']
        read_only_fields = ['processed', 'is_multispeaker', 'uploaded_at']

    def validate_file(self, value):
        allowed_types = [
            "audio/wav",
            "audio/x-wav",
            "audio/mpeg",
            "audio/x-flac",
            "audio/flac",
            "audio/mp3",
        ]

        if value.content_type not in allowed_types:
            raise serializers.ValidationError("Solo se permiten archivos de audio.")

        return value
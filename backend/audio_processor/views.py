from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import AudioAnalysis
from .serializers import AudioAnalysisSerializer
from .logic import verify_multispeaker

class AudioAnalysisViewSet(viewsets.ModelViewSet):
    queryset = AudioAnalysis.objects.all().order_by('-uploaded_at')
    serializer_class = AudioAnalysisSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        """
        Sobreescribimos el método CREATE para ejecutar el algoritmo
        inmediatamente después de subir el archivo.
        """
        # 1. Validar y guardar el archivo en disco/db
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        # 2. Ejecutar tu algoritmo de IA
        print(f"🎤 Procesando audio: {instance.file.path}")
        is_multi = verify_multispeaker(instance.file.path)
        
        # 3. Actualizar la instancia
        # ¡OJO! Al hacer este .save(), se dispara el Trigger SQL si es True
        instance.is_multispeaker = is_multi
        instance.processed = True
        instance.save() 

        # 4. Devolver respuesta con el resultado
        return Response(serializer.data, status=status.HTTP_201_CREATED)

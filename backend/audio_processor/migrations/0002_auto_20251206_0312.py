from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('audio_processor', '0001_initial'), 
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE FUNCTION log_rejected_audio()
            RETURNS TRIGGER AS $$
            BEGIN
                -- Si el campo is_multispeaker cambia a TRUE (detectamos voces superpuestas)
                IF NEW.is_multispeaker = TRUE THEN
                    -- Insertamos automáticamente en la tabla de auditoría
                    INSERT INTO audio_processor_auditlog (audio_ref_id, reason, created_at)
                    VALUES (NEW.id, 'RECHAZADO: Múltiples hablantes detectados (Automated by DB)', NOW());
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            """,
            reverse_sql="DROP FUNCTION IF EXISTS log_rejected_audio();"
        ),

        migrations.RunSQL(
            sql="""
            CREATE TRIGGER check_audio_quality_trigger
            AFTER UPDATE OF is_multispeaker ON audio_processor_audioanalysis
            FOR EACH ROW
            WHEN (NEW.is_multispeaker = TRUE)
            EXECUTE FUNCTION log_rejected_audio();
            """,
            reverse_sql="DROP TRIGGER IF EXISTS check_audio_quality_trigger ON audio_processor_audioanalysis;"
        ),
    ]
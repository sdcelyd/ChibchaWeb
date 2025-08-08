import polib
from googletrans import Translator
import time
import argparse
import logging
import os
from typing import Optional
import json

# Configuración de logging con soporte para UTF-8
import sys

# Configurar la salida estándar para UTF-8 en Windows
if sys.platform.startswith('win'):
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Crear handlers con codificación UTF-8
file_handler = logging.FileHandler('translation.log', encoding='utf-8')
stream_handler = logging.StreamHandler()

# En Windows, configurar la codificación de la consola
if sys.platform.startswith('win'):
    stream_handler.setStream(open(sys.stdout.fileno(), 'w', encoding='utf-8', buffering=1))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[file_handler, stream_handler]
)
logger = logging.getLogger(__name__)

class PoTranslator:
    def __init__(self, src_lang='es', dest_lang='en', delay=0.5):
        self.src_lang = src_lang
        self.dest_lang = dest_lang
        self.delay = delay
        self.translator = Translator()
        self.stats = {
            'total': 0,
            'translated': 0,
            'failed': 0,
            'skipped': 0
        }
    
    def _is_translatable(self, text: str) -> bool:
        """Verifica si un texto debe ser traducido"""
        if not text.strip():
            return False
        
        # Skip if it's only variables/placeholders
        if text.strip().startswith('%') or text.strip().startswith('{'):
            return False
        
        # Skip if it's only HTML tags
        import re
        if re.match(r'^<[^>]+>$', text.strip()):
            return False
            
        return True
    
    def _backup_file(self, po_path: str) -> str:
        """Crea una copia de respaldo del archivo .po"""
        backup_path = f"{po_path}.backup"
        if os.path.exists(po_path):
            with open(po_path, 'r', encoding='utf-8') as src:
                with open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            logger.info(f"Backup creado: {backup_path}")
        return backup_path
    
    def _translate_text(self, text: str) -> Optional[str]:
        """Traduce un texto con manejo de errores y reintentos"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                result = self.translator.translate(text, src=self.src_lang, dest=self.dest_lang)
                return result.text
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # Backoff exponencial
                    logger.warning(f"⚠️ Intento {attempt + 1} fallido, reintentando en {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ Falló después de {max_retries} intentos: {text[:50]}...")
                    return None
        
        return None
    
    def translate_po_file(self, po_path: str, create_backup: bool = True) -> dict:
        """Traduce un archivo .po completo"""
        if not os.path.exists(po_path):
            raise FileNotFoundError(f"El archivo {po_path} no existe")
        
        start_time = time.time()
        logger.info(f"Iniciando traduccion de: {po_path}")
        logger.info(f"Idiomas: {self.src_lang} -> {self.dest_lang}")
        
        # Crear backup
        if create_backup:
            self._backup_file(po_path)
        
        # Cargar archivo .po
        try:
            po = polib.pofile(po_path)
        except Exception as e:
            logger.error(f"Error al cargar el archivo .po: {e}")
            raise
        
        untranslated = po.untranslated_entries()
        self.stats['total'] = len(untranslated)
        
        if self.stats['total'] == 0:
            logger.info("No hay entradas sin traducir")
            return self.stats
        
        logger.info(f"Entradas sin traducir: {self.stats['total']}")
        
        # Procesar entradas
        for i, entry in enumerate(untranslated, start=1):
            self._process_entry(entry, i, self.stats['total'])
            
            # Pausa entre traducciones
            if i < self.stats['total']:  # No pausar después de la última
                time.sleep(self.delay)
        
        # Guardar archivos
        try:
            po.save()
            mo_path = po_path.replace('.po', '.mo')
            po.save_as_mofile(mo_path)
            logger.info(f"💾 Archivos guardados: {po_path}, {mo_path}")
        except Exception as e:
            logger.error(f"❌ Error al guardar archivos: {e}")
            raise
        
        # Estadísticas finales
        duration = round(time.time() - start_time, 2)
        self._log_stats(duration)
        
        return self.stats
    
    def _process_entry(self, entry, current: int, total: int):
        """Procesa una entrada individual"""
        progress = f"[{current}/{total}]"
        original_text = entry.msgid
        
        logger.info(f"{progress} Procesando: {original_text[:60]}...")
        
        # Verificar si debe traducirse
        if not self._is_translatable(original_text):
            logger.info(f"{progress} ⏭️ Omitido (no traducible)")
            self.stats['skipped'] += 1
            return
        
        # Traducir
        translation = self._translate_text(original_text)
        
        if translation:
            entry.msgstr = translation
            logger.info(f"{progress} ✅ Traducido: {translation[:60]}...")
            self.stats['translated'] += 1
        else:
            logger.error(f"{progress} ❌ Falló la traducción")
            self.stats['failed'] += 1
    
    def _log_stats(self, duration: float):
        """Registra las estadísticas finales"""
        logger.info("\n" + "="*50)
        logger.info("RESUMEN DE TRADUCCION")
        logger.info("="*50)
        logger.info(f"Tiempo total: {duration} segundos")
        logger.info(f"Total procesadas: {self.stats['total']}")
        logger.info(f"Traducidas exitosamente: {self.stats['translated']}")
        logger.info(f"Fallidas: {self.stats['failed']}")
        logger.info(f"Omitidas: {self.stats['skipped']}")
        
        if self.stats['total'] > 0:
            success_rate = (self.stats['translated'] / self.stats['total']) * 100
            logger.info(f"Tasa de exito: {success_rate:.1f}%")
        
        logger.info("="*50)

def load_config(config_path: str) -> dict:
    """Carga configuración desde un archivo JSON"""
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def main():
    parser = argparse.ArgumentParser(description='Traductor de archivos Django .po')
    parser.add_argument('po_file', help='Ruta del archivo .po a traducir')
    parser.add_argument('--src', default='es', help='Idioma origen (default: es)')
    parser.add_argument('--dest', default='en', help='Idioma destino (default: en)')
    parser.add_argument('--delay', type=float, default=0.5, help='Pausa entre traducciones en segundos')
    parser.add_argument('--no-backup', action='store_true', help='No crear archivo de respaldo')
    parser.add_argument('--config', help='Archivo de configuración JSON')
    
    args = parser.parse_args()
    
    # Cargar configuración si existe
    config = load_config(args.config) if args.config else {}
    
    # Aplicar configuración
    src_lang = config.get('src_lang', args.src)
    dest_lang = config.get('dest_lang', args.dest)
    delay = config.get('delay', args.delay)
    
    try:
        translator = PoTranslator(src_lang=src_lang, dest_lang=dest_lang, delay=delay)
        stats = translator.translate_po_file(args.po_file, create_backup=not args.no_backup)
        
        if stats['failed'] > 0:
            exit(1)  # Exit con error si hubo fallos
        
    except KeyboardInterrupt:
        logger.info("\n⚠️ Traducción interrumpida por el usuario")
        exit(1)
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        exit(1)

if __name__ == "__main__":
    # Si se ejecuta directamente sin argumentos, usar configuración por defecto
    import sys
    if len(sys.argv) == 1:
        # Configuración por defecto para compatibilidad
        PO_FILE_PATH = 'locale/en/LC_MESSAGES/django.po'
        translator = PoTranslator()
        try:
            translator.translate_po_file(PO_FILE_PATH)
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            exit(1)
    else:
        main()
#!/usr/bin/env python3
"""
Script de respaldo y restauración para la base de datos Redis.
Permite crear respaldos de los datos y restaurarlos cuando sea necesario.
"""

import sys
import os
import json
import gzip
from datetime import datetime
import argparse

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.services.storage_service import StorageService


class BackupManager:
    """Gestor de respaldos para la base de datos."""
    
    def __init__(self):
        self.storage = StorageService()
        self.backup_dir = os.path.join(os.path.dirname(__file__), '..', 'backups')
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self, filename=None):
        """Crea un respaldo completo de la base de datos."""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'backup_textiles_als_{timestamp}.json.gz'
        
        backup_path = os.path.join(self.backup_dir, filename)
        
        print(f"🔄 Creando respaldo: {filename}")
        
        try:
            # Obtener todas las claves de Redis
            redis_client = self.storage.get_redis_client()
            all_keys = redis_client.keys('*')
            
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'version': '1.0',
                'total_keys': len(all_keys),
                'data': {}
            }
            
            # Exportar todos los datos
            for key in all_keys:
                key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                
                # Determinar el tipo de datos
                key_type = redis_client.type(key).decode('utf-8')
                
                if key_type == 'string':
                    value = redis_client.get(key)
                    if value:
                        backup_data['data'][key_str] = {
                            'type': 'string',
                            'value': value.decode('utf-8') if isinstance(value, bytes) else value
                        }
                elif key_type == 'hash':
                    value = redis_client.hgetall(key)
                    if value:
                        decoded_value = {}
                        for k, v in value.items():
                            k_str = k.decode('utf-8') if isinstance(k, bytes) else k
                            v_str = v.decode('utf-8') if isinstance(v, bytes) else v
                            decoded_value[k_str] = v_str
                        backup_data['data'][key_str] = {
                            'type': 'hash',
                            'value': decoded_value
                        }
                elif key_type == 'list':
                    value = redis_client.lrange(key, 0, -1)
                    if value:
                        decoded_value = [
                            item.decode('utf-8') if isinstance(item, bytes) else item 
                            for item in value
                        ]
                        backup_data['data'][key_str] = {
                            'type': 'list',
                            'value': decoded_value
                        }
                elif key_type == 'set':
                    value = redis_client.smembers(key)
                    if value:
                        decoded_value = [
                            item.decode('utf-8') if isinstance(item, bytes) else item 
                            for item in value
                        ]
                        backup_data['data'][key_str] = {
                            'type': 'set',
                            'value': decoded_value
                        }
            
            # Comprimir y guardar
            with gzip.open(backup_path, 'wt', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            file_size = os.path.getsize(backup_path)
            print(f"✅ Respaldo creado exitosamente:")
            print(f"   📁 Archivo: {backup_path}")
            print(f"   📊 Tamaño: {file_size / 1024:.2f} KB")
            print(f"   🔑 Claves exportadas: {len(all_keys)}")
            
            return backup_path
            
        except Exception as e:
            print(f"❌ Error al crear respaldo: {str(e)}")
            return None
    
    def restore_backup(self, backup_path, confirm=True):
        """Restaura un respaldo de la base de datos."""
        if not os.path.exists(backup_path):
            print(f"❌ Archivo de respaldo no encontrado: {backup_path}")
            return False
        
        if confirm:
            response = input("⚠️  Esta operación eliminará todos los datos actuales. ¿Continuar? (y/N): ")
            if response.lower() != 'y':
                print("Operación cancelada.")
                return False
        
        print(f"🔄 Restaurando respaldo: {backup_path}")
        
        try:
            # Leer archivo de respaldo
            with gzip.open(backup_path, 'rt', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            redis_client = self.storage.get_redis_client()
            
            # Limpiar base de datos actual
            redis_client.flushall()
            print("   🗑️  Base de datos limpiada")
            
            # Restaurar datos
            restored_count = 0
            for key, data in backup_data['data'].items():
                data_type = data['type']
                value = data['value']
                
                if data_type == 'string':
                    redis_client.set(key, value)
                elif data_type == 'hash':
                    redis_client.hset(key, mapping=value)
                elif data_type == 'list':
                    redis_client.lpush(key, *reversed(value))
                elif data_type == 'set':
                    redis_client.sadd(key, *value)
                
                restored_count += 1
            
            print(f"✅ Respaldo restaurado exitosamente:")
            print(f"   📊 Respaldo del: {backup_data['timestamp']}")
            print(f"   🔑 Claves restauradas: {restored_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al restaurar respaldo: {str(e)}")
            return False
    
    def list_backups(self):
        """Lista todos los respaldos disponibles."""
        print("📋 Respaldos disponibles:")
        
        backup_files = [f for f in os.listdir(self.backup_dir) if f.endswith('.json.gz')]
        
        if not backup_files:
            print("   No hay respaldos disponibles")
            return []
        
        backup_files.sort(reverse=True)  # Más recientes primero
        
        for i, filename in enumerate(backup_files, 1):
            filepath = os.path.join(self.backup_dir, filename)
            file_size = os.path.getsize(filepath)
            mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            print(f"   {i:2d}. {filename}")
            print(f"       📅 Creado: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"       📊 Tamaño: {file_size / 1024:.2f} KB")
        
        return backup_files
    
    def cleanup_old_backups(self, keep_count=10):
        """Elimina respaldos antiguos, manteniendo solo los más recientes."""
        backup_files = [f for f in os.listdir(self.backup_dir) if f.endswith('.json.gz')]
        backup_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.backup_dir, x)), reverse=True)
        
        if len(backup_files) <= keep_count:
            print(f"✅ No se necesita limpieza (respaldos: {len(backup_files)}, límite: {keep_count})")
            return
        
        to_delete = backup_files[keep_count:]
        
        print(f"🗑️  Eliminando {len(to_delete)} respaldos antiguos...")
        
        for filename in to_delete:
            filepath = os.path.join(self.backup_dir, filename)
            try:
                os.remove(filepath)
                print(f"   ✅ Eliminado: {filename}")
            except Exception as e:
                print(f"   ❌ Error eliminando {filename}: {str(e)}")
        
        print(f"✅ Limpieza completada. Respaldos restantes: {keep_count}")


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(description='Gestor de respaldos para Textiles ALS')
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando backup
    backup_parser = subparsers.add_parser('backup', help='Crear un respaldo')
    backup_parser.add_argument('--filename', help='Nombre del archivo de respaldo')
    
    # Comando restore
    restore_parser = subparsers.add_parser('restore', help='Restaurar un respaldo')
    restore_parser.add_argument('filename', help='Archivo de respaldo a restaurar')
    restore_parser.add_argument('--no-confirm', action='store_true', help='No pedir confirmación')
    
    # Comando list
    list_parser = subparsers.add_parser('list', help='Listar respaldos disponibles')
    
    # Comando cleanup
    cleanup_parser = subparsers.add_parser('cleanup', help='Limpiar respaldos antiguos')
    cleanup_parser.add_argument('--keep', type=int, default=10, help='Número de respaldos a mantener')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Crear la aplicación Flask
    app = create_app()
    
    with app.app_context():
        try:
            backup_manager = BackupManager()
            
            if args.command == 'backup':
                backup_manager.create_backup(args.filename)
            
            elif args.command == 'restore':
                backup_path = args.filename
                if not os.path.isabs(backup_path):
                    backup_path = os.path.join(backup_manager.backup_dir, backup_path)
                backup_manager.restore_backup(backup_path, confirm=not args.no_confirm)
            
            elif args.command == 'list':
                backup_manager.list_backups()
            
            elif args.command == 'cleanup':
                backup_manager.cleanup_old_backups(args.keep)
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            sys.exit(1)


if __name__ == '__main__':
    main()

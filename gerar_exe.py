#!/usr/bin/env python
"""
Script para gerar o executável Windows da aplicação ConsultaNF
Execute: python gerar_exe.py
"""

import subprocess
import sys
import os

def gerar_exe():
    print("🔧 Instalando PyInstaller...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    
    print("\n📦 Gerando executável...")
    subprocess.check_call([
        sys.executable, '-m', 'pyinstaller',
        '--onefile',  # Um único arquivo
        '--windowed',  # Sem console
        '--name=ConsultaNF',  # Nome do executável
        '--icon=BUILT_IN',  # Ícone padrão
        'app_launcher.py'
    ])
    
    print("\n✅ Executável criado com sucesso!")
    print("📍 Localização: dist/ConsultaNF.exe")
    print("\nVocê pode:")
    print("1. Executar diretamente: dist/ConsultaNF.exe")
    print("2. Criar um atalho no Desktop")
    print("3. Distribuir para seus colegas")

if __name__ == '__main__':
    gerar_exe()

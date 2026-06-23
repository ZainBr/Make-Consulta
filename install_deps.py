#!/usr/bin/env python
import subprocess
import sys

packages = ['pdfplumber', 'pandas', 'streamlit', 'xlsxwriter']

for package in packages:
    print(f"Instalando {package}...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
    print(f"✓ {package} instalado com sucesso!\n")

print("Todas as dependências foram instaladas!")

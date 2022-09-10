from rest_framework import serializers
from . import read_file
import os
from pathlib import Path

file_path = os.path.join(Path(__file__).resolve().parent.parent.parent, 'file.vcf')
read_file.read_vcf(file_path)

# class FileSerializer(serializers.)
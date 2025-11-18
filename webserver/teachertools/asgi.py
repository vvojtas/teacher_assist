"""
ASGI config for teachertools project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import sys
from pathlib import Path

# Add project root to Python path so 'common' package can be imported
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teachertools.settings')

application = get_asgi_application()

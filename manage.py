#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import logging

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('django_management.log', encoding='utf-8')
        ]
    )
    logger = logging.getLogger(__name__)
    
    # Add log recording
    logger.info('Starting Django management command')
    if 'createsuperuser' in sys.argv:
        logger.info('Creating superuser...')
    
    execute_from_command_line(sys.argv)
    
    # Add log recording
    logger.info('Django management command completed')

if __name__ == '__main__':
    main()

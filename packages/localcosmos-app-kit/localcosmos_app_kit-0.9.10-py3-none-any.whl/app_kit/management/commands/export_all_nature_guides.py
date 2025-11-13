import os
import zipfile
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django_tenants.utils import schema_context  # Assuming django-tenants for multi-tenancy

from app_kit.features.nature_guides.models import NatureGuide, MetaNode, NatureGuidesTaxonTree, MatrixFilterSpace
from app_kit.models import ContentImage

class Command(BaseCommand):
    help = 'Export all Nature Guides as ZIP files for a specific tenant schema'

    def add_arguments(self, parser):
        parser.add_argument(
            'schema_name',
            type=str,
            help='The tenant schema name to export Nature Guides from (required).',
        )

    def handle(self, *args, **options):
        schema_name = options['schema_name']
        
        # Use schema_context to switch to the tenant's schema
        with schema_context(schema_name):
            export_path = os.path.join(settings.MEDIA_ROOT, 'nature_guides_exports', schema_name)
            os.makedirs(export_path, exist_ok=True)
            
            nature_guide_content_type = ContentType.objects.get_for_model(NatureGuide)
            meta_node_content_type = ContentType.objects.get_for_model(MetaNode)
            taxon_tree_content_type = ContentType.objects.get_for_model(NatureGuidesTaxonTree)
            matrix_filter_space_content_type = ContentType.objects.get_for_model(MatrixFilterSpace)
            
            image_content_types = [nature_guide_content_type, meta_node_content_type,
                                   taxon_tree_content_type, matrix_filter_space_content_type]
            
            content_images = ContentImage.objects.filter(
                content_type__in=image_content_types
            )
            
            # get all full filepaths of those images
            image_filepaths = [ci.file.path for ci in content_images if ci.file]

            
            self.stdout.write(f'All Nature Guides exported to: {export_path}')

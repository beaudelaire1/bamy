from django.core.management.base import BaseCommand
class Command(BaseCommand):
    def add_arguments(self,parser): parser.add_argument('file')
    def handle(self,*a,**k): print('import promo catalog')

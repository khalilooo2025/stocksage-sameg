"""
Commande de demarrage - cree les donnees initiales.
Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Cree les donnees initiales (admin, entrepot principal)'

    def handle(self, *args, **options):
        self.stdout.write('Initialisation de StockSage...')

        # Creer l'admin
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@stocksage.local',
                password='admin123',
                first_name='Admin',
                last_name='StockSage',
                role='admin',
            )
            self.stdout.write(self.style.SUCCESS('  [OK] Utilisateur admin cree (admin / admin123)'))
        else:
            self.stdout.write('  [-] Utilisateur admin deja existant')

        # Creer l'entrepot principal
        from apps.stock.models import Warehouse
        if not Warehouse.objects.filter(warehouse_type='main').exists():
            Warehouse.objects.create(
                name='Stock Principal',
                code='MAIN',
                warehouse_type='main',
            )
            self.stdout.write(self.style.SUCCESS('  [OK] Entrepot principal cree'))
        else:
            self.stdout.write('  [-] Entrepot principal deja existant')

        # Creer quelques categories de demonstration
        from apps.products.models import Category
        categories = [
            ('ELEC', 'Electrique'),
            ('PLOMB', 'Plomberie'),
            ('CLIM', 'Climatisation'),
            ('OUTIL', 'Outillage'),
            ('CONSOM', 'Consommables'),
        ]
        for code, name in categories:
            Category.objects.get_or_create(code=code, defaults={'name': name})
        self.stdout.write(self.style.SUCCESS(f'  [OK] {len(categories)} categories creees'))

        self.stdout.write(self.style.SUCCESS('\nStockSage initialise avec succes !'))
        self.stdout.write('  -> Connexion : http://localhost:8000/')
        self.stdout.write('  -> Admin : admin / admin123')

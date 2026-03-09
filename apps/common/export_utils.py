"""Utilitaires d'exportation et importation de donnees."""
import csv
import unicodedata
from io import StringIO
from decimal import Decimal, InvalidOperation
from datetime import datetime

from django.http import HttpResponse
from django.template.loader import render_to_string

try:
    from weasyprint import HTML
except Exception:  # pragma: no cover - dependance optionnelle en execution
    HTML = None


def _resolve_field(obj, field_path):
    """
    Resout un chemin de champ avec __ (ex: 'warehouse__name').
    Traverse les relations Django et les proprietes.
    """
    parts = field_path.split('__')
    current = obj
    for part in parts:
        if current is None:
            return ''
        try:
            current = getattr(current, part, None)
        except Exception:
            return ''
    if current is None:
        return ''
    return current


def _format_export_value(value):
    """Formate une valeur pour export CSV/PDF."""
    if isinstance(value, Decimal):
        return f"{value:.2f}"
    if isinstance(value, datetime):
        return value.strftime('%d/%m/%Y %H:%M')
    if hasattr(value, 'strftime'):
        return value.strftime('%d/%m/%Y')
    if isinstance(value, bool):
        return 'Oui' if value else 'Non'
    if value is None:
        return ''
    return str(value)


def export_to_csv(queryset, fields, headers, filename):
    """
    Exporte un queryset en CSV.

    Args:
        queryset: QuerySet Django
        fields: Liste des chemins de champs (ex: 'warehouse__name')
        headers: Liste des en-tetes lisibles
        filename: Nom du fichier CSV
    """
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    response.write('\ufeff')  # BOM UTF-8 pour Excel

    writer = csv.writer(response, delimiter=';')
    writer.writerow(headers)

    for obj in queryset:
        row = []
        for field in fields:
            value = _resolve_field(obj, field)
            row.append(_format_export_value(value))
        writer.writerow(row)

    return response


def export_to_pdf(queryset, fields, headers, filename, title):
    """Exporte un queryset en PDF tabulaire."""
    if HTML is None:
        return HttpResponse(
            "Export PDF indisponible: WeasyPrint n'est pas installe.",
            status=500,
            content_type='text/plain; charset=utf-8',
        )

    rows = []
    for obj in queryset:
        rows.append([_format_export_value(_resolve_field(obj, field)) for field in fields])

    html = render_to_string('reports/export_table_pdf.html', {
        'title': title,
        'headers': headers,
        'rows': rows,
        'generated_at': datetime.now().strftime('%d/%m/%Y %H:%M'),
    })
    pdf_bytes = HTML(string=html).write_pdf()

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    return response


def _export_by_format(queryset, fields, headers, filename, title, file_format='csv'):
    if file_format == 'pdf':
        return export_to_pdf(queryset, fields, headers, filename, title)
    return export_to_csv(queryset, fields, headers, filename)


# ---------------------- EXPORT FUNCTIONS ----------------------


def export_products_export(products, file_format='csv'):
    """Exporte les produits en CSV ou PDF."""
    return _export_by_format(
        products,
        fields=['code', 'designation', 'category__name', 'unit', 'unit_price_ht', 'min_stock_level', 'is_active'],
        headers=['Code', 'Designation', 'Categorie', 'Unite', 'Prix Unitaire HT', 'Seuil Stock Min', 'Actif'],
        filename=f'produits_{datetime.now().strftime("%Y%m%d")}',
        title='Produits',
        file_format=file_format,
    )


def export_clients_export(clients, file_format='csv'):
    """Exporte les clients en CSV ou PDF."""
    return _export_by_format(
        clients,
        fields=['code', 'name', 'contact_person', 'email', 'phone', 'address', 'city', 'is_active'],
        headers=['Code', 'Nom', 'Contact', 'Email', 'Telephone', 'Adresse', 'Ville', 'Actif'],
        filename=f'clients_{datetime.now().strftime("%Y%m%d")}',
        title='Clients',
        file_format=file_format,
    )


def export_suppliers_export(suppliers, file_format='csv'):
    """Exporte les fournisseurs en CSV ou PDF."""
    return _export_by_format(
        suppliers,
        fields=['code', 'name', 'contact_person', 'email', 'phone', 'address', 'city', 'is_active'],
        headers=['Code', 'Nom', 'Contact', 'Email', 'Telephone', 'Adresse', 'Ville', 'Actif'],
        filename=f'fournisseurs_{datetime.now().strftime("%Y%m%d")}',
        title='Fournisseurs',
        file_format=file_format,
    )


def export_stock_export(stock_balances, file_format='csv'):
    """Exporte le stock en CSV ou PDF."""
    return _export_by_format(
        stock_balances,
        fields=['warehouse__name', 'product__code', 'product__designation', 'quantity'],
        headers=['Entrepot', 'Code Produit', 'Designation', 'Quantite'],
        filename=f'stock_{datetime.now().strftime("%Y%m%d")}',
        title='Stock',
        file_format=file_format,
    )


def export_deliveries_export(deliveries, file_format='csv'):
    """Exporte les BL clients en CSV ou PDF."""
    return _export_by_format(
        deliveries,
        fields=['number', 'delivery_date', 'client__name', 'technician__full_name',
                'order_number', 'intervention_details', 'status', 'notes'],
        headers=['Numero BL', 'Date', 'Client', 'Technicien',
                 'N Ordre', 'Details Intervention', 'Statut', 'Notes'],
        filename=f'livraisons_clients_{datetime.now().strftime("%Y%m%d")}',
        title='BL Clients',
        file_format=file_format,
    )


def export_invoices_export(invoices, file_format='csv'):
    """Exporte les factures fournisseur en CSV ou PDF."""
    return _export_by_format(
        invoices,
        fields=['number', 'invoice_date', 'supplier__name', 'status', 'notes'],
        headers=['Numero', 'Date Facture', 'Fournisseur', 'Statut', 'Notes'],
        filename=f'factures_fournisseur_{datetime.now().strftime("%Y%m%d")}',
        title='Factures Fournisseur',
        file_format=file_format,
    )


def export_stock_movement_history_export(movements, file_format='csv'):
    """Exporte l'historique des mouvements de stock en CSV ou PDF."""
    return _export_by_format(
        movements,
        fields=['created_at', 'warehouse__name', 'product__code', 'product__designation',
                'movement_type', 'quantity', 'direction', 'reference', 'created_by__full_name'],
        headers=['Date', 'Entrepot', 'Code Produit', 'Designation',
                 'Type Mouvement', 'Quantite', 'Direction', 'Reference', 'Par'],
        filename=f'historique_stock_{datetime.now().strftime("%Y%m%d")}',
        title='Historique Mouvements Stock',
        file_format=file_format,
    )


# ---------------------- IMPORT FUNCTIONS ----------------------


def _normalize_key(value):
    value = str(value or '').strip().lower().replace('_', ' ')
    value = ''.join(
        ch for ch in unicodedata.normalize('NFKD', value)
        if not unicodedata.combining(ch)
    )
    return ' '.join(value.split())


def _parse_bool(value, default=True):
    if value is None:
        return default
    val = str(value).strip().lower()
    if val in {'1', 'true', 'vrai', 'oui', 'yes', 'y', 'active', 'actif'}:
        return True
    if val in {'0', 'false', 'faux', 'non', 'no', 'n', 'inactive', 'inactif'}:
        return False
    return default


def _parse_decimal(value):
    """Parse un nombre en tolerant espaces et separateurs locaux."""
    if value is None:
        return Decimal('0')
    txt = str(value).strip().replace('\xa0', '').replace(' ', '')
    if not txt:
        return Decimal('0')

    if ',' in txt and '.' in txt:
        if txt.rfind(',') > txt.rfind('.'):
            txt = txt.replace('.', '').replace(',', '.')
        else:
            txt = txt.replace(',', '')
    else:
        txt = txt.replace(',', '.')

    try:
        return Decimal(txt)
    except (InvalidOperation, ValueError):
        raise ValueError(f"Valeur numerique invalide: {value}")


def _read_csv(file_obj):
    """Lit un fichier CSV uploade et retourne des lignes normalisees."""
    raw = file_obj.read()

    for encoding in ['utf-8-sig', 'utf-8', 'latin-1']:
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = raw.decode('latin-1')

    sample = text[:4096]
    delimiter = ';'
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=';,|\t,')
        delimiter = dialect.delimiter
    except csv.Error:
        pass

    reader = csv.DictReader(StringIO(text), delimiter=delimiter)
    for row in reader:
        normalized = {}
        for key, val in row.items():
            if key is None:
                continue
            normalized[_normalize_key(key)] = val.strip() if isinstance(val, str) else val
        yield normalized


def _get(row, *keys, default=''):
    """Cherche une valeur dans un dict CSV avec plusieurs cles possibles."""
    for key in keys:
        val = row.get(_normalize_key(key))
        if val is not None and str(val).strip():
            return str(val).strip()
    return default


def import_csv_products(file_obj):
    """Importe des produits depuis un fichier CSV."""
    from apps.products.models import Product, Category

    reader = _read_csv(file_obj)
    imported = 0
    errors = []

    for row_num, row in enumerate(reader, start=2):
        try:
            designation = _get(row, 'Designation', 'designation', 'nom')
            if not designation:
                continue

            code = _get(row, 'Code', 'code')
            if not code:
                errors.append(f"Ligne {row_num}: Code manquant pour '{designation}'")
                continue

            category = None
            cat_name = _get(row, 'Categorie', 'categorie', 'category')
            if cat_name:
                base_code = ''.join(ch for ch in cat_name.upper().replace(' ', '_') if ch.isalnum() or ch == '_')[:20] or 'CATEGORIE'
                category = Category.objects.filter(name__iexact=cat_name).first()
                if not category:
                    code_candidate = base_code
                    idx = 1
                    while Category.objects.filter(code=code_candidate).exists():
                        suffix = str(idx)
                        code_candidate = f"{base_code[:20-len(suffix)]}{suffix}"
                        idx += 1
                    category = Category.objects.create(name=cat_name, code=code_candidate)

            unit = _get(row, 'Unite', 'unite', 'unit', default='pce')
            price_str = _get(row, 'Prix Unitaire HT', 'prix_unitaire_ht', 'unit_price_ht', default='0')
            price = _parse_decimal(price_str)
            min_stock = _get(row, 'Seuil Stock Min', 'seuil stock min', 'min_stock_level', default='5')
            try:
                min_stock_value = max(0, int(float(str(min_stock).replace(',', '.'))))
            except ValueError:
                min_stock_value = 5
            is_active = _parse_bool(_get(row, 'Actif', 'is_active', default='oui'), default=True)

            Product.objects.update_or_create(
                code=code,
                defaults={
                    'designation': designation,
                    'category': category,
                    'unit': unit,
                    'unit_price_ht': price,
                    'min_stock_level': min_stock_value,
                    'is_active': is_active,
                }
            )
            imported += 1
        except Exception as e:
            errors.append(f"Ligne {row_num}: {str(e)}")

    return imported, errors


def import_csv_clients(file_obj):
    """Importe des clients depuis un fichier CSV."""
    from apps.clients.models import Client

    reader = _read_csv(file_obj)
    imported = 0
    errors = []

    for row_num, row in enumerate(reader, start=2):
        try:
            name = _get(row, 'Nom', 'nom', 'name', 'designation')
            if not name:
                continue

            code = _get(row, 'Code', 'code')
            if not code:
                errors.append(f"Ligne {row_num}: Code manquant pour '{name}'")
                continue

            Client.objects.update_or_create(
                code=code,
                defaults={
                    'name': name,
                    'contact_person': _get(row, 'Contact', 'contact_person'),
                    'email': _get(row, 'Email', 'email'),
                    'phone': _get(row, 'Telephone', 'telephone', 'phone'),
                    'address': _get(row, 'Adresse', 'adresse', 'address'),
                    'city': _get(row, 'Ville', 'ville', 'city'),
                    'is_active': _parse_bool(_get(row, 'Actif', 'is_active', default='oui'), default=True),
                }
            )
            imported += 1
        except Exception as e:
            errors.append(f"Ligne {row_num}: {str(e)}")

    return imported, errors


def import_csv_suppliers(file_obj):
    """Importe des fournisseurs depuis un fichier CSV."""
    from apps.suppliers.models import Supplier

    reader = _read_csv(file_obj)
    imported = 0
    errors = []

    for row_num, row in enumerate(reader, start=2):
        try:
            name = _get(row, 'Nom', 'nom', 'name', 'designation')
            if not name:
                continue

            code = _get(row, 'Code', 'code')
            if not code:
                errors.append(f"Ligne {row_num}: Code manquant pour '{name}'")
                continue

            Supplier.objects.update_or_create(
                code=code,
                defaults={
                    'name': name,
                    'contact_person': _get(row, 'Contact', 'contact_person'),
                    'email': _get(row, 'Email', 'email'),
                    'phone': _get(row, 'Telephone', 'telephone', 'phone'),
                    'address': _get(row, 'Adresse', 'adresse', 'address'),
                    'city': _get(row, 'Ville', 'ville', 'city'),
                    'is_active': _parse_bool(_get(row, 'Actif', 'is_active', default='oui'), default=True),
                }
            )
            imported += 1
        except Exception as e:
            errors.append(f"Ligne {row_num}: {str(e)}")

    return imported, errors


# Compatibilite retroactive si d'autres modules importent les anciens noms.
export_products_csv = export_products_export
export_clients_csv = export_clients_export
export_suppliers_csv = export_suppliers_export
export_stock_csv = export_stock_export
export_deliveries_csv = export_deliveries_export
export_invoices_csv = export_invoices_export
export_stock_movement_history_csv = export_stock_movement_history_export

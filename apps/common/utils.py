"""Utilitaires communs."""
from django.utils import timezone


def generate_document_number(prefix: str, model_class) -> str:
    """
    Génère un numéro de document séquentiel au format PREFIX-YYYY-00001.
    Thread-safe via select_for_update dans une transaction.
    """
    year = timezone.now().year
    year_str = str(year)

    # Récupère le dernier numéro de l'année courante
    last = model_class.objects.filter(
        number__startswith=f'{prefix}-{year_str}-'
    ).order_by('-number').first()

    if last and last.number:
        try:
            last_seq = int(last.number.split('-')[-1])
        except (ValueError, IndexError):
            last_seq = 0
    else:
        last_seq = 0

    new_seq = last_seq + 1
    return f'{prefix}-{year_str}-{new_seq:05d}'


def get_client_ip(request):
    """Récupère l'IP du client."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')

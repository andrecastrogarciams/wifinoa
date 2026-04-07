from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta
from .models import ActiveSession, Voucher, UserMacMapping, AuditLog, RadAcct

def get_dashboard_metrics():
    """
    Calcula as métricas para o dashboard administrativo customizado.
    """
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # 1. KPI Cards
    total_users = UserMacMapping.objects.count()
    active_vouchers = Voucher.objects.filter(expires_at__gt=now, is_revoked=False).count()
    active_sessions = ActiveSession.objects.count()
    
    # Simulação de crescimento/status (em um cenário real seria comparativo)
    metrics = {
        'total_users': total_users,
        'active_vouchers': active_vouchers,
        'active_sessions': active_sessions,
        'system_load': 24.8, # Placeholder ou calculado via OS
        'total_events_today': AuditLog.objects.filter(timestamp__gte=today_start).count(),
    }

    # 2. Dados para o Gráfico (Últimos 7 dias)
    graph_data = []
    graph_labels = []
    days_map = {0: 'SEG', 1: 'TER', 2: 'QUA', 3: 'QUI', 4: 'SEX', 5: 'SÁB', 6: 'DOM'}
    
    for i in range(6, -1, -1):
        day_date = (now - timedelta(days=i)).date()
        count = RadAcct.objects.filter(acctstarttime__date=day_date).count()
        graph_labels.append(days_map[day_date.weekday()])
        graph_data.append(count)

    metrics['graph_labels'] = graph_labels
    metrics['graph_data'] = graph_data

    # 3. Últimos Acessos (Tabela)
    # Pegamos os últimos registros de accounting
    latest_accesses = RadAcct.objects.all().order_by('-acctstarttime')[:5]
    metrics['latest_accesses'] = latest_accesses

    return metrics

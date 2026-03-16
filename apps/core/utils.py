"""
Helper functions for staff lookup from custom accounts table
"""

from django.db import connection


def get_current_staff(user):
    """
    Lấy đối tượng Staff từ username
    
    Args:
        user: Django User object
    
    Returns:
        Staff object hoặc None
    """
    from apps.staff.models import Staff
    from django.db.models import Q
    
    if not user or not user.is_authenticated:
        return None
    
    # Nếu user là superuser
    if user.is_superuser:
        return None
    
    # Cách 1: Tìm từ accounts table (accounts custom)
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT s.id, s.name, s.role, s.phone, s.email
                FROM staff s
                JOIN accounts a ON s.id = a.staff_id
                WHERE a.username = %s AND a.is_active = True
                LIMIT 1
            """, [user.username])
            
            result = cursor.fetchone()
            if result:
                staff_id = result[0]
                return Staff.objects.get(id=staff_id)
    except Exception:
        pass
    
    # Cách 2: Fallback - tìm từ email hoặc phone (cho Django User)
    try:
        staff = Staff.objects.filter(
            Q(email__iexact=user.username) |
            Q(phone__iexact=user.username) |
            Q(email__iexact=user.email) if user.email else Q(),
            is_active=True
        ).first()
        
        if staff:
            return staff
    except Exception:
        pass
    
    return None

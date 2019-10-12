VARIETALS = [
    ('1', 'Malbec'),
    ('2', 'Cabernet Sauvignon'),
    ('3', 'Chardonnay'),
    ('4', 'Merlot'),
    ('5', 'Other'),
]

RESERVATION_CREATED = 1
RESERVATION_CONFIRMED = 2
RESERVATION_REJECTED = 3
RESERVATION_CANCELLED = 4
RESERVATION_PAIDOUT = 5

RESERVATION_STATUS = [
    (RESERVATION_CREATED, 'Created'),
    (RESERVATION_CONFIRMED, 'Confirmed'),
    (RESERVATION_REJECTED, 'Rejected'),
    (RESERVATION_CANCELLED, 'Cancelled'),
    (RESERVATION_PAIDOUT, 'Paid Out'),
]

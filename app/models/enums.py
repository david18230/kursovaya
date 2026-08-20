from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    def can_transition_to(self, new_status):
        if self == BookingStatus.PENDING  and (new_status == BookingStatus.CONFIRMED
                                   or new_status == BookingStatus.CANCELLED):
            return True
        elif  self == BookingStatus.CONFIRMED and new_status == BookingStatus.CANCELLED:
            return True
        else:
            return False

class RoomType(str, Enum):
    STANDART = "standart"
    LUX = "lux"
    FAMILY = "family"
    PRESIDENT = "president"



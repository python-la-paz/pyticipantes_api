from datetime import datetime
from typing import List, Tuple

from app.models import Event, EventRegister, EventRegisterInDB
from app.services.bl.user import UserProfileService
from app.services.event import EventService
from app.utils import PyObjectId


class EventRegistration:
    """Service for EVENTS in database operations"""

    @classmethod
    def list_public_events(
        cls, page_number: int = 0, n_per_page: int = 100
    ) -> List[Event]:
        finds = EventService.list_public_events(
            page_number=page_number, n_per_page=n_per_page
        )
        return finds
    
    @classmethod
    def get_public_event(cls, id: PyObjectId) -> Event:
        finds = EventService.get_public_event(id)
        return finds

    @classmethod
    def register_in_event(
        cls,
        id: PyObjectId,
        username: str,
        document_upload: str | None,
        additional_info: List[str],
    ) -> Tuple[EventRegisterInDB | None, str]:
        user = UserProfileService.get_public_user(username)
        if user is None:
            return None, "User not found"

        if not user.data_complete:
            return None, "User data not complete"

        event = EventService.get_public_no_finished(id=id)
        if event is None:
            return None, "Event not found"

        if event.date < datetime.now():
            return None, "Event already finished"

        full, seat = EventService.is_full(event)
        if full:
            return None, "Event full"

        already = EventService.is_already_registered(event, user.id)
        if already:
            return None, "User already registered"

        if event.document_required and not document_upload:
            return None, "Document required"

        if event.additional_info and not additional_info:
            return None, "Additional info required"

        register = EventRegisterInDB(
            event=event.id,
            user=user.id,
            date=datetime.now(),
            seat=seat + 1,
            status="pending" if event.automatic else "accepted",
            document_upload=document_upload if event.document_required else None,
            additional_info=additional_info if event.additional_info else [],
        )
        register = EventService.register_in_event(register)
        if register is None:
            return None, "Error registering"
        return register, "Success"

    @classmethod
    def get_registers(cls, id: PyObjectId, username: str) -> List[EventRegister]:
        user = UserProfileService.get_public_user(username)
        if not user:
            return []
        registers = EventService.get_registers(id,user.id)
        return registers
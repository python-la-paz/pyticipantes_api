from datetime import datetime
from typing import List, Tuple

from fastapi import UploadFile

from app.core.configuration import MAX_SIZE_IMAGE_MB
from app.models import Event, EventRegister, EventRegisterInDB
from app.models.event import FileBlob
from app.services.bl.user import UserProfileService
from app.services.event import EventService
from app.utils import PyObjectId, google_cloud_storage
from app.utils.content_types import CONTENT_TYPES_IMAGE, CONTENT_TYPES_VALID


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
        file: UploadFile,
        size_image: int,
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

        blob = None
        if event.document_required:
            if not file.content_type in CONTENT_TYPES_IMAGE:
                return (
                    False,
                    f"No valid content type, valid types: {','.join(CONTENT_TYPES_VALID)}",
                )

            if size_image > MAX_SIZE_IMAGE_MB * 1024 * 1024:
                return (
                    False,
                    f"Max size enabled: {MAX_SIZE_IMAGE_MB} MB",
                )

            result, filename, url, content_type = google_cloud_storage.upload_file(
                f"{event.id}-{user.id}", file.filename, file.content_type, file.file
            )
            # delete old image if exists after  upload new image

            if result:
                blob = FileBlob(name=filename, url=url, content_type=content_type)

        if event.additional_info and not additional_info:
            return None, "Additional info required"

        if len(additional_info) != len(event.additional_info):
            return None, "Responses are not complete"
        
        register = EventRegisterInDB(
            event=event.id,
            user=user.id,
            date=datetime.now(),
            seat=seat + 1,
            status="pending" if event.automatic else "accepted",
            document_upload=blob if event.document_required else None,
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
        registers = EventService.get_registers(id, user.id)
        return registers

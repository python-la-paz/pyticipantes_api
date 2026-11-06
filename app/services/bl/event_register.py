from datetime import datetime
from typing import List, Tuple

from fastapi import UploadFile

from app.core.configuration import MAX_SIZE_IMAGE_MB
from app.models import (Event, EventRegister, EventRegisterInDB, FileBlob,
                        StatusCode)
from app.models.event import REGISTRATION_TIMEZONE
from app.models.additional_info import AdditionalInfoAnswer
from app.services import SocialNetworkService
from app.services.bl.user import UserProfileService
from app.services.bl.additional_info import validate_additional_info
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
        additional_info: List[AdditionalInfoAnswer],
        rrss: str,
    ) -> Tuple[EventRegisterInDB | None, str, StatusCode]:
        user = UserProfileService.get_public_user(username)
        if user is None:
            return None, "User not found", StatusCode.USER_NOT_FOUND

        if not user.data_complete:
            return None, "User data not complete", StatusCode.USER_DATA_NOT_COMPLETE

        event = EventService.get_public_no_finished(id=id)
        if event is None:
            return None, "Event not found", StatusCode.EVENT_NOT_FOUND

        if event.registration_start is None or event.registration_end is None:
            return (
                None,
                "Registration dates not configured",
                StatusCode.EVENT_REGISTRATION_NOT_CONFIGURED,
            )

        now = datetime.now(REGISTRATION_TIMEZONE).replace(tzinfo=None)
        if now < event.registration_start:
            return (
                None,
                "Registration not started",
                StatusCode.EVENT_REGISTRATION_NOT_STARTED,
            )
        if now > event.registration_end:
            return (
                None,
                "Registration closed",
                StatusCode.EVENT_REGISTRATION_CLOSED,
            )

        full, seat = EventService.is_full(event)
        if full:
            return None, "Event full", StatusCode.EVENT_FULL

        already = EventService.is_already_registered(event, user.id)
        if already:
            return None, "User already registered", StatusCode.USER_ALREADY_REGISTERED

        validation_error = validate_additional_info(event.additional_info, additional_info)
        if validation_error is not None:
            message, code = validation_error
            return None, message, code

        blob = None
        if event.document_required:
            if not file.content_type in CONTENT_TYPES_IMAGE:
                return (
                    False,
                    f"No valid content type, valid types: {','.join(CONTENT_TYPES_VALID)}",
                    StatusCode.NO_VALID_CONTENT_TYPE,
                )

            if size_image > MAX_SIZE_IMAGE_MB * 1024 * 1024:
                return (
                    False,
                    f"Max size enabled: {MAX_SIZE_IMAGE_MB} MB",
                    StatusCode.MAX_SIZE_ENABLED,
                )

            result, filename, url, content_type = google_cloud_storage.upload_file(
                f"{event.id}-{user.id}", file.filename, file.content_type, file.file
            )
            # delete old image if exists after  upload new image

            if result:
                blob = FileBlob(name=filename, url=url, content_type=content_type)

        if not rrss:
            return None, "RRSS required", StatusCode.RRSS_REQUIRED
        social_network = SocialNetworkService.get(rrss)
        if social_network is None:
            return None, "Social network not found", StatusCode.RRSS_NOT_FOUND


        register = EventRegisterInDB(
            event=event.id,
            user=user.id,
            date=datetime.now(),
            seat=seat + 1,
            status="accepted" if event.automatic else "pending",
            document_upload=blob if event.document_required else None,
            additional_info=additional_info if event.additional_info else [],
            rrss=social_network.id,
        )
        register = EventService.register_in_event(register)
        if register is None:
            return None, "Error registering", StatusCode.ERROR_REGISTERING
        return register, "Success", StatusCode.REGISTER_COMPLETE

    @classmethod
    def get_registers(cls, id: PyObjectId, username: str) -> List[EventRegister]:
        user = UserProfileService.get_public_user(username)
        if not user:
            return []
        registers = EventService.get_registers(id, user.id)
        return registers

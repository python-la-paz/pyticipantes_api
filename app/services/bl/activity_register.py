from datetime import datetime
from typing import List, Tuple

from fastapi import UploadFile

from app.core.configuration import MAX_SIZE_IMAGE_MB
from app.models import (Activity, ActivityRegister, ActivityRegisterInDB, FileBlob,
                        StatusCode)
from app.models.registration import REGISTRATION_TIMEZONE

from app.services.bl.user import UserProfileService
from app.services.activity import ActivityService
from app.utils import PyObjectId, google_cloud_storage
from app.utils.content_types import CONTENT_TYPES_IMAGE, CONTENT_TYPES_VALID


class ActivityRegistration:
    """Service for ACTIVITIES in database operations"""
    @classmethod
    def list_public_activities(
        cls, page_number: int = 0, n_per_page: int = 100
    ) -> List[Activity]:
        finds = ActivityService.list_public_activities(
            page_number=page_number, n_per_page=n_per_page
        )
        return finds

    @classmethod
    def get_public_activity(cls, id: PyObjectId) -> Activity:
        finds = ActivityService.get_public_activity(id)
        return finds
    
    @classmethod
    def get_activities_by_event(cls, id: PyObjectId) -> List[Activity]:
        finds = ActivityService.get_activities_by_event(id)
        return finds
    
    @classmethod
    def register_in_activity(
        cls,
        id: PyObjectId,
        username: str,
        file: UploadFile,
        size_image: int,
        additional_info: List[str],
    ) -> Tuple[ActivityRegisterInDB | None, str, StatusCode]:
        user = UserProfileService.get_public_user(username)
        if user is None:
            return None, "User not found", StatusCode.USER_NOT_FOUND
        if not user.data_complete:
            return None, "User data not complete", StatusCode.USER_DATA_NOT_COMPLETE
        activity = ActivityService.get_public_not_finished(id = id)
        if activity is None:
            return None, "Activity not found", StatusCode.ACTIVITY_NOT_FOUND
        if activity.registration_start is None or activity.registration_end is None:
            return (
                None,
                "Registration dates not configured",
                StatusCode.ACTIVITY_REGISTRATION_NOT_CONFIGURED,
            )
        now = datetime.now(REGISTRATION_TIMEZONE).replace(tzinfo=None)
        if now < activity.registration_start:
            return (
                None,
                "Registration not started",
                StatusCode.ACTIVITY_REGISTRATION_NOT_STARTED,
            )
        if now > activity.registration_end:
            return (
                None,
                "Registration closed",
                StatusCode.ACTIVITY_REGISTRATION_CLOSED,
            )
        full, seat = ActivityService.is_full(activity)
        if full:
            return None, "Activity full", StatusCode.ACTIVITY_FULL
        already = ActivityService.is_already_registered(activity, user.id)
        if already:
            return None, "User already registered", StatusCode.USER_ALREADY_REGISTERED
        blob = None
        if activity.document_required:
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
                f"{activity.id}-{user.id}", file.filename, file.content_type, file.file
            )
            if result:
                blob = FileBlob(name=filename, url=url, content_type=content_type)
        if activity.additional_info and not additional_info:
            return None, "Additional info required", StatusCode.ADDITIONAL_INFO_REQUIRED
        if len(additional_info) != len(activity.additional_info):
            return None, "Responses are not complete", StatusCode.RESPONSES_NOT_COMPLETE
        register = ActivityRegisterInDB(
            activity=activity.id,
            user=user.id,
            date=datetime.now(),
            seat=seat + 1,
            status="accepted" if activity.automatic else "pending",
            document_upload=blob if activity.document_required else None,
            additional_info=additional_info if activity.additional_info else [],
        )
        register = ActivityService.register_in_activity(register)
        if register is None:
            return None, "Error registering", StatusCode.ERROR_REGISTERING
            
        return register, "Success", StatusCode.REGISTER_COMPLETE

    @classmethod
    def get_registers(cls, id: PyObjectId, username: str) -> List[ActivityRegister]:
        user = UserProfileService.get_public_user(username)
        if not user:
            return []
        registers = ActivityService.get_registers(id, user.id)
        return registers
    @classmethod
    def get_registers_by_event(cls, id: PyObjectId, username: str) -> List[ActivityRegister]:
        user = UserProfileService.get_public_user(username)
        if not user:
            return []
        
        activities = ActivityService.get_activities_by_event(id)      
        activities_ids = [activity.id for activity in activities]
        registers = ActivityService.get_registers_by_ids(activities_ids, user.id)
        return registers
    
    @classmethod
    def delete_register(cls, id: PyObjectId, username: str) -> Tuple[bool, str, StatusCode]:
        user = UserProfileService.get_public_user(username)
        if not user:
            return False, "User not found", StatusCode.USER_NOT_FOUND
        if not user.data_complete:
            return None, "User data not complete", StatusCode.USER_DATA_NOT_COMPLETE
        activity = ActivityService.get_public_not_finished(id = id)
        if activity is None:
            return None, "Activity not found", StatusCode.ACTIVITY_NOT_FOUND
        register = ActivityService.actual_registered(activity, user.id)
        if register is None:
            return False, "Register not found", StatusCode.REGISTER_NOT_FOUND
        if register.user != user.id:
            return False, "Register not found", StatusCode.REGISTER_NOT_FOUND
        
        ActivityService.delete_register(register.id)
        return True, "Success", StatusCode.REGISTER_COMPLETE
from typing import List

from app.models import Gender, Location, Profession, User, UserAPI, UserInDB
from app.services import (GenderService, LocationService, ProfessionService,
                          UserService)


class UserProfileService:

    @classmethod
    def get_public_user(cls, username: str) -> UserAPI | None:
        """Get public user profile by username

        Args:
            username (str): Username to search in database

        Returns:
            UserPublic | None: User found or None
        """
        find = UserService.get_user_by_username(username)
        if not find:
            return None
        find = UserAPI(**find.model_dump(by_alias=True))
        find.data_complete = cls.validate_data(find)
        return find

    @classmethod
    def validate_data(cls, user: UserAPI) -> bool:
        """Validate user additional data complete
        Args:
            user (UserAPI): User to validate
        Returns:
            bool: True if data is complete, False if not
        """
        if not user.birthday:
            return False
        if not user.gender:
            return False
        if not user.dni:
            return False
        if not user.profession:
            return False
        if not user.place_profession:
            return False
        if not user.residence:
            return False
        if not user.phone:
            return False
        return True

    @classmethod
    def update_user(cls, user: UserAPI) -> UserAPI | None:
        """Update user profile

        Args:
            user (UserAPI): User to update in database

        Returns:
            UserAPI | None: User updated or None
        """
        find = UserService.get_user_by_username(user.username)
        if not find:
            return None
        find.birthday = user.birthday
        find.gender = user.gender
        find.dni = user.dni
        find.profession = user.profession
        find.place_profession = user.place_profession
        find.residence = user.residence
        find.level_programming = user.level_programming
        find.phone = user.phone
        find.programming_languages = user.programming_languages

        validate_info = cls.validate_fields(find)
        if not validate_info:
            return None
        find.new = False
        updated = UserService.update_extra_info(find)
        if not updated:
            return None
        updated = UserAPI(**updated.model_dump(by_alias=True))
        updated.data_complete = cls.validate_data(updated)
        return updated

    @classmethod
    def validate_fields(cls, user: UserInDB) -> bool:
        """Validate user fields

        Args:
            user (UserInDB): User to validate

        Returns:
            bool: True if fields are valid, False if not
        """
        gender = GenderService.get(user.gender)
        if not gender:
            return False
        profession = ProfessionService.get(user.profession)
        if not profession:
            return False
        if user.level_programming < 0 or user.level_programming > 10:
            return False
        
        return True

    @classmethod
    def list_gender(cls) -> List[Gender]:
        """Get list of genders

        Returns:
            List of genders: List
        """
        return GenderService.list()
    
    @classmethod
    def list_profession(cls) -> List[Profession]:
        """Get list of professions

        Returns:
            List of professions: List
        """
        return ProfessionService.list()

    @classmethod
    def list_locations(cls) -> List[Location]:
        """Get list of locations

        Returns:
            List of locations: List
        """
        return LocationService.list()
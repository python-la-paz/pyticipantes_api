from typing import List
from fastapi import APIRouter, Depends, status

from app.auth.access import get_actual_user
from app.models import SocialNetwork, UserInDB, SocialNetworkInDB
from app.models.socialnetwork import SocialNetwork
from app.services import SocialNetworkService
from app.utils.mongo_validator import PyObjectId

router = APIRouter()


@router.get("", response_model=List[SocialNetwork], status_code=status.HTTP_200_OK)
async def get_social_networks(user: UserInDB = Depends(get_actual_user)):
    """Retrieve a list of social networks."""
    return SocialNetworkService.list()


@router.get("/{id}", response_model=SocialNetwork, status_code=status.HTTP_200_OK)
async def get_social_network_by_id(id: PyObjectId, user: UserInDB = Depends(get_actual_user)):
    """Retrieve a social network by ID."""
    social_network = SocialNetworkService.get(social_network_id=id)  # Cambié 'id' a 'social_network_id'
    if not social_network:
        raise HTTPException(status_code=404, detail="Social network not found") 
    return social_network


@router.post("", response_model=SocialNetwork, status_code=status.HTTP_201_CREATED)
async def create_social_network(social_network: SocialNetwork, user: UserInDB = Depends(get_actual_user)):
    """Create a new social network."""
    social_network_db = SocialNetworkInDB(**social_network.model_dump(by_alias=True))
    social_network_db.username_insert = user.username
    return SocialNetworkService.insert(item=social_network_db)


@router.put("/{id}", response_model=SocialNetwork, status_code=status.HTTP_200_OK)
async def update_social_network(
    id: PyObjectId, social_network: SocialNetwork, user: UserInDB = Depends(get_actual_user)
):
    """Update an existing social network."""
    social_network_db = SocialNetworkInDB(**social_network.model_dump(by_alias=True))
    social_network_db.id = id
    social_network_db.username_update = user.username
    return SocialNetworkService.update(item=social_network_db)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_social_network(id: PyObjectId, user: UserInDB = Depends(get_actual_user)):
    """Delete a social network by ID."""
    SocialNetworkService.delete(id=id)
    return None

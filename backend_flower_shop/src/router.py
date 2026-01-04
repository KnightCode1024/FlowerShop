from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_db_session
from schemas import UpdatePost, CreatePost
from service import PostService

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/")
async def get_all_posts(
    offset: int = Query(0, ge=0, description="Offset"),
    limit: int = Query(0, ge=0, description="Limit"),
    session: AsyncSession = Depends(get_db_session),
):
    post_service = PostService(session)
    return await post_service.get_all(offset, limit)


@router.get("/{post_id}/")
async def get_post_by_id(
    post_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    post_service = PostService(session)
    return await post_service.get_by_id(post_id)


@router.post("/")
async def add_post(
    post_data: CreatePost,
    session: AsyncSession = Depends(get_db_session),
):
    post_service = PostService(session)
    try:
        return await post_service.create_post(post_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create post. {e}",
        )


@router.patch("/{post_id}/")
async def update_post(
    post_id: int,
    post_data: UpdatePost,
    session: AsyncSession = Depends(get_db_session),
):
    post_service = PostService(session)
    try:
        post = await post_service.update_post(
            post_id,
            post_data,
        )

        if not post:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Post not found",
            )
        return post
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{e}",
        )


@router.delete("/{post_id}/")
async def delete_post(
    post_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    post_service = PostService(session)
    success = await post_service.delete_post(post_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    return {"message": "Post delete succsessfully"}

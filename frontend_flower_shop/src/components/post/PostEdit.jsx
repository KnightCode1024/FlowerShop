import { useContext } from "react"
import PostContex from "../../context/PostContex"

function PostEdit({post}) {
    const {editPost} = useContext(PostContex)

    return (
        <div>
            <span
            onClick={() => editPost(post)}
            className='cursor-pointer text-xs text-emerald-600'>Редактировать</span>
        </div>
    )
}

export default PostEdit
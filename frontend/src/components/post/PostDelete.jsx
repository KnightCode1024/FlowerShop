import PostContex from "../../context/PostContex"
import { useContext } from "react"

function PostDelete({post}) {
    const {deletePost} = useContext(PostContex)

    return (
        <div>
              <span
             onClick={() => deletePost(post)}
             className='cursor-pointer text-xs text-red-600'>Удалить</span>
        </div>
    )
}

export default PostDelete
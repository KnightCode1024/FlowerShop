import PostDelete from "./PostDelete"
import PostEdit from "./PostEdit"

function PostItem ({ post}) {

    return (
         <div key={post.index} className='flex justify-between items-center mb-4 w-1/2 mx-auto bg-white p-4 border border-gray-200'>
          <div>
            <h3 className='text-lg mb-2'>{post.title}</h3>
            <p  className='text-xs'>{post.content}</p>
          </div>
          <div>
            <PostDelete post={post}/>
            <PostEdit post={post}/>
          </div>
       </div>
    )
}

export default PostItem
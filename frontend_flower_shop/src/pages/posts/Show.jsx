import { useEffect, useState } from "react"
import axios from 'axios'
import { useParams, Link } from "react-router-dom"
import PostItem from "../../components/post/PostItem"

function PostShow() {

    const {id} = useParams()

    const [post, setPost] = useState({
        id: null,
        title: '',
        content: '',
    })

    const getPost = async () => {
        const base_url = `http://127.0.0.1:8000`
        const url = `${base_url}/posts/${id}`
        const res = await axios.get(url)
        setPost(res.data)
    }

    useEffect(() => {
        getPost()
    }, [])

    const deletePost = async (id) => {
        const res = await axios.delete(`http://127.0.0.1:8000/posts/${id}`)

        const newPost = posts.filter(PostItem => PostItem.id !== id)
        setPost(newPost)
    }

    return (
        <div>
            <div key={post.id} className="mb-4 bg-white p-4 border border-gray-200 w-full">
                <h3 className="text-lg mb-2">{post.title}</h3>
                <p className="text-xs">{post.content}</p>
            </div>
            <div className="mb-4">
                 <Link
                 to={`/posts/${post.id}/edit`}
                 className="inline-block px-3 py-2 bg-sky-600 border border-sky-700 text-white text-xs">
                Редактировать
                </Link>
            </div>
            <div className="mb-4">
                <a
                onClick={() => deletePost(post.id)}
                className="text-xs text-red-600">Удалить</a>
            </div>
        </div>
    )
}

export default PostShow
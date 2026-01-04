import { useEffect, useState } from "react"
import axios from 'axios'
import { Link } from "react-router-dom"

function Index() {

    const [posts, setPosts] = useState([])

    const getPosts = async () => {
        const offset = 0
        const limit = 20
        const base_url = `http://127.0.0.1:8000`
        const url = `${base_url}/posts/?offset=${offset}&limit=${limit}`
        const res = await axios.get(url)
        setPosts(res.data)
    }

    useEffect(() => {
        getPosts()
    }, [])

    return (
        <div>
            <div className="mb-4">
                <Link to={'/posts/create'} className="inline-block px-3 py-2 bg-sky-600 border border-sky-700 text-white text-xs">
                Создать пост
                </Link>
            </div>
            <div className="">
                {posts.map(
                post => (
                    <div key={post.id} className="flex justify-between items-center mb-4 bg-white p-4 border border-gray-200 w-full">
                        <h3 className="text-lg mb-2">
                            <Link to={`/posts/${post.id}`}>{post.title}</Link>
                            </h3>
                        <p className="text-xs">{post.content}</p>
                    </div>
                )
            )}
            </div>
        </div>
    )
}

export default Index
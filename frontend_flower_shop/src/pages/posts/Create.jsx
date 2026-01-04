import { useEffect, useState } from "react"
import axios from 'axios'
import { useParams } from "react-router-dom"

function PostCreate() {

    const [post, setPost] = useState({
        title: '',
        content: '',
    })

    const createPost = async(e) => {
        e.preventDefault()

        const res = await axios.post('http://127.0.0.1:8000/posts', post)
        console.log(res)

    }

    const handlePost = (e) => {
        const name = e.target.name
        const value = e.target.value

        setPost({...post, [name]: value})
    }


    return (
        <div>
            <div className="mb-4 bg-white p-4 border border-gray-200 w-full">
               <div className="mb-4">
                    <input
                        onChange={(e) => handlePost(e)}
                        value={post.title}
                        placeholder="Заголовок"
                        name="title"
                        type="text"
                        className="border border-gray-200 p-4 w-full"/>

               </div>
               <div className="mb-4">
                    <textarea
                        onChange={(e) => handlePost(e)}
                        value={post.content}
                        placeholder="Контент"
                        name="content"
                        className="border border-gray-200 p-4 w-full"/>
               </div>
               <div className="mb-4">
                    <a
                        onClick={(e) => createPost(e)}
                        className="inline-block px-3 py-2 bg-sky-600 border border-sky-700 text-white text-xs">
                        Создать
                    </a>
               </div>
            </div>
        </div>
    )
}

export default PostCreate
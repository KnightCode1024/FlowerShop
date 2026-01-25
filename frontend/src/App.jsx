import { useState, useEffect } from 'react'
import PostItem from './components/post/PostItem'
import PostContex from './context/PostContex'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import PostIndex from './pages/posts/Index'
import MainIndex from './pages/main/Index'
import PostShow from './pages/posts/Show'
import PostCreate from './pages/posts/Create'
import PostEdit from './pages/posts/Edit'

function App() {


  const [post, setPost] = useState({
    index: null,
    title: "",
    content: "",
  })

  const [editingPost, setEditingPost] = useState({
    index: null,
    title: "",
    content: "",
  })

  const [isModal, setIsModal] = useState(false)
  const [posts, setPosts] = useState([])
  const [errors, setErorrors] = useState([])

  const storePost = (e) => {
    e.preventDefault()

    if (validateFields().length > 0) {
      return
    }

    setPosts([...posts, post])
    setPost({
      title: "",
      content: "",
    })

  }

  const editPost = (post) => {
    setIsModal(true)
    setEditingPost({
      index: posts.indexOf(post),
      title: post.title,
      content: post.content,
    })
  }

  const updatePost = (e) => {
    const newPosts = posts.map((post, index) => {
      if (index === editingPost.index) {
        return {
          title: editingPost.title,
          content: editingPost.content,
        }
      }
      return post
    })

    setPosts(newPosts)
    setIsModal(false)

    e.preventDefault()
  }

  const deletePost = (post) => {
    const newPosts = posts.filter(postItem => postItem !== post)
    setPosts(newPosts)
  }

  const handlePost = (e) => {
    setErorrors([])
    const name = e.target.name
    const value = e.target.value
    setPost({...post, [name]: value

    })
  }

  const handleEditingPost = (e) => {
    const name = e.target.name
    const value = e.target.value
    setEditingPost({...editingPost, [name]: value})

  }

  const validateFields = () => {
    const newErrors = []

    if (post.title === '') {
      newErrors.push({"message": "title field is required"})
    }
    if (post.content === '') {
      newErrors.push({"message": "content field is required"})
    }

    if (newErrors.length > 0) {
      setErorrors(newErrors)
    }
    return newErrors
  }


  return (
    <>
      <Router>
        <div className='bg-white py-4 border-b border-gray-200 w-full'>
          <div className='w-1/2 mx-auto'>
            <Link className='mr-4' to={'/'}>Main</Link>
            <Link className='mr-4' to={'/posts'}>Posts</Link>
          </div>
        </div>


        <div className='bg-gray-50 min-h-screen'>
          <div className="w-1/2 mx-auto py-4">
            <Routes>
              <Route path={'/'} element={<MainIndex />}></Route>
              <Route path={'/posts'} element={<PostIndex />}></Route>
              <Route path={'/posts/:id'} element={<PostShow />}></Route>
              <Route path={'/posts/:id/edit'} element={<PostEdit />}></Route>
              <Route path={'/posts/create'} element={<PostCreate />}></Route>

            </Routes>
          </div>
        </div>
      </Router>
    </>
  )
}

export default App

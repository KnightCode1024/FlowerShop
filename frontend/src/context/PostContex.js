import React from "react";

const PostContext = React.createContext({
    deletePost: () => {},
    editPost: () => {},
    posts: [],
})

export default PostContext
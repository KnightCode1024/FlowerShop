import React, {Suspense, lazy, JSX} from 'react';
import {Routes, Route} from 'react-router-dom';
import Home from "./pages/Home.tsx";
import Layout from "./layouts/Layout.tsx";
import About from "./pages/About.tsx";


function App(): JSX.Element {
    return (
        <Routes>
            <Route path="/" element={<Layout/>}>
                <Route index element={<Home/>}/>
                <Route path={"/about"} element={<About/>}/>
            </Route>
        </Routes>
    );
}

export default App;

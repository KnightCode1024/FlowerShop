import React, { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";


const Navbar: React.FC = () => {

    return (
        <div className="sticky z-50 top-0 p-4 bg-white  flex flex-row w-full items-center justify-center p-4 border-b border-gray-800 pb-4">

            <a href="/" className="font-bold text-2xl w-full">Our Blooms R</a>

            <div className="flex flex-row flex-1 font-semibold gap-5 flex-1 ml-auto">
                <Link to="/gallery">GALLERY</Link>
                <Link to="/about">ABOUT</Link>
                <Link to="/contact">CONTACT</Link>
                <Link to="/login">LOGIN</Link>
                <Link to="/register">REGISTER</Link>
            </div>
        </div>
    );
};

export default Navbar;

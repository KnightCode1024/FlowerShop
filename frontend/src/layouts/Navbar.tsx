import React, { useEffect, useRef, useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";


const Navbar: React.FC = () => {

    return (
        <div className="flex flex-row w-full items-center justify-center p-4 border-b border-gray-800 pb-4">

            <a href="/" className="font-bold text-2xl w-full">Our Blooms R</a>

            <div className="flex flex-row flex-1 font-semibold gap-5 flex-1 ml-auto">
                <a href="/gallery">GALLERY</a>
                <a href="/about">ABOUT</a>
                <a href="/contact">CONTACT</a>
            </div>
        </div>
    );
};

export default Navbar;

import React from 'react';
import mainFlower from "../assets/images/main_flower.png";
import flower1 from "../assets/images/flower1.png";

import "../styles/App.css";


function Home(props) {
    return (
        <div className="flex flex-col gap-6 my-9">
            <div className="font-bold text-5xl sm:text-7xl md:text-9xl">
                Our Blooms R
            </div>

            <img src={mainFlower} alt="Main Image" className="image"/>

            <div className="flex flex-col gap-9 my-18 font-bold items-center">
                <p className="text-sm text-gray-500">Who We Are</p>
                <p className="text-3xl">We're Our Blooms® and we're here to help you find your floral story.</p>

                <a href="/about" className="p-3 flex flex-row items-center gap-3 bg-yellow-500 text-black items-center rounded">
                    <p>◾</p>
                    <p className="text-xl font-bold">ABOUT US</p>
                </a>
            </div>

            <div className="flex flex-col gap-9 ">
                <div className="flex flex-row gap-3">
                    <img src={flower1} alt="" className="image"/>
                    <img src={flower1} alt="" className="image"/>
                    <img src={flower1} alt="" className="image"/>
                    <img src={flower1} alt="" className="image"/>
                </div>

                <div className="flex flex-col gap-6 items-center">
                    <h1 className="text-4xl font-bold">What We Do</h1>
                    <h4 className="font-medium text-sm">We bring a touch of that simple magic into your world.</h4>
                </div>
            </div>

            <div className="flex flex-col gap-9">
                <div className="text-center p-6 flex flex-col gap-6 border-b border-t border-gray-700 pb-4">
                    <p className="text-3xl font-bold">1</p>
                    <img src="" alt="photo1"/>
                </div>
                <div className="text-center p-6 flex flex-col gap-6 border-b border-gray-700 pb-4">
                    <p className="text-3xl font-bold">2</p>
                    <img src="" alt="photo2"/>
                </div>
                <div className="text-center p-6 flex flex-col gap-6 border-b border-gray-700 pb-4">
                    <p className="text-3xl font-bold">3</p>
                    <img src="" alt="photo3"/>
                </div>
            </div>
        </div>


    );
}

export default Home;
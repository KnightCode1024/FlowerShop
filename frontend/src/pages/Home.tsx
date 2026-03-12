import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import mainFlower from "../assets/images/main_flower.png";
import { ApiError } from "../api/authApi";
import { getProducts, type ProductListItem } from "../api/catalogApi";
import ProductCard from "../components/ProductCard";

import "../styles/App.css";
import About from "../components/buttons/About.tsx";

    return () => {
      isActive = false;
    };
  }, []);

            <img src={mainFlower} alt="Main Image" className="image"/>

            <div className="flex flex-col gap-9 my-18 font-bold items-center">
                <p className="text-sm text-gray-500">Who We Are</p>
                <p className="text-3xl">We're Our Blooms® and we're here to help you find your floral story.</p>

                <About/>
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
                <div className="my-12 border-b border-t border-gray-700 pb-4">
                    <div className="my-18 text-center p-6 flex flex-col gap-6 ">
                        <p className="text-3xl font-bold">1</p>
                        <img src="" alt="photo1"/>
                        <h2 className="text-xl font-bold">FLORAL INSTALLATIONS</h2>
                        <h4 className="font-medium text-xs">Living art for homes, businesses, and events.</h4>
                    </div>
                </div>
                <div className="my-12 border-b border-t border-gray-700 pb-4">
                    <div className="my-18 text-center p-6 flex flex-col gap-6 ">
                        <p className="text-3xl font-bold">2</p>
                        <img src="" alt="photo1"/>
                        <h2 className="text-xl font-bold">FLORAL INSTALLATIONS</h2>
                        <h4 className="font-medium text-xs">Whether it’s a private retreat or a public space, we craft floral experiences that bloom
                            beyond expectations.</h4>
                    </div>
                </div>
                <div className="my-12 border-b border-t border-gray-700 pb-4">
                    <div className="my-18 text-center p-6 flex flex-col gap-6 ">
                        <p className="text-3xl font-bold">3</p>
                        <img src="" alt="photo1"/>
                        <h2 className="text-xl font-bold">CUSTOM FLORAL CONCEPTS</h2>
                        <h4 className="font-medium text-xs">Your vision, our blooms. We build arrangements that are both personal and exquisitely
                            simple. Whether it’s a private retreat or a public space, we craft floral experiences that bloom beyond expectations.</h4>
                    </div>
                </div>

                <img src={mainFlower} alt="Main Image" className="image"/>

                <div className="my-18">

                    <div className="flex flex-col gap-6"><h1>Work with us</h1>
                        <h1>Discover how we can add a touch of natural beauty to your next event</h1>
                        <About/></div>
                </div>

                <img src={mainFlower} alt="Main Image" className="image"/>

            </div>
        </div>

        {error ? (
          <p className="rounded bg-red-100 p-3 text-sm text-red-800">{error}</p>
        ) : null}

        {isLoading ? (
          <p className="py-6 text-center text-slate-500">Загрузка...</p>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

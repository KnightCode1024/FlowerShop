import { useEffect, useState } from "react";
import mainFlower from "../assets/images/main_flower.png";
import { ApiError } from "../api/authApi";
import { getProducts, type ProductListItem } from "../api/catalogApi";
import ProductCard from "../components/ProductCard";
import About from "../components/buttons/About.tsx";

import "../styles/App.css";

export default function Home() {
  const [products, setProducts] = useState<ProductListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;

    const loadProducts = async () => {
      try {
        const data = await getProducts({ offset: 0, limit: 8, in_stock: true });
        if (isActive) {
          setProducts(data);
        }
      } catch (err) {
        if (isActive) {
          setError(err instanceof ApiError ? err.message : "Не удалось загрузить товары");
        }
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    };

    loadProducts();

    return () => {
      isActive = false;
    };
  }, []);

  const services = [
    {
      number: "1",
      title: "FLORAL INSTALLATIONS",
      description: "Living art for homes, businesses, and events.",
    },
    {
      number: "2",
      title: "EVENT FLOWERS",
      description:
        "Whether it’s a private retreat or a public space, we craft floral experiences that bloom beyond expectations.",
    },
    {
      number: "3",
      title: "CUSTOM FLORAL CONCEPTS",
      description:
        "Your vision, our blooms. We build arrangements that are both personal and exquisitely simple.",
    },
  ];

  return (
    <section className="w-full">
      <div>
        <img src={mainFlower} alt="Main flower" className="image" />

        <div className="flex flex-col items-center gap-9 my-18 font-bold">
          <p className="text-sm text-gray-500">Who We Are</p>
          <p className="text-3xl text-center">
            We're Our Blooms® and we're here to help you find your floral story.
          </p>
          <About />
        </div>

        <div className="flex flex-col gap-9">
          <div className="flex flex-row gap-3 overflow-hidden">
            <img src={mainFlower} alt="Flower 1" className="image" />
            <img src={mainFlower} alt="Flower 2" className="image" />
            <img src={mainFlower} alt="Flower 3" className="image" />
            <img src={mainFlower} alt="Flower 4" className="image" />
          </div>

          <div className="flex flex-col items-center gap-6">
            <h1 className="text-4xl font-bold">What We Do</h1>
            <h4 className="font-medium text-sm text-center">
              We bring a touch of that simple magic into your world.
            </h4>
          </div>
        </div>

        <div className="flex flex-col gap-9">
          {services.map((service) => (
            <div key={service.number} className="my-12 border-b border-t border-gray-700 pb-4">
              <div className="my-18 flex flex-col gap-6 p-6 text-center">
                <p className="text-3xl font-bold">{service.number}</p>
                <img src={mainFlower} alt={service.title} className="mx-auto w-48" />
                <h2 className="text-xl font-bold">{service.title}</h2>
                <h4 className="font-medium text-xs">{service.description}</h4>
              </div>
            </div>
          ))}

          <img src={mainFlower} alt="Main flower" className="image" />

          <div className="my-18">
            <div className="flex flex-col gap-6">
              <h1 className="text-2xl font-bold">Work with us</h1>
              <h2 className="text-lg">
                Discover how we can add a touch of natural beauty to your next event
              </h2>
              <About />
            </div>
          </div>

          <img src={mainFlower} alt="Main flower" className="image" />
        </div>

        {error ? (
          <p className="my-3 rounded bg-red-100 p-3 text-sm text-red-800">{error}</p>
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
      </div>
    </section>
  );
}
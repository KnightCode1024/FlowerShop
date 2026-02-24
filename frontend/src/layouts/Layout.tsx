import React from "react";
import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";
import Footer from "./Footer";

const Layout: React.FC = () => {
    return (
        <div className="flex flex-col mx-auto min-h-screen max-w-screen-lg">
            <Navbar />

            <main className="flex-1 overflow-auto p-3">
                <div className="w-full h-full">
                    <Outlet />
                </div>
            </main>

            <Footer />
        </div>
    );
};

export default Layout;

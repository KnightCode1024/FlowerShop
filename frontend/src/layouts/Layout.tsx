import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";
import Footer from "./Footer";

export default function Layout() {
  return (
    <div className="mx-auto flex min-h-screen max-w-screen-lg flex-col">
      <Navbar />

      <main className="flex-1 overflow-auto p-3">
        <div className="h-full w-full">
          <Outlet />
        </div>
      </main>

      <Footer />
    </div>
  );
}

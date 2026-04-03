import { Outlet } from "react-router";
import Header from "./Header";
import SystemInfo from "./SystemInfo";

export default function Root() {
  return (
    <div className="h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 flex flex-col">
      <Header />
      <SystemInfo />
      <main className="flex-1 overflow-hidden">
        <Outlet />
      </main>
    </div>
  );
}

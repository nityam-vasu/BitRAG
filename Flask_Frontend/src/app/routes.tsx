import { createBrowserRouter } from "react-router";
import { ChatPage } from "./pages/ChatPage";
import { SettingsPage } from "./pages/SettingsPage";
import { DocumentsPage } from "./pages/DocumentsPage";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: ChatPage,
  },
  {
    path: "/settings",
    Component: SettingsPage,
  },
  {
    path: "/documents",
    Component: DocumentsPage,
  },
]);

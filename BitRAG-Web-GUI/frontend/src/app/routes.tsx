import { createBrowserRouter } from "react-router";
import { ChatPage } from "./pages/ChatPage";
import { SettingsPage } from "./pages/SettingsPage";
import { DocumentsPage } from "./pages/DocumentsPage";
import { GraphPage } from "./pages/GraphPage";

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
  {
    path: "/graph",
    Component: GraphPage,
  },
], {
  // Prevent full page refresh on navigation
  future: {
    v7_fetcherPersist: true,
    v7_relativeSplatPath: true,
    v7_prependFutureBasePath: true,
  },
});

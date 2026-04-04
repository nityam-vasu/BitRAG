import { createBrowserRouter } from "react-router";
import Root from "./components/Root";
import ChatPage from "./pages/ChatPage";
import DocumentsPage from "./pages/DocumentsPage";
import GraphPageEnhanced from "./pages/GraphPageEnhanced";
import SettingsPage from "./pages/SettingsPage";
import OllamaParamsPage from "./pages/OllamaParamsPage";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Root,
    children: [
      { index: true, Component: ChatPage },
      { path: "documents", Component: DocumentsPage },
      { path: "graph", Component: GraphPageEnhanced },
      { path: "ollama-params", Component: OllamaParamsPage },
      { path: "settings", Component: SettingsPage },
    ],
  },
]);
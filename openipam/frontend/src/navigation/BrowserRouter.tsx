import React from "react";
import {
  RouteObject,
  RouterProvider,
  createHashRouter,
} from "react-router-dom";
import { Main } from "../Main";
import { Navigation } from "./Navigation";
import "../styles/index.css";
import { Domains } from "../modules/domains";
import { Hosts } from "../modules/hosts";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { NotFoundPage } from "../components/NotFoundPage";

const routes: RouteObject[] = [
  {
    path: "",
    element: <Navigation />, //change to Navigation element
    errorElement: <NotFoundPage />,
    children: [
      {
        path: "",
        element: <Main />,
      },
      {
        path: "hosts",
        element: <Hosts />, //HostLayout
      },
      {
        path: "domains",
        // element: <></>, //DomainLayout
        children: [
          {
            path: "",
            element: <Domains />,
          },
          {
            path: ":domain",
            lazy: async () => {
              const { DomainPage: Domain } = await import("../modules/domain");
              return {
                element: <Domain />,
              };
            },
          },
        ],
      },
      {
        path: "admin",
        // element: <></>, //AdminLayout
        children: [
          {
            path: "logs",
            lazy: async () => {
              const { Logs } = await import("../modules/logs");
              return {
                element: <Logs />,
              };
            },
          },
        ],
      },
    ],
  },
];

const router = createHashRouter(routes, {
  basename: "/",
  future: {
    v7_normalizeFormMethod: true,
  },
});

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      cacheTime: 5 * 60 * 1000,
      staleTime: 5 * 60 * 1000,
    },
  },
});

export const App = () => {
  return (
    <React.StrictMode>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>
    </React.StrictMode>
  );
};

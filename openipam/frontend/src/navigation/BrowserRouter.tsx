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

const routes: RouteObject[] = [
  {
    path: "",
    element: <Navigation />, //change to Navigation element
    errorElement: <div>TODO: create 404 page</div>,
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
        element: <Domains />, //DomainLayout
        children: [
          {
            path: ":domain",
            lazy: async () => {
              const { DnsRecords } = await import("../components/DnsRecords");
              return {
                element: <DnsRecords />,
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

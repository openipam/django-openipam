import React from "react";
import {
  RouteObject,
  RouterProvider,
  createHashRouter,
} from "react-router-dom";
import { Navigation } from "./Navigation";
import "../styles/index.css";
import { Domains } from "../modules/domains";
import { Hosts } from "../modules/hosts";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { NotFoundPage } from "../components/NotFoundPage";
import { Networks } from "../modules/networks";
import { Profile } from "../modules/profile";

const routes: RouteObject[] = [
  {
    path: "",
    element: <Navigation />, //change to Navigation element
    errorElement: <NotFoundPage />,
    children: [
      {
        path: "",
        element: <Profile />,
      },
      {
        path: "networks",
        // element: <></>, //NetworkLayout
        children: [
          {
            path: "",
            element: <Networks />,
          },
          {
            path: ":network/:range",
            lazy: async () => {
              const { Network } = await import("../modules/network");
              return {
                element: <Network />,
              };
            },
          },
        ],
      },
      {
        path: "addresses",
        // element: <></>, //AddressLayout
        children: [
          {
            path: "",
            element: <></>,
          },
          {
            path: ":address",
            lazy: async () => {
              const { Address } = await import("../modules/address");
              return {
                element: <Address />,
              };
            },
          },
        ],
      },
      {
        path: "hosts",
        // element: <Hosts />, //HostLayout
        children: [
          {
            path: "",
            element: <Hosts />,
          },
          {
            path: ":mac",
            lazy: async () => {
              const { HostPage: Host } = await import("../modules/host");
              return {
                element: <Host />,
              };
            },
          },
        ],
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
          {
            path: "users",
            lazy: async () => {
              const { Users } = await import("../modules/users");
              return {
                element: <Users />,
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

import React from "react";
import { RouteObject, RouterProvider, createHashRouter } from "react-router-dom";
import { Main } from "../Main";
import { Navigation } from "./Navigation";

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
                element: <Main />, //HostLayout
            },
            {
                path: "domains",
                element: <Main />, //DomainLayout
                children: [
                    {
                        path: ":domain",
                        lazy: async () => {
                            const {DnsRecords} = await import("../components/DnsRecords")
                            return {
                                element: <DnsRecords />,
                            };
                        },
                    },
                ],
            },
        ],
    }
]

const router = createHashRouter(routes, {
    basename: "/",
    future: {
        v7_normalizeFormMethod: true,
    },
})

export const App = () => {
    return (
        <React.StrictMode>
            <RouterProvider router={router} />
        </React.StrictMode>
    )
}
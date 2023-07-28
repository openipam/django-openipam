import React from "react";
import { Link, Outlet } from "react-router-dom";

export const Navigation = () => {
  return (
    <div className="bg-base-100">
      <div className="w-full navbar menu menu-horizontal items-center flex flex-row bg-base-300">
        <button className="btn btn-ghost btn-primary">
          <Link className="link-hover text-white font-semibold text-lg" to="/">
            Home
          </Link>
        </button>
        <button className="btn btn-ghost btn-primary">
          <Link
            className="link-hover text-white font-semibold text-lg"
            to="/hosts"
          >
            Hosts
          </Link>
        </button>
        <button className="btn btn-ghost btn-primary">
          <Link
            className="link-hover text-white font-semibold text-lg"
            to="/domains"
          >
            Domains
          </Link>
        </button>
      </div>

      <Outlet />
    </div>
  );
};

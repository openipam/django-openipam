import React from "react";
import { Link, Outlet } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export const Navigation = () => {
  const auth = useAuth();
  return (
    <div className="bg-base-100">
      <div className="w-full navbar menu menu-horizontal items-center flex flex-row bg-base-300">
        <button className="btn btn-ghost btn-primary">
          <Link className="link-hover font-semibold text-lg" to="/">
            Home
          </Link>
        </button>
        <button className="btn btn-ghost btn-primary">
          <Link className="link-hover font-semibold text-lg" to="/hosts">
            Hosts
          </Link>
        </button>
        <button className="btn btn-ghost btn-primary">
          <Link className="link-hover font-semibold text-lg" to="/domains">
            Domains
          </Link>
        </button>
        {auth?.is_ipamadmin && (
          <>
            <button className="btn btn-ghost btn-primary">
              <Link className="link-hover font-semibold text-lg" to="/networks">
                Networks
              </Link>
            </button>
            <button className="btn btn-ghost btn-primary">
              <Link
                className="link-hover font-semibold text-lg"
                to="/admin/logs"
              >
                Logs
              </Link>
            </button>
            <button className="btn btn-ghost btn-primary">
              <Link
                className="link-hover font-semibold text-lg"
                to="/admin/users"
              >
                Users
              </Link>
            </button>
          </>
        )}
      </div>

      <Outlet />
    </div>
  );
};

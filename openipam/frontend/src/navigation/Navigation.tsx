import React, { useContext } from "react";
import { Link, Outlet } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { ThemeContext, useThemes } from "../hooks/useTheme";
import { Palette } from "@mui/icons-material";
import { IdToName } from "../components/idToName";

export const Navigation = () => {
  const auth = useAuth();
  const { theme, setTheme } = useContext(ThemeContext);
  const themes = useThemes();
  return (
    <div
      className={`${
        theme === "dark" ? "bg-gray-800" : "bg-base-100"
      } min-h-screen min-w-screen w-full h-full`}
      data-theme={theme}
    >
      <div className="w-full navbar menu menu-horizontal items-center flex flex-row justify-between bg-base-300">
        <div className="flex-flex-row justify-start">
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
                <Link
                  className="link-hover font-semibold text-lg"
                  to="/networks"
                >
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
        <div className="flex flex-row gap-2 mr-4">
          <Palette />
          <select
            className="btn btn-ghost btn-primary"
            onChange={(e) => {
              setTheme(e.target.value);
            }}
            value={theme}
          >
            {themes.map((theme) => (
              <option key={theme} value={theme}>
                {IdToName(theme)}
              </option>
            ))}
          </select>
        </div>
      </div>

      <Outlet />
    </div>
  );
};

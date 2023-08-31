import React from "react";
export const Loading = () => {
  return (
    <div className="flex flex-col justify-center items-center h-screen w-screen bg-base-100">
      <div className="loader ease-linear rounded-full border-8 border-t-8 border-primary h-64 w-64"></div>
    </div>
  );
};

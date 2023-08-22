import { Info, InfoOutlined } from "@mui/icons-material";
import React, { useState } from "react";

export const ToolTip = (p: {
  children?: React.ReactNode;
  text: string;
  props?: string;
}) => {
  const [isHovering, setIsHovering] = useState(false);
  const handleMouseOver = () => {
    setIsHovering(true);
  };

  const handleMouseOut = () => {
    setIsHovering(false);
  };

  return (
    <div className="relative">
      {/* Hover over this div to hide/show <HoverText /> */}
      <div onMouseOver={handleMouseOver} onMouseOut={handleMouseOut}>
        {p.children ?? (
          <>
            <div className="pl-0.5 pb-0.5">
              <InfoOutlined fontSize="inherit" />
            </div>
          </>
        )}
      </div>
      {isHovering && (
        <div
          className={`absolute bg-black text-white p-2 shadow-lg rounded-xl ${p.props}`}
        >
          {p.text}
        </div>
      )}
    </div>
  );
};

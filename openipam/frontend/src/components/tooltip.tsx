import { InfoOutlined } from "@mui/icons-material";
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
            <div className="pl-0.5 pb-0.5 text-secondary-content">
              <InfoOutlined fontSize="inherit" color="inherit" />
            </div>
          </>
        )}
      </div>
      {isHovering && (
        <div
          className={`absolute bg-black p-2 shadow-lg rounded-xl ${p.props} text-white`}
        >
          {p.text}
        </div>
      )}
    </div>
  );
};

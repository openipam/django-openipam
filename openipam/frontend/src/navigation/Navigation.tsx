import { Box, Button, ButtonGroup, Tab, Tabs, Typography } from "@mui/material";
import React from "react";
import { Link, Outlet } from "react-router-dom";

export const Navigation = () => {
  return (
    <div>
      <div style={{ flexDirection: "row", width: "100%", padding: "10px" }}>
        <ButtonGroup variant="text" aria-label="text button group">
          <Button>
            <Link style={styles.button} to="/">
              Home
            </Link>
          </Button>
          <Button>
            <Link style={styles.button} to="/hosts">
              Hosts
            </Link>
          </Button>
          <Button>
            <Link style={styles.button} to="/domains">
              Domains
            </Link>
          </Button>
        </ButtonGroup>
      </div>

      <Outlet />
    </div>
  );
};

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function CustomTabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          <Typography>{children}</Typography>
        </Box>
      )}
    </div>
  );
}

const styles = {
  button: {
    color: "white",
    textDecoration: "none",
    backgroundColor: "#42a5f5",
    border: "none",
    cursor: "pointer",
    fontSize: "1rem",
    fontWeight: 400,
    padding: "0.5rem 1rem",
    borderRadius: "0.5rem",
    "&:hover": {
      color: "#ccc",
    },
  },
};

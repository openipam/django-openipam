import React from "react";

export const Show = (p: {
  children: React.ReactNode;
  when: boolean | any;
  fallback?: React.ReactNode;
}) => {
  return Boolean(p.when) ? p.children : p.fallback ?? <></>;
};

export const Switch = (p: { children: React.ReactNode; expression: any }) => {
  const children = React.Children.toArray(p.children);
  for (let i = 0; i < children.length; i++) {
    const child = children[i];
    if (React.isValidElement(child) && child.props.value === p.expression) {
      return child;
    }
  }
  return <></>;
};

export const Match = (p: { value: any; children: React.ReactNode }) =>
  p.children;

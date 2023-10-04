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
    if (!React.isValidElement(child)) {
      continue;
    }
    // based on type of value and type of expression
    const expressionType = typeof p.expression;
    const valueType = typeof child.props.value;
    if (expressionType === valueType && child.props.value === p.expression) {
      return child;
    } else if (
      expressionType === "string" &&
      valueType === "object" &&
      child.props.value instanceof RegExp &&
      child.props.value.test(p.expression)
    ) {
      return child;
    } else if (
      expressionType === "string" &&
      valueType === "object" &&
      child.props.value instanceof Array &&
      child.props.value.includes(p.expression)
    ) {
      return child;
    } else if (
      expressionType === "string" &&
      valueType === "object" &&
      child.props.value instanceof Function &&
      child.props.value(p.expression)
    ) {
      return child;
    } else if (
      expressionType === "object" &&
      valueType === "string" &&
      p.expression instanceof RegExp &&
      p.expression.test(child.props.value)
    ) {
      return child;
    } else if (
      expressionType === "object" &&
      valueType === "string" &&
      p.expression instanceof Array &&
      p.expression.includes(child.props.value)
    ) {
      return child;
    } else if (
      expressionType === "object" &&
      valueType === "string" &&
      p.expression instanceof Function &&
      p.expression(child.props.value)
    ) {
      return child;
    }
  }
  return (
    children.find((c) => React.isValidElement(c) && c.props.default) ?? <></>
  );
};

export const Match = (p: {
  value?: any;
  default?: boolean;
  children: React.ReactNode;
}) => p.children;

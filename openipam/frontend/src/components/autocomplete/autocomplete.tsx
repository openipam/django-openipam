import React, {
  InputHTMLAttributes,
  ReactNode,
  useEffect,
  useState,
} from "react";

export const AutocompleteSelect = (props: {
  options: Array<any>;
  getValueFromOption: (option: any | undefined) => string;
  textFilter: any;
  setTextFilter: any;
  value: any;
  setValue: any;
  loading?: boolean;
  inputProps?: InputHTMLAttributes<HTMLInputElement> | undefined;
  icon?: ReactNode;
  disableFilter?: boolean;
}) => {
  const [show, setShow] = useState(false);
  const [hovering, setHovering] = useState(0);

  const filteredOptions = () =>
    props.disableFilter
      ? props.options
      : props.options?.filter?.((option) =>
          props.getValueFromOption(option).includes(props.textFilter)
        ) ?? [];

  useEffect(() => {
    setHovering(0);
  }, [props.textFilter]);
  const handleInput = (event: any) => {
    props.setTextFilter(event.currentTarget.value);
  };
  const handleAdd = (item: any) => {
    const transformedVal = props.getValueFromOption(item);
    const valueSelected =
      props.getValueFromOption(props.value) === transformedVal;
    if (valueSelected) props.setValue(undefined);
    else props.setValue(() => item);
  };

  useEffect(() => {
    if (props.value) {
      props.setTextFilter(props.getValueFromOption(props.value));
    }
  }, [props.value]);

  const handleKeydown = (event: any) => {
    if (event.code === "ArrowUp") {
      setHovering((prev) =>
        prev === 0 ? filteredOptions().length - 1 : prev - 1
      );
    } else if (event.code === "ArrowDown") {
      setHovering((prev) =>
        prev + 1 === filteredOptions().length ? 0 : prev + 1
      );
    } else if (event.code === "Enter") {
      event.preventDefault();
      const item = filteredOptions().at(hovering);
      if (!item) {
        return;
      }
      handleAdd(item);
    }
  };

  const inputId = `${Math.random()}`;

  return (
    <>
      <div className={`dropdown dropdown-end ${show ? "dropdown-open" : ""}`}>
        <label
          className="input input-bordered input-primary flex gap-2 items-center w-full"
          htmlFor={inputId}
        >
          {props.icon}
          <input
            id={inputId}
            type="text"
            className="bg-transparent p-1 w-full"
            value={props.textFilter}
            onInput={handleInput}
            onKeyDown={handleKeydown}
            onFocus={() => setShow(true)}
            onBlur={() => setShow(false)}
          />
          {props.loading && <div className="spinner spinner-primary"></div>}
        </label>
        <ul className="dropdown-content menu shadow bg-base-100 rounded-box w-full z-50 max-h-[30vh] overflow-y-scroll flex-nowrap menu-compact">
          {filteredOptions().map((item, i) => (
            <li
              className={`${
                props.getValueFromOption(props.value) ===
                props.getValueFromOption(item)
                  ? "bordered"
                  : ""
              }`}
              key={i}
            >
              <a
                className={`cursor-default ${hovering === i ? "active" : ""} ${
                  props.getValueFromOption(props.value) ===
                    props.getValueFromOption(item) && hovering === i
                    ? "!border-primary-focus"
                    : ""
                }`}
                onMouseDown={(e) => {
                  e.preventDefault();
                  handleAdd(item);
                }}
              >
                {props.getValueFromOption(item)}
              </a>
            </li>
          ))}
        </ul>
      </div>
    </>
  );
};

export const AutocompleteMultiSelect = (props: {
  options: Array<any>;
  getValueFromOption: (option: any | undefined) => string;
  textFilter: any;
  setTextFilter: any;
  value: any[];
  setValue: (x: any[]) => void;
  loading?: boolean;
  inputProps?: InputHTMLAttributes<HTMLInputElement> | undefined;
  icon?: ReactNode;
  disableFilter?: boolean;
}) => {
  const [show, setShow] = useState(false);
  const [hovering, setHovering] = useState(0);

  const filteredOptions = () =>
    props.disableFilter
      ? props.options
      : props.options?.filter?.((option) =>
          props.getValueFromOption(option).includes(props.textFilter)
        ) ?? [];

  useEffect(() => {
    setHovering(0);
  }, [props.textFilter]);
  const handleInput = (event: any) => {
    props.setTextFilter(event.currentTarget.value);
  };
  const handleAdd = (item: any) => {
    const transformedVal = props.getValueFromOption(item);
    const valueSelected =
      props.getValueFromOption(props.value) === transformedVal;
    if (valueSelected)
      props.setValue(
        props.value.filter(
          (v) => props.getValueFromOption(v) !== transformedVal
        )
      );
    else props.setValue([...props.value, item]);
  };

  const handleKeydown = (event: any) => {
    if (event.code === "ArrowUp") {
      setHovering((prev) =>
        prev === 0 ? filteredOptions().length - 1 : prev - 1
      );
    } else if (event.code === "ArrowDown") {
      setHovering((prev) =>
        prev + 1 === filteredOptions().length ? 0 : prev + 1
      );
    } else if (event.code === "Enter") {
      event.preventDefault();
      const item = filteredOptions().at(hovering);
      if (!item) {
        return;
      }
      handleAdd(item);
    }
  };

  const inputId = `${Math.random()}`;

  return (
    <>
      <div className={`dropdown dropdown-end ${show ? "dropdown-open" : ""}`}>
        <label
          className="input input-bordered input-primary flex gap-2 items-center w-full"
          htmlFor={inputId}
        >
          {props.icon}
          <input
            id={inputId}
            type="text"
            className="bg-transparent p-1 w-full"
            value={props.textFilter}
            onInput={handleInput}
            onKeyDown={handleKeydown}
            onFocus={() => setShow(true)}
            onBlur={() => setShow(false)}
          />
          {props.loading && <div className="spinner spinner-primary"></div>}
        </label>
        <ul className="dropdown-content menu shadow bg-base-100 rounded-box w-full z-50 max-h-[30vh] overflow-y-scroll flex-nowrap menu-compact">
          {filteredOptions().map((item, i) => (
            <li className={``} key={i}>
              <a
                className={`cursor-default ${hovering === i ? "active" : ""} `}
                onMouseDown={(e) => {
                  e.preventDefault();
                  handleAdd(item);
                }}
              >
                {props.getValueFromOption(item)}
              </a>
            </li>
          ))}
        </ul>
      </div>
    </>
  );
};

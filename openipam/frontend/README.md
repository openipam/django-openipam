# React frontend for OpenIpam

Written in typescript, using BrowserRouter for navigation.

For styling, tailwindCSS is used alongside DaisyUI.

### Datatable

The data table used is Tanstack React Table, a headless yet powerful datatable. The generic UI implementation is found in components/table/table.tsx.

Individual tables are found in their respective module directories. A module directory will have an index.tsx where the main page is rendered.

There will be a useXXXTable.tsx file for every table displayed on the given page. This useXXXTable file handles state for the table. Generally, the data to be displayed is called using a hook along the lines of useInfiniteXXX, where this hook is kept in the /queries directory in the /hooks directory.

Typically, columns and table actions are also declared in the same useXXXTable file, though can be moved to a separate file for larger, more complex tables. Any other files in the module directory are components used only by that module, such as create or edit modules.

## Installation and Setup

In the /frontend directory, run:

```
npm install
```

Compiling - to test changes in real time (separate terminal), run the following in the same directory:

```
npm run dev
```

Run the backend with this command in the root directory:

```
./manage.py runserver
```

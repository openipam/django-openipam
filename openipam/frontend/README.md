# React frontend for OpenIpam

The url path /ui will take you to this react app containing datatable views for the main modules used in openipam. Written in typescript.

## Installation and Setup

In the /frontend directory, run:

```
npm install
```

Compiling - to test changes in real time (separate terminal), run the following in the same directory:

```
npm run dev
```

Run the backend api with these command in the root directory (Also covered in the readme in root):

```
poetry shell
poetry install
./manage.py runserver
```

Then visit localhost:8000/ui to view the react app.

## General Details

### [Components](/openipam/frontend/src/components/)

Various reusable components are contained in this directory. The more complex, reused components are in the autocomplete, forms, and table subdirectories.

#### [Table](/openipam/frontend/src/components/table/)

The datatable used is Tanstack React Table, a headless yet powerful datatable. The generic UI implementation is found in components/table/table.tsx.

Individual tables are found in their respective module directories. A module directory will have an index.tsx where the main page is rendered.

There will be a useXXXTable.tsx file in the same directory for every table displayed on the given page. This useXXXTable file handles state for the table. Generally, the data to be displayed is called using a hook along the lines of useInfiniteXXX, where this hook is kept in the /queries directory in the /hooks directory.

Typically, columns and table actions are also declared in the same useXXXTable file, though can be moved to a separate file for larger, more complex tables. Any other files in the module directory are components used only by that module, such as create or edit modules.

#### [Autocomplete](/openipam/frontend/src/components/autocomplete/)

The base autocomplete.tsx file contains an autocomplete (an a multi-select autocomplete) components that will display data passed to it. To create a new autocomplete components, create a new file in the same directory which will handle the filter state, and any necessary api calls, providing the autocomplete component with the options and filter value.

#### [Forms](/openipam/frontend/src/components/forms/)

As forms were extremely common, logic for a general module, footer, and a titledInput were pulled into their respective components and are kept here. It is recommended to use them when creating new modules.

### [Hooks](/openipam/frontend/src/hooks/)

The useApi, useAuth, useTheme, and useToken hooks are self-explanatory.

#### [Queries](/openipam/frontend/src/hooks/queries)

When building an api query, it is recommended to use the 'usePrefetchedQuery' in the usePrefetchedQuery file if you want to cache prefetch the next page. Otherwise, use the 'useQueryBuilder' function in the same file.

Prefetched queries should be prefixed with 'useInfinite'.

### [Navigation](/openipam/frontend/src/navigation/)

We are using ReactRouter's HashRouter for navigation.

### [Styles](/openipam/frontend/src/styles/)

TailwindCSS is used alongside DaisyUI.

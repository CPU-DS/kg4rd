# kg4rd visualization

Please execute the following commands in the `kg4rd/visualization/kg4rd` directory:

## Install

```
npm install
```

## Preview

Start the backend server and execute the following command:

```
npm run dev
```

then open the browser and visit `http://localhost:5173`.

## Build

```
npm run build
```

## Backend address

All configuration files are located in the `src/config/environments/` directory. For development and production environments, the corresponding files are:

- `development.ts`
- `production.ts`

change the value of `api.baseURL` in the corresponding file.

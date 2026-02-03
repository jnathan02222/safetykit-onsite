# Atlas frontend

## Quickstart

This is a Node project, so begin by installing [Node](https://nodejs.org/en/download)
and [pnpm](https://pnpm.io/installation) (which is like npm but it doesn't use
a butt ton of space).

Then, run

```bash
pnpm install
```

and start the server with

```bash
pnpm dev
```

Make sure to define an `.env` file with

```
BACKEND_API=http://localhost:8000/
```

This will be used for Next rewrites (basically proxies frontend requests to the backend,
which is an easy way to avoid CORS issues).

## Development

### File structure

```
frontend/
├── api-codegen/    # Helper functions and types for the backend API
├── app/            # Main React app logic
└── common/      # Various general components (not a design system)
```

For now I'm not using a design system, but it would probably be a good idea to
use one once we have enough frontend features.

### Tools

[Prettier](https://prettier.io/) is a very useful tool for formatting TypeScript.
Usage of it will probably be added as a CI check, but for now download it and have
it format on save for your own sanity :)

(this is more a note to self) It's probably also a good idea to learn
[Next](https://nextjs.org/) and [React](https://react.dev/)

### API codegen

I use OpenAPI codegen to automatically generate functions / types to work with the
backend API. Make sure the backend server is running and then run

```bash
pnpm openapi-ts
```

import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  input: 'http://localhost:8000/api/openapi.json', // sign up at app.heyapi.dev
  output: 'api-codegen/client'
});
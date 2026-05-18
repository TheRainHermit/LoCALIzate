import type { APIRoute } from "astro";

export const GET: APIRoute = async ({ params }) => {
  const { slug } = params;
  return new Response(
    JSON.stringify({ message: `API endpoint para: ${slug}` }),
    { status: 200, headers: { "Content-Type": "application/json" } }
  );
};

export const POST: APIRoute = async ({ params, request }) => {
  const { slug } = params;
  const body = await request.json();
  return new Response(
    JSON.stringify({ message: `POST recibido en: ${slug}`, data: body }),
    { status: 200, headers: { "Content-Type": "application/json" } }
  );
};
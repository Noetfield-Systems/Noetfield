export async function onRequestPost() {
  return new Response(JSON.stringify({ ok: true }), {
    status: 200,
    headers: {
      "Content-Type": "application/json",
      "Set-Cookie": "nf_invest_auth=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0",
      "Cache-Control": "no-store",
    },
  });
}

export async function onRequest() {
  return new Response(JSON.stringify({ ok: false }), { status: 405 });
}

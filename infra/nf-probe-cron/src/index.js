import { runAllProbes } from "./probes.js";

export default {
  async scheduled(controller, env, ctx) {
    ctx.waitUntil(
      (async () => {
        const outcome = await runAllProbes(env);
        console.log(
          JSON.stringify({
            event: "nf_probe_cron",
            cron: controller.cron,
            scheduledTime: controller.scheduledTime,
            run_id: outcome.runId,
            ok: outcome.ok,
            probes: outcome.results.map((r) => ({
              probe: r.probe,
              status: r.status,
              ok: r.ok,
              reason: r.reason || null,
            })),
          })
        );
      })()
    );
  },

  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/health") {
      return Response.json({ status: "ok", service: "nf-probe-cron" });
    }
    if (url.pathname === "/run" && request.method === "POST") {
      const outcome = await runAllProbes(env);
      return Response.json({
        ok: outcome.ok,
        run_id: outcome.runId,
        checked_at: outcome.checkedAt,
        probes: outcome.results,
      });
    }
    return new Response("Not found", { status: 404 });
  },
};

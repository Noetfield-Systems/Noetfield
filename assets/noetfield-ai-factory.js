(function () {
  "use strict";

  var form = document.getElementById("factory-form");
  var output = document.getElementById("yaml-output");
  var copy = document.getElementById("copy-spec");
  var receipt = document.getElementById("gate-receipt");

  if (!form || !output) return;

  function value(name, fallback) {
    var field = form.elements[name];
    return field && field.value ? field.value.trim() : fallback;
  }

  function slugify(text) {
    return String(text || "factory")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "")
      .slice(0, 48) || "factory";
  }

  function spec() {
    var factoryType = value("factoryType", "AI Factory");
    var targetUser = value("targetUser", "Operations team");
    var outputFormat = value("outputFormat", "Board-ready brief");
    var policyMode = value("policyMode", "ALLOW / BLOCK / ESCALATE");
    var id = slugify(factoryType);

    return "factory:\n" +
      "  id: noetfield-" + id + "\n" +
      "  name: \"" + factoryType + "\"\n" +
      "  layer: \"AI Factory Layer\"\n" +
      "  target_user: \"" + targetUser + "\"\n" +
      "  output_format: \"" + outputFormat + "\"\n" +
      "runtime:\n" +
      "  mode: stateless\n" +
      "  orchestration: queue_based_pipeline\n" +
      "  idempotency_key: request_id\n" +
      "  scaling:\n" +
      "    strategy: horizontal\n" +
      "    scale_metric: queue_depth\n" +
      "input_schema:\n" +
      "  required: [request_id, user_id, factory_type, payload]\n" +
      "output_schema:\n" +
      "  required: [request_id, status, result, audit]\n" +
      "agents:\n" +
      "  - intake_agent\n" +
      "  - planner_agent\n" +
      "  - retrieval_agent\n" +
      "  - synthesis_agent\n" +
      "  - validation_agent\n" +
      "  - formatter_agent\n" +
      "  - audit_agent\n" +
      "pipeline:\n" +
      "  nodes: [receive_request, classify_task, create_execution_plan, gather_context, generate_output, validate_output, repair_output, format_result, write_audit_record]\n" +
      "failure_handling:\n" +
      "  invalid_input: reject\n" +
      "  transient_model_error: retry\n" +
      "  validation_failure: repair_once_then_partial_or_fail\n" +
      "policy:\n" +
      "  mode: \"" + policyMode + "\"\n" +
      "  decisions: [ALLOW, BLOCK, ESCALATE]\n" +
      "audit:\n" +
      "  ledger: Trust Ledger\n" +
      "  final_output_hash: required\n" +
      "stateless_execution:\n" +
      "  worker_local_state: forbidden\n" +
      "  session_memory: forbidden\n" +
      "  intermediate_state_location: external_object_store\n";
  }

  function renderSpec() {
    output.textContent = spec();
  }

  function renderReceipt(data) {
    if (!receipt) return;
    receipt.innerHTML =
      "<p class=\"nf-card__tag\">Gate receipt</p>" +
      "<h3>" + data.gate_lane + " · " + data.status_record.policy_decision + "</h3>" +
      "<p>Request <code>" + data.request_id + "</code> is in <code>" + data.status_record.lane + "</code>.</p>" +
      "<ul>" +
      "<li>Next action: " + data.status_record.next_action + "</li>" +
      "<li>Current node: " + data.status_record.current_node + "</li>" +
      "<li>Audit state: " + data.status_record.audit_state + "</li>" +
      "<li>Hash: <code>" + data.audit.final_output_hash.slice(0, 16) + "</code></li>" +
      "</ul>";
  }

  function payload() {
    return {
      user_id: "noetfield-www",
      factory_type: value("factoryType", "AI Factory"),
      target_user: value("targetUser", "Operations team"),
      output_format: value("outputFormat", "Board-ready brief"),
      policy_mode: value("policyMode", "ALLOW / BLOCK / ESCALATE"),
      payload: {
        source_route: window.location.pathname,
        constraints: ["low_cost", "scalable", "stateless"],
        generated_spec: spec()
      }
    };
  }

  form.addEventListener("input", renderSpec);
  form.addEventListener("change", renderSpec);
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    if (receipt) {
      receipt.innerHTML = "<p class=\"nf-card__tag\">Gate receipt</p><h3>Submitting</h3><p>Creating a stateless receipt.</p>";
    }
    fetch("/api/gate/ai-factory-design", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload())
    })
      .then(function (res) { return res.json().then(function (data) { return { ok: res.ok, data: data }; }); })
      .then(function (result) {
        if (!result.ok) throw new Error("Gate request failed");
        renderReceipt(result.data);
      })
      .catch(function () {
        if (receipt) receipt.innerHTML = "<p class=\"nf-card__tag\">Gate receipt</p><h3>Unavailable</h3><p>The Gate endpoint did not respond.</p>";
      });
  });

  if (copy) {
    copy.addEventListener("click", function () {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(output.textContent || "");
      }
    });
  }

  renderSpec();
})();

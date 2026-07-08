/** Purchase hub — render Stripe catalog cards (no template literals in page HTML). */
(function () {
  async function loadSalesGrid() {
    var grid = document.getElementById("salesGrid");
    if (!grid) return;
    var catalog;
    try {
      var res = await fetch("/assets/noetfield-stripe-catalog.json");
      catalog = await res.json();
    } catch (_err) {
      grid.innerHTML =
        '<p>Catalog unavailable. Email <a href="mailto:operations@noetfield.com">operations@noetfield.com</a>.</p>';
      return;
    }
    grid.innerHTML = (catalog.offerings || [])
      .map(function (o) {
        var buy = o.payment_link_url
          ? '<a class="btn btn-primary" href="' +
            o.payment_link_url +
            '" rel="noopener">Pay with Stripe</a>'
          : "";
        var intake =
          '<a class="btn btn-secondary" href="' + o.intake_url + '">Request scoping</a>';
        return (
          '<article class="nf-sales-card"><h3>' +
          o.title +
          '</h3><p class="nf-sales-price">' +
          o.price_label +
          "</p><p>" +
          o.description +
          '</p><div class="nf-sales-actions">' +
          buy +
          intake +
          "</div></article>"
        );
      })
      .join("");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", loadSalesGrid);
  } else {
    loadSalesGrid();
  }
})();

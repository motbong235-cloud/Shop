(function () {
  const tg = window.Telegram && window.Telegram.WebApp;
  if (tg) {
    try {
      tg.ready();
      tg.expand();
      tg.setHeaderColor("#061B49");
      tg.setBackgroundColor("#F4F8FF");
    } catch (e) {}
  }

  const state = {
    user: null,
    products: [],
    orders: [],
    settings: {},
    cat: "all",
    q: "",
    product: null,
    planIdx: 0,
    order: null,
    isAdmin: false,
  };

  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];

  function toast(msg) {
    const t = $("#toast");
    t.textContent = msg;
    t.classList.add("on");
    clearTimeout(t._tm);
    t._tm = setTimeout(() => t.classList.remove("on"), 2600);
  }

  function initData() {
    return (tg && tg.initData) || "";
  }

  async function api(path, opts = {}) {
    const headers = Object.assign({ Accept: "application/json" }, opts.headers || {});
    if (!(opts.body instanceof FormData)) {
      headers["Content-Type"] = headers["Content-Type"] || "application/json";
    }
    const id = initData();
    if (id) headers["X-Telegram-Init-Data"] = id;
    const res = await fetch(path, { ...opts, headers });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || data.message || "Request failed");
    return data;
  }

  function show(name) {
    $$(".scr").forEach((s) => s.classList.remove("on"));
    const el = document.getElementById("scr-" + name);
    if (el) el.classList.add("on");
    $$(".nav button").forEach((b) => b.classList.toggle("on", b.dataset.scr === name));
    if (tg && tg.BackButton) {
      const main = ["home", "products", "orders", "account"].includes(name);
      if (main) tg.BackButton.hide();
      else {
        tg.BackButton.show();
        tg.BackButton.onClick(() => show("home"));
      }
    }
    window.scrollTo(0, 0);
  }

  function iconKey(p) {
    const k = ((p && (p.key || p.id || p.name)) || "").toLowerCase();
    if (k.includes("spotify") || k.includes("music")) return "i-music";
    if (k.includes("youtube") || k.includes("capcut") || k.includes("video")) return "i-video";
    if (k.includes("canva") || k.includes("design")) return "i-design";
    if (k.includes("gemini") || k.includes("gpt") || k.includes("ai") || k.includes("chat")) return "i-ai";
    return "i-box";
  }

  function escapeHtml(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function priceOf(p) {
    if (p.plans && p.plans.length) return Number(p.plans[0].price || 0);
    return Number(p.price || 0);
  }

  function imgOf(p) {
    return p.image || p.image_url || "";
  }

  function renderProducts(target, list) {
    const el = $(target);
    if (!list.length) {
      el.innerHTML = `<div class="empty">មិនមានផលិតផល</div>`;
      return;
    }
    el.innerHTML = list
      .map((p) => {
        const img = imgOf(p);
        const media = img
          ? `<img src="${escapeHtml(img)}" alt="">`
          : `<div class="ph"><svg class="ic"><use href="#${iconKey(p)}"/></svg></div>`;
        return `<div class="pcard" data-id="${escapeHtml(p.key || p.id)}">
          <div class="pcard-img">${media}</div>
          <div class="pcard-body">
            <h4>${escapeHtml(p.name)}</h4>
            <div class="cat">${escapeHtml(p.category || "")}</div>
            <div class="row">
              <span class="price">$${priceOf(p).toFixed(2)}</span>
              <span class="go"><svg class="ic ic-sm"><use href="#i-chev"/></svg></span>
            </div>
          </div>
        </div>`;
      })
      .join("");
    el.querySelectorAll(".pcard").forEach((card) => {
      card.addEventListener("click", () => openProduct(card.dataset.id));
    });
  }

  function filtered() {
    let list = state.products.slice();
    if (state.cat && state.cat !== "all") {
      const c = state.cat.toLowerCase();
      list = list.filter(
        (p) =>
          (p.category || "").toLowerCase().includes(c) ||
          (p.key || "").toLowerCase().includes(c) ||
          (p.name || "").toLowerCase().includes(c)
      );
    }
    if (state.q) {
      const q = state.q.toLowerCase();
      list = list.filter(
        (p) =>
          (p.name || "").toLowerCase().includes(q) ||
          (p.description || "").toLowerCase().includes(q) ||
          (p.key || "").toLowerCase().includes(q)
      );
    }
    return list;
  }

  function renderBanner() {
    const box = $("#home-banner");
    const url = state.settings.banner_url || state.settings.banner || "";
    if (url) {
      box.innerHTML = `<img src="${escapeHtml(url)}" alt="banner"><div class="hero-badge">Premium</div>`;
    } else {
      box.innerHTML = `<div class="hero-fallback">
        <h2>Premium Account &amp; Digital Services</h2>
        <p>ទិញងាយស្រួល · រហ័ស · សុវត្ថិភាព</p>
      </div><div class="hero-badge">Premium</div>`;
    }
  }

  function openProduct(id) {
    const p = state.products.find((x) => String(x.key || x.id) === String(id));
    if (!p) return;
    state.product = p;
    state.planIdx = 0;
    const img = imgOf(p);
    $("#detail-ico").innerHTML = img
      ? `<img src="${escapeHtml(img)}" alt="">`
      : `<svg class="ic"><use href="#${iconKey(p)}"/></svg>`;
    $("#detail-name").textContent = p.name;
    $("#detail-desc").textContent = p.description || p.category || "";
    const plans =
      p.plans && p.plans.length
        ? p.plans
        : [{ name: "Standard", price: p.price || 0, days: 30 }];
    $("#detail-plans").innerHTML = plans
      .map(
        (pl, i) => `<div class="plan ${i === 0 ? "on" : ""}" data-i="${i}">
        <div><b>${escapeHtml(pl.name || pl.label || "Plan")}</b><br>
        <span>${pl.days ? pl.days + " ថ្ងៃ" : ""}</span></div>
        <div class="pr">$${Number(pl.price || 0).toFixed(2)}</div>
      </div>`
      )
      .join("");
    $$("#detail-plans .plan").forEach((el) => {
      el.addEventListener("click", () => {
        $$("#detail-plans .plan").forEach((x) => x.classList.remove("on"));
        el.classList.add("on");
        state.planIdx = Number(el.dataset.i);
      });
    });
    show("detail");
  }

  function renderOrders() {
    const el = $("#orders-list");
    if (!state.orders.length) {
      el.innerHTML = `<div class="empty">មិនទាន់មានការបញ្ជាទិញ</div>`;
      return;
    }
    el.innerHTML = state.orders
      .slice()
      .reverse()
      .map(
        (o) => `<div class="litem">
        <div class="ico"><svg class="ic"><use href="#i-bag"/></svg></div>
        <div>
          <h4>${escapeHtml(o.product_name || o.product || "Order")}</h4>
          <p>${escapeHtml(o.status || "pending")} · $${Number(o.price || o.amount || 0).toFixed(2)}</p>
        </div>
      </div>`
      )
      .join("");
  }

  function renderAccount() {
    const u = state.user || {};
    $("#acc-name").textContent = u.first_name || u.name || "Kairozen User";
    $("#acc-user").textContent = u.username ? "@" + u.username : "Telegram User";
    $("#acc-bal").textContent = "$" + Number(u.balance || 0).toFixed(2);
    $("#acc-orders").textContent = String(u.orders || state.orders.length || 0);
    $("#acc-mem").textContent = state.isAdmin ? "Admin" : "User";
    const av = (u.first_name || "K").charAt(0).toUpperCase();
    $("#acc-av").textContent = av;
  }

  function renderAdmin() {
    const prev = $("#admin-banner-preview");
    const b = state.settings.banner_url || "";
    prev.innerHTML = b
      ? `<img src="${escapeHtml(b)}" alt="banner" style="width:100%;height:100px;object-fit:cover">`
      : `<div class="muted" style="padding:28px;text-align:center">មិនទាន់មាន banner</div>`;

    const list = $("#admin-prod-list");
    list.innerHTML = state.products
      .map((p) => {
        const img = imgOf(p);
        const thumb = img
          ? `<img src="${escapeHtml(img)}" alt="">`
          : `<svg class="ic"><use href="#${iconKey(p)}"/></svg>`;
        return `<div class="admin-prod" data-key="${escapeHtml(p.key || p.id)}">
          <div class="thumb">${thumb}</div>
          <div style="flex:1;min-width:0">
            <div style="font-weight:700;font-size:13px">${escapeHtml(p.name)}</div>
            <div class="muted">$${priceOf(p).toFixed(2)}</div>
            <div class="admin-edit">
              <input type="number" step="0.01" min="0.01" class="adm-price" value="${priceOf(p).toFixed(2)}" placeholder="តម្លៃ">
              <button type="button" class="btn btn-p btn-sm adm-save">រក្សាទុកតម្លៃ</button>
            </div>
          </div>
          <label class="btn btn-g btn-sm" style="width:auto;cursor:pointer;flex:none">
            <svg class="ic ic-sm"><use href="#i-img"/></svg>
            <input type="file" accept="image/*" data-key="${escapeHtml(p.key || p.id)}" class="admin-prod-file" style="display:none">
          </label>
        </div>`;
      })
      .join("");

    list.querySelectorAll(".admin-prod-file").forEach((inp) => {
      inp.addEventListener("change", async () => {
        if (!inp.files || !inp.files[0]) return;
        const fd = new FormData();
        fd.append("image", inp.files[0]);
        fd.append("product_key", inp.dataset.key);
        try {
          toast("កំពុង upload…");
          await api("/api/mini/admin/product-image", { method: "POST", body: fd });
          toast("រូបផលិតផលរក្សាទុកហើយ");
          await loadAll();
          renderAdmin();
        } catch (e) {
          toast(e.message);
        }
      });
    });

    list.querySelectorAll(".admin-prod").forEach((row) => {
      const btn = row.querySelector(".adm-save");
      const priceInp = row.querySelector(".adm-price");
      if (!btn) return;
      btn.addEventListener("click", async () => {
        try {
          await api("/api/mini/admin/product", {
            method: "POST",
            body: JSON.stringify({
              product_key: row.dataset.key,
              price: Number(priceInp.value),
            }),
          });
          toast("តម្លៃរក្សាទុកហើយ");
          await loadAll();
          renderAdmin();
        } catch (e) {
          toast(e.message);
        }
      });
    });
  }

  async function loadAll() {
    const data = await api("/api/mini/bootstrap");
    state.user = data.user || {};
    state.products = data.products || [];
    state.orders = data.orders || [];
    state.settings = data.settings || {};
    state.isAdmin = !!(data.user && data.user.is_admin);
    $("#btn-admin").style.display = state.isAdmin ? "grid" : "none";
    renderBanner();
    renderProducts("#home-grid", filtered().slice(0, 8));
    renderProducts("#prod-grid", filtered());
    renderOrders();
    renderAccount();
  }

  async function checkout() {
    const p = state.product;
    if (!p) return;
    const plans =
      p.plans && p.plans.length
        ? p.plans
        : [{ name: "Standard", price: p.price || 0 }];
    const plan = plans[state.planIdx] || plans[0];
    const email = $("#chk-email").value.trim();
    $("#chk-err").textContent = "";
    if (!email || !email.includes("@")) {
      $("#chk-err").textContent = "សូមបំពេញ email ត្រឹមត្រូវ";
      return;
    }
    const btn = $("#chk-btn");
    btn.disabled = true;
    try {
      const res = await api("/api/mini/order", {
        method: "POST",
        body: JSON.stringify({
          product_key: p.key || p.id,
          plan_index: state.planIdx,
          email,
        }),
      });
      state.order = res.order;
      const pay = res.payment || {};
      if (pay.qr_image) {
        $("#pay-qr").src =
          pay.qr_image.startsWith("http") || pay.qr_image.startsWith("data:") || pay.qr_image.startsWith("/")
            ? pay.qr_image
            : "data:image/png;base64," + pay.qr_image;
        $("#pay-qr").style.display = "block";
      } else {
        $("#pay-qr").style.display = "none";
      }
      $("#pay-amount").textContent = "$" + Number(res.order.price || plan.price).toFixed(2);
      $("#pay-id").textContent = res.order.id;
      $("#pay-note").textContent = pay.demo
        ? "DEMO — មិនទាន់ភ្ជាប់ ABA key"
        : pay.error
        ? pay.error
        : "ស្កេន KHQR ឬ OPEN ABA Mobile";
      if (pay.open_aba_url) {
        $("#pay-aba").href = pay.open_aba_url;
        $("#pay-aba").style.display = "flex";
      } else {
        $("#pay-aba").style.display = "none";
      }
      show("pay");
      toast("បង្កើត order រួច");
    } catch (e) {
      $("#chk-err").textContent = e.message;
    } finally {
      btn.disabled = false;
    }
  }

  $$(".nav button").forEach((b) =>
    b.addEventListener("click", () => {
      show(b.dataset.scr);
      if (b.dataset.scr === "products") renderProducts("#prod-grid", filtered());
      if (b.dataset.scr === "orders") renderOrders();
      if (b.dataset.scr === "account") renderAccount();
    })
  );

  $("#btn-admin").addEventListener("click", () => {
    renderAdmin();
    show("admin");
  });

  ["#search-home", "#search-prod"].forEach((sel) => {
    $(sel).addEventListener("input", (e) => {
      state.q = e.target.value;
      renderProducts("#home-grid", filtered().slice(0, 8));
      renderProducts("#prod-grid", filtered());
    });
  });

  function bindChips(row) {
    row.addEventListener("click", (e) => {
      const c = e.target.closest(".chip");
      if (!c) return;
      row.querySelectorAll(".chip").forEach((x) => x.classList.remove("on"));
      c.classList.add("on");
      state.cat = c.dataset.cat || "all";
      renderProducts("#home-grid", filtered().slice(0, 8));
      renderProducts("#prod-grid", filtered());
    });
  }
  bindChips($("#chips-home"));
  bindChips($("#chips-prod"));

  $("#btn-to-checkout").addEventListener("click", () => {
    const p = state.product;
    if (!p) return;
    const plans =
      p.plans && p.plans.length
        ? p.plans
        : [{ name: "Standard", price: p.price || 0 }];
    const plan = plans[state.planIdx] || plans[0];
    $("#chk-summary").textContent = `${p.name} · ${plan.name || "Plan"} · $${Number(
      plan.price
    ).toFixed(2)}`;
    $("#chk-err").textContent = "";
    show("checkout");
  });
  $("#chk-btn").addEventListener("click", checkout);
  $("#pay-check").addEventListener("click", async () => {
    if (!state.order) return;
    try {
      const res = await api("/api/mini/order/" + encodeURIComponent(state.order.id));
      toast("ស្ថានភាព: " + (res.order.status || "pending"));
    } catch (e) {
      toast(e.message);
    }
  });

  $("#admin-banner-file").addEventListener("change", async (e) => {
    const f = e.target.files && e.target.files[0];
    if (!f) return;
    const fd = new FormData();
    fd.append("image", f);
    try {
      toast("កំពុង upload banner…");
      const res = await api("/api/mini/admin/banner", { method: "POST", body: fd });
      state.settings.banner_url = res.banner_url;
      renderBanner();
      renderAdmin();
      toast("Banner រក្សាទុកហើយ");
    } catch (err) {
      toast(err.message);
    }
  });

  loadAll()
    .then(() => show("home"))
    .catch((e) => {
      $("#home-grid").innerHTML = `<div class="empty">${escapeHtml(
        e.message
      )}<br><br><button class="btn btn-p" type="button" onclick="location.reload()">Retry</button></div>`;
    });
})();

(function () {
  const D = window.ATLAS;
  const X = window.EXTRAS;
  const root = document.getElementById("app");
  const navEl = document.getElementById("nav");
  const searchInput = document.getElementById("q");

  const FAM_BLURB = {
    magnitude: ["أظهر الحجم المطلق أو النسبي بين الفئات.", "Show absolute or relative size across categories."],
    ranking: ["حين يكون الموقع في القائمة أهم من القيمة.", "When rank matters more than the raw value."],
    deviation: ["أكّد الفرق عن صفر أو هدف أو متوسط.", "Emphasise difference from zero, a target, or an average."],
    distribution: ["كيف تنتشر القيم؟ أين الكثافة والشذوذ؟", "How values spread: density, skew, outliers."],
    correlation: ["هل يتحرك متغيّران معاً؟ وكيف؟", "Do two variables move together — and how?"],
    time: ["الاتجاه، الموسمية، والانكسار.", "Trend, seasonality, and breaks."],
    part: ["كيف يتكون المجموع من أجزائه؟", "How a whole is built from its parts."],
    spatial: ["حين يكون الموقع الجغرافي هو القصة.", "When location is the story."],
    flow: ["حركة الكميات والعلاقات بين الكيانات.", "Movement of quantities and ties between entities."],
    special: ["البُنى، العمليات، والنص، وعدم اليقين.", "Hierarchy, process, text, and uncertainty."],
  };

  let lang = localStorage.getItem("atlas-lang") || "ar";
  let audience = localStorage.getItem("atlas-aud") || "analyst";
  let cb = localStorage.getItem("atlas-cb") === "1";
  let quizI = 0, quizScore = 0, quizDone = false, quizPick = null;

  function t(k) { return (window.I18N[lang] && window.I18N[lang][k]) || k; }
  function L(ar, en) { return lang === "en" ? (en || ar) : ar; }
  function applyChrome() {
    document.documentElement.lang = lang === "ar" ? "ar" : "en";
    document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
    document.body.classList.toggle("cb-on", cb);
    const brand = document.getElementById("brand-title");
    if (brand) brand.textContent = t("brand");
    searchInput.placeholder = t("search");
    document.getElementById("btn-lang").textContent = t("lang");
    const aud = document.getElementById("aud");
    aud.value = audience;
    aud.options[0].text = t("aud_all");
    aud.options[1].text = t("aud_news");
    aud.options[2].text = t("aud_exec");
    document.getElementById("btn-cb").textContent = cb ? t("cb_on") : t("cb_off");
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      el.textContent = t(el.dataset.i18n);
    });
    document.getElementById("foot-copy").textContent = t("footer");
  }

  function allowed(id) {
    if (audience === "analyst") return true;
    const set = audience === "exec" ? X.exec : X.news;
    return set.includes(id);
  }
  function vis(list) { return list.filter((c) => allowed(c.id)); }

  function allCharts() {
    const out = [];
    D.families.forEach((f) => {
      f.charts.forEach((c, i) => out.push({ ...c, family: f, index: i }));
    });
    return vis(out);
  }
  function findChart(id) {
    for (const f of D.families) {
      const i = f.charts.findIndex((c) => c.id === id);
      if (i >= 0) return { ...f.charts[i], family: f, index: i };
    }
    return null;
  }
  function findFamily(id) { return D.families.find((f) => f.id === id); }
  function img(id) { return `img/charts/${id}.png`; }
  function recipe(id) { return window.RECIPES[id] || window.RECIPES.default; }

  function crumb(parts) {
    return `<div class="crumb">${parts.map((p) => (p.href ? `<a href="${p.href}">${p.t}</a>` : p.t)).join(" · ")}</div>`;
  }
  function chartCard(c) {
    return `<a class="chart-card" href="#/chart/${c.id}">
      <img src="${img(c.id)}" alt="${L(c.ar, c.en)}" loading="lazy">
      <div class="meta"><h3>${L(c.ar, c.en)}</h3><div class="en">${lang === "ar" ? c.en : c.ar}</div></div>
    </a>`;
  }

  function recCard(title, start, avoid, chartId) {
    const name = chartId && findChart(chartId) ? L(findChart(chartId).ar, findChart(chartId).en) : start;
    const text = lang === "ar"
      ? `التوصية: استخدم ${name}. تجنّب ${avoid}. السبب: ${title}.`
      : `Recommendation: use ${name}. Avoid ${avoid}. Because: ${title}.`;
    return `<div class="rec" id="rec">
      <h3>${t("rec_card")}</h3>
      <p id="rec-text">${text}</p>
      <div class="cta-row">
        <button class="btn btn-gold" id="copy-rec" type="button">${t("copy")}</button>
        <button class="btn btn-ghost dark" id="dl-rec" type="button">${t("download")}</button>
      </div>
    </div>`;
  }

  function home() {
    return `
      <section class="hero">
        <div class="hero-inner">
          <p class="kicker">ATLAS · 2026</p>
          <h1>${t("brand")}</h1>
          <p class="lead">${t("hero_lead")}</p>
          <div class="stats">
            <div><b>80</b><span>charts</span></div>
            <div><b>10</b><span>families</span></div>
            <div><b>12</b><span>× same data</span></div>
            <div><b>8</b><span>chart crimes</span></div>
          </div>
          <div class="cta-row">
            <a class="btn btn-gold" href="#/choose">${t("cta_choose")}</a>
            <a class="btn btn-ghost" href="#/data">${t("cta_data")}</a>
            <a class="btn btn-ghost" href="#/quiz">${t("cta_quiz")}</a>
          </div>
        </div>
      </section>
      <div class="wrap page">
        <h2 class="sec">${t("tools_t")}</h2>
        <p class="sec-sub">${t("tools_s")}</p>
        <div class="gold-rule"></div>
        <div class="grid tools-grid">
          <a class="fam-card" href="#/data"><div class="count">01</div><h3>${t("nav_data")}</h3><p>${t("data_s")}</p></a>
          <a class="fam-card" href="#/play"><div class="count">02</div><h3>${t("nav_play")}</h3><p>${t("play_s")}</p></a>
          <a class="fam-card" href="#/quiz"><div class="count">03</div><h3>${t("nav_quiz")}</h3><p>${t("quiz_sub")}</p></a>
          <a class="fam-card" href="#/compare"><div class="count">04</div><h3>${t("nav_compare")}</h3><p>${t("compare_s")}</p></a>
          <a class="fam-card" href="#/poster"><div class="count">05</div><h3>${t("nav_poster")}</h3><p>${t("poster_s")}</p></a>
          <a class="fam-card" href="#/principles"><div class="count">06</div><h3>${t("nav_principles")}</h3><p>${t("prin_s")}</p></a>
        </div>
        <h2 class="sec" style="margin-top:2.2rem">${t("fam_t")}</h2>
        <p class="sec-sub">${t("fam_s")}</p>
        <div class="gold-rule"></div>
        <div class="grid">
          ${D.families.map((f) => `
            <a class="fam-card" href="#/family/${f.id}">
              <div class="count">${vis(f.charts).length}</div>
              <h3>${L(f.ar, f.en)}</h3>
              <div class="en">${lang === "ar" ? f.en : f.ar}</div>
              <p>${L(FAM_BLURB[f.id][0], FAM_BLURB[f.id][1])}</p>
            </a>`).join("")}
        </div>
      </div>`;
  }

  function choose(active) {
    const row = D.chooser.find((c) => c.goal === active);
    const fam = row ? findFamily(row.family) : null;
    const first = fam ? vis(fam.charts)[0] : null;
    return `
      <div class="wrap page">
        ${crumb([{ t: t("brand"), href: "#/" }, { t: t("choose_t") }])}
        <h2 class="sec">${t("choose_t")}</h2>
        <p class="sec-sub">${t("choose_s")}</p>
        <div class="gold-rule"></div>
        <div class="choose-grid">
          ${D.chooser.map((c) => `
            <button class="choose-card ${c.goal === active ? "active" : ""}" data-goal="${c.goal}">
              <div class="goal">${c.goal}</div>
              <div class="start">${t("start")}: ${c.start}</div>
              <div class="avoid">${t("avoid_short")}: ${c.avoid}</div>
            </button>`).join("")}
        </div>
        ${row ? recCard(row.goal, row.start, row.avoid, first && first.id) : ""}
        ${fam ? `<h2 class="sec" style="margin-top:1.6rem">${L(fam.ar, fam.en)}</h2>
          <div class="grid">${vis(fam.charts).map(chartCard).join("")}</div>` : ""}
      </div>`;
  }

  function dataShape(active) {
    const node = X.tree.find((n) => n.id === active);
    return `
      <div class="wrap page">
        ${crumb([{ t: t("brand"), href: "#/" }, { t: t("data_t") }])}
        <h2 class="sec">${t("data_t")}</h2>
        <p class="sec-sub">${t("data_s")}</p>
        <div class="gold-rule"></div>
        <div class="choose-grid">
          ${X.tree.map((n) => `
            <button class="choose-card ${n.id === active ? "active" : ""}" data-shape="${n.id}">
              <div class="goal">${L(n.ar, n.en)}</div>
              <div class="start">${L(n.hint_ar, n.hint_en)}</div>
            </button>`).join("")}
        </div>
        ${node ? `
          ${recCard(L(node.ar, node.en), node.rec.map((id) => { const c = findChart(id); return c ? L(c.ar, c.en) : id; }).join(" / "), L(node.avoid_ar, node.avoid_en), node.rec[0])}
          <h3 class="sec" style="margin-top:1.2rem">${t("rec_charts")}</h3>
          <div class="grid">${node.rec.map(findChart).filter(Boolean).filter((c) => allowed(c.id)).map(chartCard).join("")}</div>
          <div class="info bad" style="margin-top:1rem"><h4>${t("forbid")}: ${findChart(node.avoid) ? L(findChart(node.avoid).ar, findChart(node.avoid).en) : node.avoid}</h4>
            <p>${L(node.avoid_ar, node.avoid_en)}</p></div>
        ` : ""}
      </div>`;
  }

  function family(id) {
    const f = findFamily(id);
    if (!f) return home();
    const charts = vis(f.charts);
    return `<div class="wrap page">
      ${crumb([{ t: t("brand"), href: "#/" }, { t: L(f.ar, f.en) }])}
      <div class="banner-fam">
        <div class="en">${lang === "ar" ? f.en : f.ar}</div>
        <h1>${L(f.ar, f.en)}</h1>
        <p style="margin:.4rem 0 0;color:#d9d1c2">${L(FAM_BLURB[f.id][0], FAM_BLURB[f.id][1])} · ${charts.length}</p>
      </div>
      <div class="grid">${charts.map(chartCard).join("")}</div>
    </div>`;
  }

  function chart(id) {
    const c = findChart(id);
    if (!c) return home();
    const f = c.family;
    const r = recipe(id);
    const prev = vis(f.charts)[vis(f.charts).findIndex((x) => x.id === id) - 1];
    const next = vis(f.charts)[vis(f.charts).findIndex((x) => x.id === id) + 1];
    return `<div class="wrap page">
      ${crumb([{ t: t("brand"), href: "#/" }, { t: L(f.ar, f.en), href: "#/family/" + f.id }, { t: L(c.ar, c.en) }])}
      <div class="chart-hero">
        <div class="frame"><img src="${img(c.id)}" alt="${L(c.ar, c.en)}"></div>
        <div class="headline">
          <div class="en">${lang === "ar" ? c.en : c.ar}</div>
          <h1>${L(c.ar, c.en)}</h1>
          <p>${c.purpose}</p>
          <div class="cta-row">
            <a class="btn btn-gold" href="#/family/${f.id}">${t("all_charts_of")} «${L(f.ar, f.en)}»</a>
            <a class="btn btn-ghost dark" href="#/compare?a=${c.id}">${t("nav_compare")}</a>
          </div>
        </div>
      </div>
      <div class="info-grid">
        <div class="info good"><h4>${t("when")}</h4><p>${c.when}</p></div>
        <div class="info bad"><h4>${t("avoid")}</h4><p>${c.avoid}</p></div>
        <div class="info"><h4>${t("data")}</h4><p>${c.data}</p></div>
        <div class="info bad"><h4>${t("mistake")}</h4><p>${c.mistake}</p></div>
        <div class="info good"><h4>${t("alt")}</h4><p>${c.alt}</p></div>
        <div class="info"><h4>${t("family")}</h4><p>${L(f.ar, f.en)}</p></div>
      </div>
      <div class="recipe">
        <h3>${t("recipe")}</h3>
        <div class="recipe-grid">
          <div><h4>Excel</h4><pre>${r.excel}</pre></div>
          <div><h4>Power BI</h4><pre>${r.pbi}</pre></div>
          <div><h4>Python</h4><pre>${r.py}</pre></div>
        </div>
      </div>
      ${recCard(L(c.ar, c.en), L(c.ar, c.en), c.avoid, c.id)}
      <div class="pager">
        ${prev ? `<a href="#/chart/${prev.id}">→ ${L(prev.ar, prev.en)}</a>` : "<span></span>"}
        ${next ? `<a href="#/chart/${next.id}">${L(next.ar, next.en)} ←</a>` : "<span></span>"}
      </div>
    </div>`;
  }

  function play(active) {
    const cur = X.play.find((p) => p.id === active) || X.play.find((p) => p.id === "line");
    return `<div class="wrap page">
      ${crumb([{ t: t("brand"), href: "#/" }, { t: t("play_t") }])}
      <h2 class="sec">${t("play_t")}</h2>
      <p class="sec-sub">${t("play_s")}</p>
      <div class="gold-rule"></div>
      <div class="play-tabs">
        ${X.play.map((p) => `<a class="tab ${p.id === cur.id ? "on" : ""}" href="#/play?shape=${p.id}">${L(p.ar, p.en)}</a>`).join("")}
      </div>
      <div class="chart-hero">
        <div class="frame"><img src="img/play/${cur.id}.png" alt="${L(cur.ar, cur.en)}"></div>
        <div>
          <span class="verdict v-${cur.verdict}">${t("verdict_" + cur.verdict)}</span>
          <h3>${t("story")}</h3>
          <p class="lead-sm">${L(cur.story_ar, cur.story_en)}</p>
        </div>
      </div>
    </div>`;
  }

  function quiz() {
    const Q = X.quiz;
    if (quizI >= Q.length) {
      return `<div class="wrap page quiz-end">
        <h2 class="sec">${t("quiz_score")}: ${quizScore} / ${Q.length}</h2>
        <p class="sec-sub">${quizScore >= 7 ? (lang === "ar" ? "عين محرّر بيانات." : "A newsroom eye.") : (lang === "ar" ? "أعد المبادئ الثمانية ثم حاول." : "Revisit the eight principles, then retry.")}</p>
        <button class="btn btn-gold" id="quiz-reset">${t("quiz_again")}</button>
      </div>`;
    }
    const q = Q[quizI];
    const opts = lang === "ar" ? q.options_ar : q.options_en;
    return `<div class="wrap page">
      ${crumb([{ t: t("brand"), href: "#/" }, { t: t("quiz_title") }])}
      <h2 class="sec">${t("quiz_title")} · ${quizI + 1}/${Q.length}</h2>
      <p class="sec-sub">${t("quiz_sub")} · ${t("quiz_score")}: ${quizScore}</p>
      <div class="gold-rule"></div>
      <div class="frame"><img src="${img(q.id)}" alt=""></div>
      <p class="q">${L(q.q_ar, q.q_en)}</p>
      <div class="quiz-opts">
        ${opts.map((o, i) => `<button class="opt ${quizPick === i ? "picked" : ""} ${quizDone ? (i === q.answer ? "yes" : quizPick === i ? "no" : "") : ""}" data-i="${i}">${o}</button>`).join("")}
      </div>
      ${quizDone ? `<p class="quiz-fb ${quizPick === q.answer ? "good" : "bad"}">${quizPick === q.answer ? t("correct") : t("wrong")}</p>
        <div class="cta-row"><a class="btn btn-ghost dark" href="#/principles/${q.id}">${t("nav_principles")}</a>
        <button class="btn btn-gold" id="quiz-next">${t("quiz_next")}</button></div>` : `<button class="btn btn-gold" id="quiz-check">${t("check")}</button>`}
    </div>`;
  }

  function compare(a, b) {
    const ids = allCharts();
    const ca = findChart(a) || ids[0];
    const cb_ = findChart(b) || ids[3];
    const sel = (selId) => ids.map((c) => `<option value="${c.id}" ${c.id === selId ? "selected" : ""}>${L(c.ar, c.en)}</option>`).join("");
    return `<div class="wrap page">
      ${crumb([{ t: t("brand"), href: "#/" }, { t: t("compare_t") }])}
      <h2 class="sec">${t("compare_t")}</h2>
      <p class="sec-sub">${t("compare_s")}</p>
      <div class="gold-rule"></div>
      <div class="compare-pick">
        <select id="cmp-a">${sel(ca.id)}</select>
        <span class="en">${t("vs")}</span>
        <select id="cmp-b">${sel(cb_.id)}</select>
      </div>
      <div class="compare-grid">
        ${[ca, cb_].map((c) => `
          <article class="cmp">
            <h3><a href="#/chart/${c.id}">${L(c.ar, c.en)}</a></h3>
            <div class="frame"><img src="${img(c.id)}" alt=""></div>
            <p><strong>${t("when")}:</strong> ${c.when}</p>
            <p><strong>${t("avoid")}:</strong> ${c.avoid}</p>
          </article>`).join("")}
      </div>
    </div>`;
  }

  function principlesIndex() {
    return `<div class="wrap page">
      ${crumb([{ t: t("brand"), href: "#/" }, { t: t("nav_principles") }])}
      <h2 class="sec">${t("prin_t")}</h2>
      <p class="sec-sub">${t("prin_s")}</p>
      <div class="gold-rule"></div>
      <div class="prin-list">
        ${D.principlePages.map((p) => `
          <a class="prin-card" href="#/principles/${p.id}">
            <div class="prin-num">${p.n}</div>
            <div><h3>${lang === "en" ? p.en : p.title}</h3><p>${lang === "en" && window.PRIN_EN[p.id] ? window.PRIN_EN[p.id].setup : p.setup}</p></div>
          </a>`).join("")}
      </div>
    </div>`;
  }

  function principle(id) {
    const p = D.principlePages.find((x) => x.id === id);
    if (!p) return principlesIndex();
    const en = window.PRIN_EN[id] || {};
    const i = D.principlePages.findIndex((x) => x.id === id);
    const prev = D.principlePages[i - 1];
    const next = D.principlePages[i + 1];
    return `<div class="wrap page">
      ${crumb([{ t: t("brand"), href: "#/" }, { t: t("nav_principles"), href: "#/principles" }, { t: lang === "en" ? p.en : p.title }])}
      <div class="en">${p.en}</div>
      <h2 class="sec">${lang === "en" ? p.en : p.title}</h2>
      <p class="sec-sub">${L(p.setup, en.setup)}</p>
      <div class="mode-bar">
        <button data-mode="left">${t("misleading")}</button>
        <button data-mode="both" class="on-both">${t("both")}</button>
        <button data-mode="right">${t("honest")}</button>
      </div>
      <div class="pair both" id="pair"><img src="${img(p.id)}" alt=""></div>
      <div class="info-grid" style="margin-top:1rem">
        <div class="info bad"><h4>${t("why_bad")}</h4><p>${L(p.wrong, en.wrong)}</p></div>
        <div class="info good"><h4>${t("why_good")}</h4><p>${L(p.right, en.right)}</p></div>
      </div>
      <div class="rule-bar"><strong>${t("rule")}:</strong> ${L(p.rule, en.rule)}</div>
      <div class="pager">
        ${prev ? `<a href="#/principles/${prev.id}">→ ${lang === "en" ? prev.en : prev.title}</a>` : "<span></span>"}
        ${next ? `<a href="#/principles/${next.id}">${lang === "en" ? next.en : next.title} ←</a>` : "<span></span>"}
      </div>
    </div>`;
  }

  function poster() {
    const picks = {
      magnitude: ["bar", "lollipop", "bullet"],
      ranking: ["ordered_bar", "slope", "bump"],
      deviation: ["diverging_bar", "butterfly", "surplus_deficit"],
      distribution: ["histogram", "boxplot", "violin"],
      correlation: ["scatter", "bubble", "corr_heatmap"],
      time: ["line", "slope", "calendar_heatmap"],
      part: ["waffle", "stacked100", "treemap"],
      spatial: ["choropleth", "bubble_map", "dot_density"],
      flow: ["sankey", "alluvial", "network"],
      special: ["gantt", "radar", "errorbar"],
    };
    return `<div class="wrap page poster-page">
      <div class="no-print cta-row" style="margin-bottom:1rem">
        <button class="btn btn-gold" id="print-poster">${t("print")}</button>
      </div>
      <header class="poster-head">
        <p class="kicker">ATLAS · VISUAL VOCABULARY</p>
        <h1>${t("brand")}</h1>
        <p>${t("poster_s")}</p>
      </header>
      <div class="poster-grid">
        ${D.families.map((f) => `
          <section class="poster-fam">
            <h2>${L(f.ar, f.en)} <span class="en">${f.en}</span></h2>
            <div class="poster-thumbs">
              ${(picks[f.id] || []).map((id) => {
                const c = findChart(id);
                return c ? `<figure><img src="${img(id)}" alt=""><figcaption>${L(c.ar, c.en)}</figcaption></figure>` : "";
              }).join("")}
            </div>
          </section>`).join("")}
      </div>
    </div>`;
  }

  function gallery() {
    return `<div class="wrap page">
      ${crumb([{ t: t("brand"), href: "#/" }, { t: t("gallery_t") }])}
      <h2 class="sec">${t("gallery_t")}</h2>
      <div class="gold-rule"></div>
      ${D.families.map((f) => {
        const cs = vis(f.charts);
        if (!cs.length) return "";
        return `<h2 class="sec" style="margin-top:1.5rem"><a href="#/family/${f.id}">${L(f.ar, f.en)}</a></h2>
          <div class="grid">${cs.map(chartCard).join("")}</div>`;
      }).join("")}
    </div>`;
  }

  function sources() {
    return `<div class="wrap page">
      ${crumb([{ t: t("brand"), href: "#/" }, { t: t("nav_sources") }])}
      <h2 class="sec">${t("nav_sources")}</h2>
      <div class="gold-rule"></div>
      <div class="grid">${D.sources.map((s, i) => `
        <article class="src-card"><h3>${i + 1}. ${s.title}</h3><p>${s.note}</p>
          ${s.url.startsWith("http") ? `<a class="en" href="${s.url}" target="_blank" rel="noopener">${s.url}</a>` : `<span class="en">${s.url}</span>`}
        </article>`).join("")}</div>
    </div>`;
  }

  function search(q) {
    const needle = (q || "").trim().toLowerCase();
    const hits = allCharts().filter((c) => `${c.ar} ${c.en} ${c.purpose} ${c.when} ${c.family.ar}`.toLowerCase().includes(needle) || c.ar.includes(q));
    return `<div class="wrap page"><h2 class="sec">«${q}»</h2><p class="sec-sub">${hits.length}</p>
      ${hits.length ? `<div class="grid">${hits.map(chartCard).join("")}</div>` : `<p class="empty">${t("empty")}</p>`}</div>`;
  }

  function parse() {
    const raw = (location.hash || "#/").replace(/^#/, "");
    const [path, query] = raw.split("?");
    const parts = path.split("/").filter(Boolean);
    const params = {};
    if (query) query.split("&").forEach((kv) => {
      const [k, v] = kv.split("=");
      params[decodeURIComponent(k)] = decodeURIComponent(v || "");
    });
    return { parts, params };
  }

  function render() {
    applyChrome();
    const { parts, params } = parse();
    const a = parts[0], b = parts[1];
    let html;
    if (!a) html = home();
    else if (a === "choose") html = choose(params.goal || "");
    else if (a === "data") html = dataShape(params.shape || "");
    else if (a === "family" && b) html = family(b);
    else if (a === "chart" && b) html = chart(b);
    else if (a === "play") html = play(params.shape || "line");
    else if (a === "quiz") html = quiz();
    else if (a === "compare") html = compare(params.a, params.b);
    else if (a === "principles" && b) html = principle(b);
    else if (a === "principles") html = principlesIndex();
    else if (a === "poster") html = poster();
    else if (a === "gallery") html = gallery();
    else if (a === "sources") html = sources();
    else if (a === "search") html = search(params.q || "");
    else html = home();
    root.innerHTML = html;
    window.scrollTo(0, 0);
    bind();
    navEl.classList.remove("open");
  }

  function bindRec() {
    const copy = document.getElementById("copy-rec");
    const dl = document.getElementById("dl-rec");
    const text = document.getElementById("rec-text");
    if (copy && text) copy.onclick = () => {
      navigator.clipboard.writeText(text.textContent).then(() => { copy.textContent = t("copied"); });
    };
    if (dl && text) dl.onclick = () => downloadCard(text.textContent);
  }

  function downloadCard(text) {
    const cnv = document.createElement("canvas");
    cnv.width = 1200; cnv.height = 630;
    const ctx = cnv.getContext("2d");
    ctx.fillStyle = "#0E2433"; ctx.fillRect(0, 0, 1200, 630);
    ctx.strokeStyle = "#C6A15B"; ctx.lineWidth = 3; ctx.strokeRect(40, 40, 1120, 550);
    ctx.fillStyle = "#C6A15B"; ctx.font = "22px sans-serif";
    ctx.fillText("ATLAS · RECOMMENDATION", 80, 110);
    ctx.fillStyle = "#F7F2E8"; ctx.font = "32px sans-serif";
    wrapText(ctx, text, 80, 200, 1040, 44);
    const a = document.createElement("a");
    a.download = "atlas-recommendation.png";
    a.href = cnv.toDataURL("image/png");
    a.click();
  }
  function wrapText(ctx, text, x, y, maxW, lh) {
    const words = text.split(" ");
    let line = "";
    for (const w of words) {
      const test = line + w + " ";
      if (ctx.measureText(test).width > maxW) { ctx.fillText(line, x, y); line = w + " "; y += lh; }
      else line = test;
    }
    ctx.fillText(line, x, y);
  }

  function bind() {
    bindRec();
    document.querySelectorAll(".choose-card[data-goal]").forEach((btn) => {
      btn.onclick = () => { location.hash = "#/choose?goal=" + encodeURIComponent(btn.dataset.goal); };
    });
    document.querySelectorAll(".choose-card[data-shape]").forEach((btn) => {
      btn.onclick = () => { location.hash = "#/data?shape=" + btn.dataset.shape; };
    });
    const bar = document.querySelector(".mode-bar");
    if (bar) {
      const pair = document.getElementById("pair");
      bar.onclick = (e) => {
        const b = e.target.closest("button"); if (!b) return;
        const mode = b.dataset.mode;
        pair.className = "pair " + (mode === "both" ? "both" : mode);
        bar.querySelectorAll("button").forEach((x) => (x.className = ""));
        b.className = mode === "left" ? "on-left" : mode === "right" ? "on-right" : "on-both";
      };
    }
    const qa = document.getElementById("cmp-a");
    const qb = document.getElementById("cmp-b");
    if (qa && qb) {
      const go = () => { location.hash = `#/compare?a=${qa.value}&b=${qb.value}`; };
      qa.onchange = go; qb.onchange = go;
    }
    const chk = document.getElementById("quiz-check");
    if (chk) chk.onclick = () => {
      if (quizPick == null) return;
      const q = X.quiz[quizI];
      if (!quizDone) { if (quizPick === q.answer) quizScore += 1; quizDone = true; render(); }
    };
    document.querySelectorAll(".opt").forEach((o) => {
      o.onclick = () => { if (quizDone) return; quizPick = +o.dataset.i; render(); };
    });
    const nxt = document.getElementById("quiz-next");
    if (nxt) nxt.onclick = () => { quizI += 1; quizDone = false; quizPick = null; render(); };
    const rst = document.getElementById("quiz-reset");
    if (rst) rst.onclick = () => { quizI = 0; quizScore = 0; quizDone = false; quizPick = null; render(); };
    const pr = document.getElementById("print-poster");
    if (pr) pr.onclick = () => window.print();
  }

  document.getElementById("btn-lang").onclick = () => {
    lang = lang === "ar" ? "en" : "ar";
    localStorage.setItem("atlas-lang", lang);
    render();
  };
  document.getElementById("aud").onchange = (e) => {
    audience = e.target.value;
    localStorage.setItem("atlas-aud", audience);
    render();
  };
  document.getElementById("btn-cb").onclick = () => {
    cb = !cb;
    localStorage.setItem("atlas-cb", cb ? "1" : "0");
    render();
  };
  document.getElementById("menu").onclick = () => navEl.classList.toggle("open");

  let st;
  searchInput.addEventListener("input", () => {
    clearTimeout(st);
    st = setTimeout(() => {
      const v = searchInput.value.trim();
      location.hash = v ? "#/search?q=" + encodeURIComponent(v) : "#/";
    }, 180);
  });

  window.addEventListener("hashchange", render);
  render();
})();

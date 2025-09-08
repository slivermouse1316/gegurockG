function $(sel, p = document) {
  return p.querySelector(sel);
}

/* GitHub Pages 리포 베이스 경로 */
const BASE = "/gegurockG";
const A = (p) => `${BASE}${p}`;
const bust = () => `?v=${Date.now()}`;

/* 공용 fetch 헬퍼 */
async function loadJSON(path) {
  const r = await fetch(path, { cache: "no-store" });
  if (!r.ok) throw new Error(`loadJSON ${path} -> ${r.status}`);
  return r.json();
}
async function loadText(path) {
  const r = await fetch(path, { cache: "no-store" });
  if (!r.ok) throw new Error(`loadText ${path} -> ${r.status}`);
  return r.text();
}

/* 아주 간단한 md -> html 변환 */
function mdToHtml(md) {
  return md
    .replace(/^# (.*$)/gim, "<h1>$1</h1>")
    .replace(/^## (.*$)/gim, "<h2>$1</h2>")
    .replace(/\*\*(.*?)\*\*/g, "<b>$1</b>")
    .replace(/\*(.*?)\*/g, "<i>$1</i>")
    .replace(/\n/g, "<br>");
}

/* 파셜 include */
async function include(selector, url) {
  const mount = $(selector);
  if (!mount) return;
  const res = await fetch(url + bust(), { cache: "no-store" });
  if (!res.ok) {
    console.error(`[include] ${url} -> ${res.status}`);
    return;
  }
  mount.innerHTML = await res.text();
}

/* 헤더/푸터 로드 + 첫 페이지만 '개구락지' 제목 */
async function initPartials() {
  await include("#header", A("/assets/header.html"));
  await include("#footer", A("/assets/footer.html"));

  const path = location.pathname;
  const isIndex =
    path.endsWith("/index.html") || path === BASE || path === `${BASE}/`;
  const siteTitle = $("#siteTitle");
  if (siteTitle) siteTitle.textContent = isIndex ? "개구락지" : "Cinéma Vérité";
}

/* 블로그 목록 */
async function initBlog() {
  const listEl = $("#postList");
  if (!listEl) return;
  const posts = await loadJSON(A("/posts/posts.json"));
  listEl.innerHTML = "";
  posts.forEach((p) => {
    const li = document.createElement("li");
    li.innerHTML = `<a href="${A("/post.html")}?slug=${p.slug}">${p.title}</a>`;
    listEl.appendChild(li);
  });
}

/* 블로그 글 */
async function initPost() {
  const c = $("#postContainer");
  if (!c) return;
  const slug = new URLSearchParams(location.search).get("slug");
  if (!slug) {
    c.innerHTML = "<p>글을 찾을 수 없음</p>";
    return;
  }
  const md = await loadText(A(`/posts/${slug}.md`));
  c.innerHTML = mdToHtml(md);
  const title = $("#postTitle");
  if (title) title.textContent = slug;
}

/* WebGL 목록 */
async function initWebGL() {
  const list = $("#webglList");
  if (!list) return;
  const games = await loadJSON(A("/webgl/list.json"));
  list.innerHTML = "";
  games.forEach((g) => {
    const div = document.createElement("div");
    div.className = "card";
    div.innerHTML = `
      <h3>${g.title}</h3>
      <p>${g.description}</p>
      <a class="btn" href="${A(g.path)}/index.html">실행</a>`;
    list.appendChild(div);
  });
}

/* 진입점: 헤더/푸터 먼저, 그 다음 컨텐츠 초기화 */
document.addEventListener("DOMContentLoaded", async () => {
  await initPartials();
  initBlog();
  initPost();
  initWebGL();
});

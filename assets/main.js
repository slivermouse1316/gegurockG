function $(sel, p = document) {
  return p.querySelector(sel);
}
async function loadJSON(path) {
  const r = await fetch(path);
  return r.json();
}
async function loadText(path) {
  const r = await fetch(path);
  return r.text();
}
function mdToHtml(md) {
  return md
    .replace(/^# (.*$)/gim, "<h1>$1</h1>")
    .replace(/^## (.*$)/gim, "<h2>$1</h2>")
    .replace(/\*\*(.*?)\*\*/g, "<b>$1</b>")
    .replace(/\*(.*?)\*/g, "<i>$1</i>")
    .replace(/\n/g, "<br>");
}
async function initBlog() {
  const listEl = $("#postList");
  if (!listEl) return;
  const posts = await loadJSON("posts/posts.json");
  listEl.innerHTML = "";
  posts.forEach((p) => {
    const li = document.createElement("li");
    li.innerHTML =
      '<a href="post.html?slug=' + p.slug + '">' + p.title + "</a>";
    listEl.appendChild(li);
  });
}
async function initPost() {
  const c = $("#postContainer");
  if (!c) return;
  const slug = new URLSearchParams(location.search).get("slug");
  if (!slug) {
    c.innerHTML = "<p>글을 찾을 수 없음</p>";
    return;
  }
  const md = await loadText("posts/" + slug + ".md");
  c.innerHTML = mdToHtml(md);
  $("#postTitle").textContent = slug;
}
async function initWebGL() {
  const list = $("#webglList");
  if (!list) return;
  const games = await loadJSON("webgl/list.json");
  list.innerHTML = "";
  games.forEach((g) => {
    const div = document.createElement("div");
    div.className = "card";
    div.innerHTML =
      "<h3>" +
      g.title +
      "</h3><p>" +
      g.description +
      '</p><a class="btn" href="' +
      g.path +
      '/index.html">실행</a>';
    list.appendChild(div);
  });
}
document.addEventListener("DOMContentLoaded", () => {
  initBlog();
  initPost();
  initWebGL();
});

//푸터 및 헤더 자동 수정 기능
async function loadPartials() {
  // Header
  const header = document.getElementById("header");
  if (header) {
    const res = await fetch("assets/header.html");
    header.innerHTML = await res.text();
  }

  // Footer
  const footer = document.getElementById("footer");
  if (footer) {
    const res = await fetch("assets/footer.html");
    footer.innerHTML = await res.text();
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadPartials();
});

async function loadPartials() {
  const header = document.getElementById("header");
  if (header)
    header.innerHTML = await (await fetch("assets/header.html")).text();

  const footer = document.getElementById("footer");
  if (footer)
    footer.innerHTML = await (await fetch("assets/footer.html")).text();
}
document.addEventListener("DOMContentLoaded", loadPartials);

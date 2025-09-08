function $(sel, p = document) {
  return p.querySelector(sel);
}

/* GitHub Pages 리포 베이스 경로 (정확한 대/소문자!) */
const BASE = "/gegurockG";
const A = (p) => `${BASE}${p}`;
const bust = () => `?v=${Date.now()}`;

/* 상단 제목: 지금은 모든 페이지에서 Cinéma Vérité */
const DEFAULT_TITLE = "Cinéma Vérité";

/* 공용 fetch */
async function fetchText(url) {
  const res = await fetch(url + bust(), { cache: "no-store" });
  if (!res.ok) throw new Error(`${url} -> ${res.status}`);
  return res.text();
}

/* 헤더/푸터 include + 실패 시 폴백 생성 */
async function initPartials() {
  // === Header ===
  const headerMount = $("#header");
  if (headerMount) {
    try {
      // 1차: 정확 경로
      headerMount.innerHTML = await fetchText(A("/assets/header.html"));
    } catch (e1) {
      try {
        // 2차: 혹시 파일명이 Header.html인 경우(대/소문자 이슈)
        headerMount.innerHTML = await fetchText(A("/assets/Header.html"));
      } catch (e2) {
        // 최종 폴백: 자바스크립트로 직접 헤더 삽입 (무조건 표시됨)
        headerMount.innerHTML = `
          <div class="nav">
            <div class="title">
              <a href="${A("/index.html")}" id="siteTitle">${DEFAULT_TITLE}</a>
            </div>
            <div class="menu">
              <a href="${A("/about.html")}">소개</a>
              <a href="${A("/blog.html")}">일상</a>
              <a href="${A("/webgl.html")}">데모</a>
            </div>
          </div>`;
        console.warn(
          "[header] fallback rendered:",
          e1?.message || e1,
          e2?.message || e2
        );
      }
    }

    // 제목 강제 통일 (원하면 여기서 페이지별 분기 가능)
    const siteTitle = $("#siteTitle");
    if (siteTitle) siteTitle.textContent = DEFAULT_TITLE;
  }

  // === Footer ===
  const footerMount = $("#footer");
  if (footerMount) {
    try {
      footerMount.innerHTML = await fetchText(A("/assets/footer.html"));
    } catch (e1) {
      try {
        footerMount.innerHTML = await fetchText(A("/assets/Footer.html"));
      } catch (e2) {
        footerMount.innerHTML = `<footer>© ${DEFAULT_TITLE}</footer>`;
        console.warn(
          "[footer] fallback rendered:",
          e1?.message || e1,
          e2?.message || e2
        );
      }
    }
  }
}

/* (기존 블로그/웹GL 초기화는 그대로 두면 됨 — 생략) */
document.addEventListener("DOMContentLoaded", async () => {
  await initPartials();
  // initBlog(); initPost(); initWebGL();  // 쓰시는 경우 유지
});

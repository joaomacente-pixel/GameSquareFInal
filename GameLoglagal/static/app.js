const USERNAME = "usuariolindo";
let games = [];
let selectedRating = 0;

const $ = (selector) => document.querySelector(selector);

function showScreen(name) {
  document.querySelectorAll(".screen").forEach(el => el.classList.remove("active"));
  $(`#screen-${name}`).classList.add("active");
  document.querySelectorAll(".nav-item").forEach(el => el.classList.toggle("active", el.dataset.screen === name));
  $("#page-label").textContent = ({home:"INÍCIO",profile:"MEU PERFIL",write:"NOVA REVIEW"})[name];
  if (name === "profile") loadProfile();
  if (name === "write") loadGames();
  window.scrollTo({top:0, behavior:"smooth"});
}

document.querySelectorAll("[data-screen]").forEach(btn => btn.addEventListener("click", () => showScreen(btn.dataset.screen)));
document.querySelectorAll("[data-go]").forEach(btn => btn.addEventListener("click", () => showScreen(btn.dataset.go)));

function stars(rating) {
  const full = Math.round(Number(rating) || 0);
  return "★".repeat(full) + "☆".repeat(5-full);
}
function safe(value) {
  return String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}
function reviewCard(r) {
  return `<article class="review-card">
    <img class="cover" src="${safe(r.game_cover || '')}" alt="Capa de ${safe(r.game_title)}" onerror="this.style.visibility='hidden'">
    <div><div class="review-top"><span class="review-user">◉ ${safe(r.username)}</span><span class="stars">${stars(r.rating)} <small>${Number(r.rating).toFixed(1)}</small></span></div>
    <div class="review-game">${safe(r.game_title)}</div><div class="review-meta">${safe(r.genre || "Jogo")} · ${safe((r.created_at || "").slice(0,10))}</div>
    <p class="review-copy">${safe(r.review_text)}</p></div></article>`;
}
async function loadFeed() {
  const response = await fetch("/api/reviews");
  const reviews = await response.json();
  $("#review-count").textContent = `${reviews.length} PUBLICAÇÕES`;
  $("#review-feed").innerHTML = reviews.length ? reviews.map(reviewCard).join("") : '<div class="empty">Ainda não há reviews. Seja o primeiro a publicar!</div>';
}
async function loadGames() {
  if (!games.length) {
    const response = await fetch("/api/games");
    games = await response.json();
  }
  $("#game-select").innerHTML = '<option value="">Selecione um jogo...</option>' +
    games.map(g => `<option value="${g.id}">${safe(g.title)} (${g.year || "—"})</option>`).join("");
}
async function loadProfile() {
  const response = await fetch(`/api/profile?username=${encodeURIComponent(USERNAME)}`);
  const data = await response.json();
  $("#stat-reviews").textContent = data.stats.reviews;
  $("#stat-games").textContent = data.stats.games;
  $("#stat-average").textContent = data.stats.average ?? "—";
  $("#profile-reviews").innerHTML = data.reviews.length ? data.reviews.map(reviewCard).join("") : '<div class="empty">Você ainda não publicou nenhuma review.</div>';
}
$("#game-select").addEventListener("change", () => {
  const game = games.find(g => g.id === Number($("#game-select").value));
  const box = $("#selected-game");
  if (!game) { box.classList.add("hidden"); return; }
  box.classList.remove("hidden");
  box.innerHTML = `<img src="${safe(game.cover)}" alt=""><strong>${safe(game.title)} <small class="muted">· ${safe(game.genre)}</small></strong>`;
});
document.querySelectorAll("#rating-picker button").forEach(btn => btn.addEventListener("click", () => {
  selectedRating = Number(btn.dataset.rating);
  document.querySelectorAll("#rating-picker button").forEach(b => b.classList.toggle("selected", Number(b.dataset.rating) <= selectedRating));
  $("#rating-label").textContent = `${selectedRating} de 5 estrelas`;
}));
$("#review-text").addEventListener("input", e => $("#char-count").textContent = `${e.target.value.length} / 700`);

$("#review-form").addEventListener("submit", async e => {
  e.preventDefault();
  const message = $("#form-message");
  message.textContent = "";
  if (!selectedRating) { message.textContent = "Escolha uma nota antes de publicar."; return; }
  const response = await fetch("/api/reviews", {
    method:"POST", headers:{"Content-Type":"application/json"},
    body:JSON.stringify({username:USERNAME, game_id:$("#game-select").value, rating:selectedRating, review_text:$("#review-text").value})
  });
  const result = await response.json();
  if (!response.ok) { message.textContent = result.error || "Não foi possível publicar."; return; }
  e.target.reset(); selectedRating = 0;
  document.querySelectorAll("#rating-picker button").forEach(b => b.classList.remove("selected"));
  $("#rating-label").textContent = "Selecione de 1 a 5";
  $("#char-count").textContent = "0 / 700";
  $("#selected-game").classList.add("hidden");
  message.textContent = "Review publicada com sucesso!";
  await loadFeed();
  setTimeout(() => showScreen("home"), 700);
});

loadFeed();
loadGames();

// Gallery for catalog.json. GLB models open in <model-viewer>; .spz splats in Spark (three.js).
const $ = (id) => document.getElementById(id);
const TIER_LABEL = { roblox: "Roblox", game: "Game", hero: "Hero", splat: "Splat" };

let assets = [];
let splatCleanup = null;
let openToken = 0; // bumps on every open/close so a slow load cannot draw into a newer viewer

// "user.github.io/repo/" -> "https://github.com/user/repo"
(function repoLink() {
  const m = location.hostname.match(/^([^.]+)\.github\.io$/);
  const repo = location.pathname.split("/").filter(Boolean)[0];
  if (m && repo) $("repo-link").href = `https://github.com/${m[1]}/${repo}`;
  else $("repo-link").hidden = true;
})();

function fmtBytes(n) {
  return n > 1 << 20 ? `${(n / (1 << 20)).toFixed(1)} MB` : `${Math.max(1, Math.round(n / 1024))} KB`;
}

function detail(a) {
  const parts = [a.format.toUpperCase(), fmtBytes(a.bytes)];
  if (a.triangles != null) parts.push(`${a.triangles.toLocaleString()} triangles`);
  if (a.max_texture) parts.push(`${a.max_texture}px textures`);
  if (a.splat_points != null) parts.push(`${a.splat_points.toLocaleString()} gaussians`);
  parts.push("MIT license");
  return parts.join(" · ");
}

function card(a) {
  const el = document.createElement("button");
  el.className = "card";
  el.type = "button";
  const thumb = a.preview
    ? `<img src="${a.preview}" alt="" loading="lazy">`
    : `<span>${a.format.toUpperCase()}</span>`;
  el.innerHTML = `
    <div class="thumb">${thumb}</div>
    <div class="card-body">
      <h3></h3>
      <div class="chips">
        <span class="chip tier-${a.tier}">${TIER_LABEL[a.tier]}</span>
        <span class="chip">${a.category}</span>
      </div>
    </div>`;
  el.querySelector("h3").textContent = a.name; // names come from metadata: set as text, never HTML
  el.addEventListener("click", () => openViewer(a));
  return el;
}

function render() {
  const q = $("q").value.trim().toLowerCase();
  const cat = $("category").value;
  const tier = $("tier").value;
  const shown = assets.filter((a) =>
    (!cat || a.category === cat) &&
    (!tier || a.tier === tier) &&
    (!q || [a.name, a.description, ...(a.tags || [])].join(" ").toLowerCase().includes(q)));
  $("grid").replaceChildren(...shown.map(card));
  $("count").textContent = `${shown.length} of ${assets.length} models`;
  $("empty").hidden = assets.length > 0;
}

async function openViewer(a) {
  closeStage();
  $("v-name").textContent = a.name;
  $("v-meta").textContent = detail(a);
  $("v-download").href = a.model;
  $("v-download").setAttribute("download", a.model.split("/").pop());
  $("v-flip").hidden = a.format !== "spz";
  $("viewer").showModal();

  if (a.format === "glb") {
    const mv = document.createElement("model-viewer");
    mv.setAttribute("src", a.model);
    mv.setAttribute("camera-controls", "");
    mv.setAttribute("auto-rotate", "");
    mv.setAttribute("shadow-intensity", "1");
    mv.setAttribute("alt", a.name);
    $("v-stage").append(mv);
  } else {
    const token = openToken;
    const status = document.createElement("p");
    status.className = "stage-status";
    status.textContent = "Loading splat…";
    $("v-stage").append(status);
    try {
      const cleanup = await showSplat($("v-stage"), a.model, () => token === openToken);
      if (token === openToken) { splatCleanup = cleanup; status.remove(); }
      else cleanup();
    } catch (err) {
      console.error(err);
      if (token === openToken) status.textContent = "This splat could not be shown here. Download it to view it locally.";
    }
  }
}

async function showSplat(stage, url, isCurrent) {
  const THREE = await import("three");
  const { OrbitControls } = await import("three/addons/controls/OrbitControls.js");
  const { SparkRenderer, SplatMesh } = await import("@sparkjsdev/spark");
  if (!isCurrent()) return () => {};

  const renderer = new THREE.WebGLRenderer({ antialias: false });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  stage.append(renderer.domElement);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(50, 1, 0.01, 100);
  camera.position.set(0, 0, 2.5);
  scene.add(new SparkRenderer({ renderer }));

  const splat = new SplatMesh({ url });
  splat.quaternion.set(1, 0, 0, 0); // most generators write OpenCV axes (y down); flip to three.js y-up
  scene.add(splat);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.autoRotate = true;

  const flip = () => splat.rotateX(Math.PI);
  $("v-flip").addEventListener("click", flip);

  const resize = () => {
    const { clientWidth: w, clientHeight: h } = stage;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  };
  const ro = new ResizeObserver(resize);
  ro.observe(stage);
  resize();
  renderer.setAnimationLoop(() => { controls.update(); renderer.render(scene, camera); });

  return () => {
    $("v-flip").removeEventListener("click", flip);
    ro.disconnect();
    renderer.setAnimationLoop(null);
    splat.dispose?.();
    renderer.dispose();
  };
}

function closeStage() {
  openToken++;
  if (splatCleanup) { splatCleanup(); splatCleanup = null; }
  $("v-stage").replaceChildren();
}

$("v-close").addEventListener("click", () => $("viewer").close());
$("viewer").addEventListener("close", closeStage);
for (const id of ["q", "category", "tier"]) $(id).addEventListener("input", render);

try {
  const res = await fetch("catalog.json", { cache: "no-cache" });
  assets = (await res.json()).assets || [];
} catch {
  assets = [];
}
for (const c of [...new Set(assets.map((a) => a.category))].sort()) {
  $("category").append(new Option(c[0].toUpperCase() + c.slice(1), c));
}
render();

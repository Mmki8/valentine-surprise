// Builds a metric (cm) three.js blockout from plan.json and renders the
// QA passes for one camera. Runs in headless Chromium (see render.mjs).
//
// Plan axes: x = east, y = south (drawing down), z = up.
// three axes: X = x, Y = z, Z = y   (right-handed, Y up)
import * as THREE from 'three';

// ------------------------------------------------------------ palette
// "Guide" tints: the blockout is coloured by material intent so the image
// model reads WHERE each finish goes, not just the shapes.
const TINT = {
  floor_wood: 0xc9a47c, floor_stone_dark: 0x4a433d, floor_concrete: 0x8f8d89,
  wall_warm: 0xe4ddd3, wall_dark: 0x3a342f, wall_ext: 0xd9d2c8,
  ceiling_wood: 0x7d5c41, ceiling_plain: 0xefeae3, slab_edge: 0x2b2420,
  glass: 0xcfe6f2, frame: 0x2e2621, door: 0x5e412c, garage_door: 0x2d2a27,
  sofa: 0xd9ccb9, armchair: 0x6e4f3b, coffee_table: 0x2b2522, table: 0x5b3f2b,
  chair: 0x5a3d2c, stool: 0x1f1d1c, island: 0xb8b3ac, counter: 0x2b2724,
  tall_cabinet: 0x1e1b19, low_cabinet: 0x4b3527, appliance: 0xdedad5,
  tv: 0x101010, toilet: 0xf2f0ec, vanity: 0x2a2522, basin: 0x3a3632,
  bench: 0xb3875c, jacuzzi: 0x2a2826, water: 0x7fb2c0, shower: 0x3d3833,
  stair: 0x6b4a32, box: 0xe4ddd3, car: 0x171717, fixture: 0x222222,
  sink: 0x1b1b1b, cooktop: 0x0d0d0d, counter_top: 0x9a948c,
};
const STYLE_FLOOR = { dark_spa: 'floor_stone_dark', garage_gallery: 'floor_concrete' };
const STYLE_WALL = { dark_spa: 'wall_dark' };

export function buildScene(plan, opts = {}) {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xdfe8ee);
  const reg = [];                       // element registry: {id, kind, group}
  const add = (id, kind, mesh) => {
    mesh.userData.eid = id; mesh.userData.kind = kind;
    mesh.castShadow = true; mesh.receiveShadow = true;
    scene.add(mesh);
    reg.push({ id, kind, mesh });
    return mesh;
  };
  const mat = (hex, o = {}) => new THREE.MeshStandardMaterial({ color: hex, roughness: 0.85, metalness: 0, ...o });
  // axis-aligned box from plan rect + z range
  const boxMesh = (x0, y0, x1, y1, z0, z1, color, o) => {
    const [ax, bx] = [Math.min(x0, x1), Math.max(x0, x1)], [ay, by] = [Math.min(y0, y1), Math.max(y0, y1)];
    const [az, bz] = [Math.min(z0, z1), Math.max(z0, z1)];
    const g = new THREE.BoxGeometry(Math.max(bx - ax, 0.5), Math.max(bz - az, 0.5), Math.max(by - ay, 0.5));
    const m = new THREE.Mesh(g, mat(color, o));
    m.position.set((ax + bx) / 2, (az + bz) / 2, (ay + by) / 2);
    return m;
  };
  const L = plan.levels;
  const roomOf = (x, y) => plan.rooms.find(r => pointInPoly([x, y], r.polygon));

  // ---------------------------------------------------------- floors / ceilings
  for (const r of plan.rooms) {
    const shape = new THREE.Shape(r.polygon.map(([x, y]) => new THREE.Vector2(x, y)));
    const fg = new THREE.ShapeGeometry(shape); fg.rotateX(Math.PI / 2);   // y->Z
    const floor = new THREE.Mesh(fg, mat(TINT[STYLE_FLOOR[r.style] || 'floor_wood'], { side: THREE.DoubleSide }));
    floor.position.y = r.floor;
    add(`FLOOR_${r.id}`, 'floor', floor);
    if (r.id === 'R_living') continue;                // living handled by void ceiling
    const cshape = new THREE.Shape(r.polygon.map(([x, y]) => new THREE.Vector2(x, y)));
    for (const [hx0, hy0, hx1, hy1] of (r.ceiling_holes || []))
      cshape.holes.push(new THREE.Path([new THREE.Vector2(hx0, hy0), new THREE.Vector2(hx0, hy1), new THREE.Vector2(hx1, hy1), new THREE.Vector2(hx1, hy0)]));
    const cg = new THREE.ShapeGeometry(cshape); cg.rotateX(Math.PI / 2);
    const woodCeil = ['warm_wood_luxe', 'dark_spa'].includes(r.style);
    const ceil = new THREE.Mesh(cg, mat(TINT[woodCeil ? 'ceiling_wood' : 'ceiling_plain'], { side: THREE.DoubleSide }));
    ceil.position.y = r.ceiling;
    add(`CEIL_${r.id}`, 'ceiling', ceil);
  }
  // void ceiling + upper slab edge + gallery (ASSUMED until upper plan is supplied)
  const v = plan.void.rect;
  add('CEIL_void', 'ceiling', boxMesh(v[0], v[1], v[2], v[3], plan.void.ceiling, plan.void.ceiling + 20, TINT.ceiling_wood));
  const ge = plan.gallery_edge;
  add('SLAB_edge', 'slab_edge', boxMesh(ge.x - 30, ge.y0, ge.x, ge.y1, L.ceiling, L.slab_top, TINT.slab_edge));
  add('GALLERY_floor', 'slab_edge', boxMesh(ge.x - 160, ge.y0, ge.x - 30, ge.y1, L.ceiling, L.slab_top, TINT.ceiling_wood));
  add('GALLERY_glass', 'glass', glassPane(boxMesh(ge.x - 6, ge.y0, ge.x - 4, ge.y1, L.slab_top, L.slab_top + 100, TINT.glass)));
  add('GALLERY_wall', 'wall', boxMesh(ge.x - 175, ge.y0, ge.x - 160, ge.y1, L.slab_top, plan.void.ceiling, TINT.wall_warm));
  add('GALLERY_ceil', 'ceiling', boxMesh(ge.x - 175, ge.y0, ge.x, ge.y1, plan.void.ceiling, plan.void.ceiling + 20, TINT.ceiling_wood));
  add('GALLERY_end_n', 'wall', boxMesh(ge.x - 175, ge.y0 - 15, ge.x, ge.y0, L.ceiling, plan.void.ceiling, TINT.wall_warm));
  add('GALLERY_end_s', 'wall', boxMesh(ge.x - 175, ge.y1, ge.x, ge.y1 + 15, L.ceiling, plan.void.ceiling, TINT.wall_warm));
  for (const c of (plan.extra_ceilings || []))
    add(c.id, 'ceiling', boxMesh(c.rect[0], c.rect[1], c.rect[2], c.rect[3], c.z, c.z + 20, TINT.ceiling_plain));
  // exterior ground / terrace so glazing doesn't look onto void
  const ground = boxMesh(-800, -800, 2400, 2200, -62, -61, 0x8c9a7c); add('EXT_ground', 'exterior', ground);
  add('EXT_terrace', 'exterior', boxMesh(960, 985, 1600, 1250, -2, 0, 0xb9b2a6));

  // ---------------------------------------------------------- walls with openings
  for (const w of plan.walls) {
    const [x0, y0, x1, y1] = w.rect;
    const alongX = (x1 - x0) >= (y1 - y0);
    const [a0, a1] = alongX ? [x0, x1] : [y0, y1];
    const cuts = [];
    for (const o of plan.openings) {
      const r = o.rect;
      const ix = Math.min(x1, r[2]) - Math.max(x0, r[0]), iy = Math.min(y1, r[3]) - Math.max(y0, r[1]);
      if (ix > 0.5 && iy > 0.5) {
        const [b0, b1] = alongX ? [r[0], r[2]] : [r[1], r[3]];
        cuts.push({ a: Math.max(a0, b0), b: Math.min(a1, b1), sill: o.sill, head: o.head });
      }
    }
    cuts.sort((p, q) => p.a - q.a);
    const room = roomOf((x0 + x1) / 2 + (alongX ? 0 : 20), (y0 + y1) / 2 + (alongX ? 20 : 0));
    const color = w.kind === 'box' ? TINT.box : TINT[(room && STYLE_WALL[room.style]) || 'wall_warm'];
    const seg = (s0, s1, z0, z1, tag) => {
      if (s1 - s0 < 0.5 || z1 - z0 < 0.5) return;
      const m = alongX ? boxMesh(s0, y0, s1, y1, z0, z1, color) : boxMesh(x0, s0, x1, s1, z0, z1, color);
      add(`${w.id}${tag}`, 'wall', m);
    };
    let cur = a0, k = 0;
    for (const c of cuts) {
      seg(cur, c.a, w.z0, w.z1, `_s${k}`);
      if (c.sill > w.z0) seg(c.a, c.b, w.z0, c.sill, `_sill${k}`);
      if (c.head < w.z1) seg(c.a, c.b, c.head, w.z1, `_head${k}`);
      cur = Math.max(cur, c.b); k++;
    }
    seg(cur, a1, w.z0, w.z1, `_s${k}`);
  }

  // ---------------------------------------------------------- opening infill
  for (const o of plan.openings) {
    const [x0, y0, x1, y1] = o.rect;
    const alongX = (x1 - x0) >= (y1 - y0);
    const c = alongX ? (y0 + y1) / 2 : (x0 + x1) / 2;          // centre line across wall
    const [a0, a1] = alongX ? [x0, x1] : [y0, y1];
    const pane = (s0, s1, z0, z1, t, color, kind = 'glass', id = o.id) => {
      const m = alongX ? boxMesh(s0, c - t / 2, s1, c + t / 2, z0, z1, color) : boxMesh(c - t / 2, s0, c + t / 2, s1, z0, z1, color);
      if (kind === 'glass') glassPane(m);
      return add(id, kind, m);
    };
    const frameBar = (s0, s1, z0, z1, id) => pane(s0, s1, z0, z1, 8, TINT.frame, 'frame', id);
    const f = 6;                                                // frame width
    const outline = () => {
      frameBar(a0, a0 + f, o.sill, o.head, `${o.id}_fl`); frameBar(a1 - f, a1, o.sill, o.head, `${o.id}_fr`);
      frameBar(a0, a1, o.head - f, o.head, `${o.id}_ft`);
      if (o.sill > (o.type === 'garage_door' ? -999 : 0)) frameBar(a0, a1, o.sill, o.sill + f, `${o.id}_fb`);
    };
    if (o.type === 'window' || o.type === 'sliding' || o.type === 'curtain' || o.type === 'glass_partition') {
      pane(a0, a1, o.sill, o.head, 2, TINT.glass, 'glass');
      outline();
      for (const m of (o.mullions || [])) frameBar(m - 3, m + 3, o.sill, o.head, `${o.id}_m${m}`);
      if (o.transom) frameBar(a0, a1, o.transom - 4, o.transom + 4, `${o.id}_tr`);
      if (o.type === 'sliding') frameBar((a0 + a1) / 2 - 3, (a0 + a1) / 2 + 3, o.sill, o.head, `${o.id}_mid`);
    } else if (o.type === 'door') {
      pane(a0 + f, a1 - f, 0, o.head - f, 5, TINT.door, 'door');
      outline();
    } else if (o.type === 'double_door') {
      const mid = (a0 + a1) / 2;
      pane(a0 + f, a1 - f, 0, o.head - f, 2, TINT.glass, 'glass');
      outline(); frameBar(mid - 4, mid + 4, 0, o.head, `${o.id}_mid`);
      frameBar(a0, a1, 0, 12, `${o.id}_kick`);
    } else if (o.type === 'garage_door') {
      pane(a0, a1, o.sill, o.head, 6, TINT.garage_door, 'door');
      for (let z = o.sill + 50; z < o.head; z += 50) frameBar(a0, a1, z - 1, z + 1, `${o.id}_g${z}`);
    }
  }

  // ---------------------------------------------------------- furniture
  for (const f of plan.furniture) {
    if (f.kind === 'car' && opts.car === false) continue;
    const col = TINT[f.kind] ?? 0x888888;
    if (f.shape === 'cyl') {
      const [cx, cy] = f.center;
      if (f.kind === 'jacuzzi') {
        const outer = new THREE.Mesh(new THREE.CylinderGeometry(f.r, f.r, f.h, 64), mat(col));
        outer.position.set(cx, f.z0 + f.h / 2, cy); add(f.id, f.kind, outer);
        const water = new THREE.Mesh(new THREE.CylinderGeometry(f.r - 14, f.r - 14, 2, 64), mat(TINT.water, { roughness: 0.1 }));
        water.position.set(cx, f.z0 + f.h - 12, cy); add(`${f.id}_water`, 'water', water);
      } else {
        const m = new THREE.Mesh(new THREE.CylinderGeometry(f.r, f.r * 0.8, f.h, 40), mat(col));
        m.position.set(cx, f.z0 + f.h / 2, cy); add(f.id, f.kind, m);
      }
      continue;
    }
    let [x0, y0, x1, y1] = f.rect;
    [x0, x1] = [Math.min(x0, x1), Math.max(x0, x1)]; [y0, y1] = [Math.min(y0, y1), Math.max(y0, y1)];
    const z0 = f.z0, z1 = f.z0 + f.h;
    const B = (a, b, c, d, e, g, color = col, id = f.id, kind = f.kind) => add(id, kind, boxMesh(a, b, c, d, e, g, color));
    // "back" edge = opposite of facing
    const back = { N: 'S', S: 'N', E: 'W', W: 'E' }[f.facing] || null;
    const strip = (side, t) => ({
      N: [x0, y0, x1, y0 + t], S: [x0, y1 - t, x1, y1], W: [x0, y0, x0 + t, y1], E: [x1 - t, y0, x1, y1],
    }[side]);
    switch (f.kind) {
      case 'sofa': case 'armchair': {
        B(x0, y0, x1, y1, z0, z0 + 42);
        const s = strip(back, 22); B(s[0], s[1], s[2], s[3], z0 + 42, z1, col, `${f.id}_back`);
        if (f.kind === 'armchair') {
          const side = (back === 'N' || back === 'S') ? ['W', 'E'] : ['N', 'S'];
          for (const sd of side) { const a = strip(sd, 12); B(a[0], a[1], a[2], a[3], z0 + 42, z0 + 62, col, `${f.id}_arm${sd}`); }
        }
        break;
      }
      case 'chair': {
        const s = 6; B(x0 + s, y0 + s, x1 - s, y1 - s, z0 + 42, z0 + 47);
        const b = strip(back, 5); B(b[0] + (back === 'N' || back === 'S' ? s : 0), b[1], b[2] - (back === 'N' || back === 'S' ? s : 0), b[3], z0 + 47, z1, col, `${f.id}_back`);
        for (const [lx, ly] of [[x0 + s, y0 + s], [x1 - s - 3, y0 + s], [x0 + s, y1 - s - 3], [x1 - s - 3, y1 - s - 3]])
          B(lx, ly, lx + 3, ly + 3, z0, z0 + 42, 0x1a1a1a, `${f.id}_leg`);
        break;
      }
      case 'stool': {
        const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2, r = (x1 - x0) / 2;
        const seat = new THREE.Mesh(new THREE.CylinderGeometry(r, r * 0.9, 6, 32), mat(col));
        seat.position.set(cx, z1 - 3, cy); add(f.id, f.kind, seat);
        for (const [lx, ly] of [[x0 + 4, y0 + 4], [x1 - 7, y0 + 4], [x0 + 4, y1 - 7], [x1 - 7, y1 - 7]])
          B(lx, ly, lx + 3, ly + 3, z0, z1 - 6, 0x6b4a32, `${f.id}_leg`);
        break;
      }
      case 'table': case 'coffee_table': {
        B(x0, y0, x1, y1, z1 - 5, z1);
        if (f.kind === 'table') { B(x0 + 30, (y0 + y1) / 2 - 15, x0 + 40, (y0 + y1) / 2 + 15, z0, z1 - 5, col, `${f.id}_leg`); B(x1 - 40, (y0 + y1) / 2 - 15, x1 - 30, (y0 + y1) / 2 + 15, z0, z1 - 5, col, `${f.id}_leg`); }
        else B(x0 + 5, y0 + 5, x1 - 5, y1 - 5, z0, z1 - 5, col, `${f.id}_base`);
        break;
      }
      case 'island': {
        B(x0, y0, x1, y0 + 57 * 1.05, z0, z1 - 4, TINT.island);              // body (to overhang line)
        B(x0, y0, x1, y1, z1 - 4, z1, TINT.counter_top, `${f.id}_top`);       // top incl. overhang
        break;
      }
      case 'counter': {
        B(x0, y0, x1, y1, z0 + 10, z1 - 4); B(x0, y0, x1, y1 - 6, z0, z0 + 10, 0x111111, `${f.id}_plinth`);
        B(x0, y0, x1, y1, z1 - 4, z1, TINT.counter_top, `${f.id}_top`);
        break;
      }
      case 'car': {
        B(x0, y0 + 10, x1, y1 - 10, z0 + 35, z0 + 115);                          // body
        B(x0 + 12, y0 + 120, x1 - 12, y1 - 60, z0 + 115, z1, col, `${f.id}_cabin`);   // boxy cabin
        for (const yy of [y0 + 75, y1 - 75]) for (const xx of [x0 - 2, x1 - 22]) {
          const wh = new THREE.Mesh(new THREE.CylinderGeometry(40, 40, 24, 32), mat(0x0b0b0b));
          wh.rotation.z = Math.PI / 2; wh.position.set(xx + 12, z0 + 40, yy); add(`${f.id}_wheel`, 'car', wh);
        }
        break;
      }
      case 'stair': B(x0, y0, x1, y1, z0, z1, TINT.stair); break;
      case 'glass': add(f.id, 'glass', glassPane(boxMesh(x0, y0, x1, y1, z0, z1, TINT.glass))); break;
      case 'tv': B(x0, y0, x1, y1, z0, z1, TINT.tv); break;
      default: B(x0, y0, x1, y1, z0, z1);
    }
  }

  // ---------------------------------------------------------- light (working rig)
  scene.add(new THREE.HemisphereLight(0xf6f1ea, 0x8a7663, 2.4));
  scene.add(new THREE.AmbientLight(0xfff4e8, 0.9));
  const sun = new THREE.DirectionalLight(0xffe2bf, 3.2);   // late-afternoon sun from SW-S, enters south + east glass
  sun.position.set(1700, 1100, 2600); sun.target.position.set(900, 0, 500);
  sun.castShadow = true; sun.shadow.mapSize.set(4096, 4096);
  Object.assign(sun.shadow.camera, { left: -1500, right: 1500, top: 1500, bottom: -1500, near: 10, far: 6000 });
  sun.shadow.bias = -0.0004;
  scene.add(sun, sun.target);

  return { scene, reg };
}

function glassPane(m) {
  m.material.transparent = true; m.material.opacity = 0.28; m.material.roughness = 0.05;
  m.castShadow = false; m.userData.glass = true;
  return m;
}

export function pointInPoly([x, y], poly) {
  let inside = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [xi, yi] = poly[i], [xj, yj] = poly[j];
    if (((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) inside = !inside;
  }
  return inside;
}

// ------------------------------------------------------------ camera
// Two-point perspective: camera stays level (verticals stay vertical, like a
// real arch-viz shift lens); framing up/down is done with lens shift.
export function makeCamera(c, W, H) {
  const cam = new THREE.PerspectiveCamera(10, W / H, 5, 8000);
  const [px, py, pz] = c.pos, [tx, ty] = c.look;
  cam.position.set(px, pz, py);
  cam.up.set(0, 1, 0);
  cam.lookAt(tx, pz, ty);
  cam.updateMatrixWorld();
  const near = cam.near;
  const halfW = Math.tan(THREE.MathUtils.degToRad(c.hfov / 2)) * near;
  const halfH = halfW * H / W;
  const shift = (c.shift_y || 0) * 2 * halfH;   // shift_y in frame heights
  cam.projectionMatrix.makePerspective(-halfW, halfW, halfH + shift, -halfH + shift, near, cam.far);
  cam.projectionMatrixInverse.copy(cam.projectionMatrix).invert();
  cam.updateProjectionMatrix = () => {};         // keep our shifted frustum
  return cam;
}

// ------------------------------------------------------------ passes
export function idColor(i) {   // deterministic, well-separated, never black/white
  const h = (i * 0.61803398875) % 1, s = 0.55 + 0.4 * ((i * 7) % 5) / 4, l = 0.35 + 0.3 * ((i * 3) % 4) / 3;
  return new THREE.Color().setHSL(h, s, l);
}

export function renderPasses(THREEref, plan, camDef, W, H, opts) {
  const out = {};
  const { scene, reg } = buildScene(plan, opts);
  const cam = makeCamera(camDef, W, H);

  // 1. guide pass (tinted clay, real shadows) — this is what the image model sees
  const r1 = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  r1.setSize(W, H); r1.shadowMap.enabled = true; r1.shadowMap.type = THREE.PCFSoftShadowMap;
  r1.toneMapping = THREE.ACESFilmicToneMapping; r1.toneMappingExposure = camDef.exposure || 1.0;
  r1.outputColorSpace = THREE.SRGBColorSpace;
  r1.render(scene, cam);
  out.guide = r1.domElement.toDataURL('image/png');

  // 2. line pass (black structural + furniture edges, occluded)
  const white = new THREE.MeshBasicMaterial({ color: 0xffffff, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1 });
  const lineGroup = new THREE.Group();
  const idLines = new THREE.Group();
  const ids = [...new Set(reg.map(r => r.id))];
  const idIndex = new Map(ids.map((id, i) => [id, i + 1]));
  const saved = [];
  for (const r of reg) {
    if (r.kind === 'exterior') { saved.push([r.mesh, r.mesh.material, r.mesh.visible]); r.mesh.visible = false; continue; }
    const eg = new THREE.EdgesGeometry(r.mesh.geometry, 30);
    const ls = new THREE.LineSegments(eg, new THREE.LineBasicMaterial({ color: 0x000000 }));
    ls.applyMatrix4(r.mesh.matrixWorld); lineGroup.add(ls);
    const ls2 = new THREE.LineSegments(eg, new THREE.LineBasicMaterial({ color: idColor(idIndex.get(r.id)) }));
    ls2.applyMatrix4(r.mesh.matrixWorld); idLines.add(ls2);
    saved.push([r.mesh, r.mesh.material, r.mesh.visible]);
    r.mesh.material = white; r.mesh.visible = !r.mesh.userData.glass || true;
  }
  scene.background = new THREE.Color(0xffffff);
  const lights = scene.children.filter(o => o.isLight);
  lights.forEach(l => l.visible = false);
  const r2 = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  r2.setSize(W, H); r2.outputColorSpace = THREE.LinearSRGBColorSpace;
  scene.add(lineGroup); r2.render(scene, cam); out.lines = r2.domElement.toDataURL('image/png');
  scene.remove(lineGroup);

  // 3. edge-ID pass (each element's edges in its own flat colour, no AA)
  const r3 = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true });
  r3.setSize(W, H); r3.outputColorSpace = THREE.LinearSRGBColorSpace;
  scene.add(idLines); r3.render(scene, cam); out.edge_ids = r3.domElement.toDataURL('image/png');
  scene.remove(idLines);

  // 4. surface-ID pass (flat colour per element) -> visibility table
  for (const r of reg) r.mesh.material = new THREE.MeshBasicMaterial({ color: idColor(idIndex.get(r.id)) });
  // exterior hidden; glass is transparent in reality, so it must not occlude what is behind it
  for (const r of reg) if (r.kind === 'exterior' || r.mesh.userData.glass) r.mesh.visible = false;
  r3.render(scene, cam); out.surface_ids = r3.domElement.toDataURL('image/png');

  // 5. view-space normals + 6. linear depth (24-bit) -> true geometric edges in Python
  for (const r of reg) r.mesh.material = new THREE.MeshNormalMaterial();
  r3.render(scene, cam); out.normals = r3.domElement.toDataURL('image/png');
  const depthMat = new THREE.ShaderMaterial({
    vertexShader: 'varying float vD; void main(){ vec4 mv = modelViewMatrix*vec4(position,1.0); vD = -mv.z; gl_Position = projectionMatrix*mv; }',
    fragmentShader: 'varying float vD; void main(){ float d = clamp(vD/8000.0,0.0,0.99999); vec3 enc = fract(d*vec3(1.0,255.0,65025.0)); enc -= enc.yzz*vec3(1.0/255.0,1.0/255.0,0.0); gl_FragColor = vec4(enc,1.0); }',
  });
  for (const r of reg) r.mesh.material = depthMat;
  r3.render(scene, cam); out.depth = r3.domElement.toDataURL('image/png');

  out.legend = ids.map(id => {
    const c = idColor(idIndex.get(id));
    const kind = reg.find(r => r.id === id).kind;
    return { id, kind, rgb: [c.r, c.g, c.b].map(v => Math.round(v * 255)) };
  });
  out.camera = { ...camDef, W, H, projection: cam.projectionMatrix.elements, view: cam.matrixWorldInverse.elements };
  return out;
}

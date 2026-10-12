// Builds a metric (cm) three.js blockout from plan.json and renders the
// QA passes for one camera. Runs in headless Chromium (see render.mjs).
//
// Plan axes: x = east, y = south (drawing down), z = up.
// three axes: X = x, Y = z, Z = y   (right-handed, Y up)
import * as THREE from 'three';

// ------------------------------------------------------------ materials
// Every mesh carries ONE material key from design-system.json. The guide is
// tinted with that material's real colour, the prompt uses that material's one
// locked description, and a material-ID pass tells the prompt builder exactly
// which materials each camera sees. Same key -> same look in every view.
let DS = null;
const T = (key) => new THREE.Color(DS.materials[key]?.tint ?? '#888888').getHex();
const KIND_MAT = (f) => DS.id_materials[f.id] ?? DS.kind_materials[f.kind] ?? 'black_metal';

export function buildScene(plan, opts = {}, ds) {
  DS = ds;
  const SM = (style, part) => (DS.style_materials[style] || DS.style_materials.warm_wood_luxe)[part];
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xdfe8ee);
  const reg = [];                       // element registry: {id, kind, group}
  const add = (id, kind, mesh, matKey) => {
    mesh.userData.eid = id; mesh.userData.kind = kind; mesh.userData.mat = matKey ?? mesh.userData.mat;
    mesh.castShadow = true; mesh.receiveShadow = true;
    scene.add(mesh);
    reg.push({ id, kind, mesh });
    return mesh;
  };
  const mat = (hex, o = {}) => new THREE.MeshStandardMaterial({ color: hex, roughness: 0.85, metalness: 0, ...o });
  // axis-aligned box from plan rect + z range
  const boxMesh = (x0, y0, x1, y1, z0, z1, key, o) => {
    const color = typeof key === 'string' ? T(key) : key;
    const [ax, bx] = [Math.min(x0, x1), Math.max(x0, x1)], [ay, by] = [Math.min(y0, y1), Math.max(y0, y1)];
    const [az, bz] = [Math.min(z0, z1), Math.max(z0, z1)];
    const g = new THREE.BoxGeometry(Math.max(bx - ax, 0.5), Math.max(bz - az, 0.5), Math.max(by - ay, 0.5));
    const m = new THREE.Mesh(g, mat(color, o));
    m.position.set((ax + bx) / 2, (az + bz) / 2, (ay + by) / 2);
    if (typeof key === 'string') m.userData.mat = key;
    return m;
  };
  const L = plan.levels;
  const roomOf = (x, y, level) => plan.rooms.find(r => (r.level || 'ground') === (level || 'ground') && pointInPoly([x, y], r.polygon));

  // ---------------------------------------------------------- floors / ceilings
  for (const r of plan.rooms) {
    const shape = new THREE.Shape(r.polygon.map(([x, y]) => new THREE.Vector2(x, y)));
    const fg = new THREE.ShapeGeometry(shape); fg.rotateX(Math.PI / 2);   // y->Z
    const floor = new THREE.Mesh(fg, mat(T(SM(r.style, 'floor')), { side: THREE.DoubleSide }));
    floor.position.y = r.floor;
    add(`FLOOR_${r.id}`, 'floor', floor, SM(r.style, 'floor'));
    if (r.id === 'R_living') continue;                // living handled by void ceiling
    const cshape = new THREE.Shape(r.polygon.map(([x, y]) => new THREE.Vector2(x, y)));
    for (const [hx0, hy0, hx1, hy1] of (r.ceiling_holes || []))
      cshape.holes.push(new THREE.Path([new THREE.Vector2(hx0, hy0), new THREE.Vector2(hx0, hy1), new THREE.Vector2(hx1, hy1), new THREE.Vector2(hx1, hy0)]));
    const cg = new THREE.ShapeGeometry(cshape); cg.rotateX(Math.PI / 2);
    const ceil = new THREE.Mesh(cg, mat(T(SM(r.style, 'ceiling')), { side: THREE.DoubleSide }));
    ceil.position.y = r.ceiling;
    add(`CEIL_${r.id}`, 'ceiling', ceil, SM(r.style, 'ceiling'));
  }
  // double-height void: walnut ceiling. NO gallery - per the 1st-floor plan the void is closed by
  // plain walls (W_void_west_up, W_liv_north_up) running straight up.
  if (plan.void) {
    const v = plan.void.rect;
    add('CEIL_void', 'ceiling', boxMesh(v[0], v[1], v[2], v[3], plan.void.ceiling, plan.void.ceiling + 20, 'walnut_slats'));
  }
  for (const c of (plan.extra_ceilings || []))
    add(c.id, 'ceiling', boxMesh(c.rect[0], c.rect[1], c.rect[2], c.rect[3], c.z, c.z + 20, c.mat || 'walnut_slats'));
  for (const [i, [x0, y0, x1, y1]] of (plan.upper_voids || []).entries()) {
    const t = 2;
    // slab edge on each side of the opening - except where two voids meet (no floor between them)
    const others = (plan.upper_voids || []).filter((_, k) => k !== i);
    const inWall = (px, py) => plan.walls.some(w => w.z1 > L.slab_top && px > w.rect[0] && px < w.rect[2] && py > w.rect[1] && py < w.rect[3]);
    const open = (px, py) => inWall(px, py) || others.some(([a, b, c, d]) => px > a && px < c && py > b && py < d);
    const sides = [[x0, y0, x1, y0 + t, (x0 + x1) / 2, y0 - 3], [x0, y1 - t, x1, y1, (x0 + x1) / 2, y1 + 3],
                   [x0, y0, x0 + t, y1, x0 - 3, (y0 + y1) / 2], [x1 - t, y0, x1, y1, x1 + 3, (y0 + y1) / 2]];
    for (const [a, b, c, d, px, py] of sides) {
      if (!open(px, py)) { add(`SLAB_void${i}`, 'slab_edge', boxMesh(a, b, c, d, L.ceiling, L.slab_top, 'plaster_white')); continue; }
      // partly shared side: keep only the stretch that borders floor
      const along = (b === d - t || d - b === t) ? 'x' : 'y';
      const lo = along === 'x' ? a : b, hi = along === 'x' ? c : d;
      let s0 = null;
      for (let q = lo; q <= hi + 0.01; q += 2) {
        const qx = along === 'x' ? q : px, qy = along === 'x' ? py : q;
        const solid = q <= hi && !open(qx, qy);
        if (solid && s0 === null) s0 = q;
        if ((!solid || q > hi - 2) && s0 !== null) {
          const e = solid ? hi : q;
          if (e - s0 > 3) add(`SLAB_void${i}`, 'slab_edge', along === 'x' ? boxMesh(s0, b, e, d, L.ceiling, L.slab_top, 'plaster_white')
                                                                          : boxMesh(a, s0, c, e, L.ceiling, L.slab_top, 'plaster_white'));
          s0 = null;
        }
      }
    }
  }
  if (plan.site) {                      // per-plan exterior (hidden from the QA passes like every exterior mesh)
    for (const e of plan.site) {
      let m;
      if (e.rect) m = boxMesh(e.rect[0], e.rect[1], e.rect[2], e.rect[3], e.z[0], e.z[1], e.mat);
      else if (e.cyl) { m = new THREE.Mesh(new THREE.CylinderGeometry(e.cyl[2], e.cyl[2], e.z[1] - e.z[0], 16), mat(T(e.mat))); m.position.set(e.cyl[0], (e.z[0] + e.z[1]) / 2, e.cyl[1]); }
      else { m = new THREE.Mesh(new THREE.SphereGeometry(e.sphere[3], 20, 14), mat(T(e.mat))); m.position.set(e.sphere[0], e.sphere[2], e.sphere[1]); }
      add(e.id, 'exterior', m, e.mat);
    }
  } else {
    add('EXT_ground', 'exterior', boxMesh(-800, -800, 2400, 2200, -62, -61, 'lawn'));
    add('EXT_terrace', 'exterior', boxMesh(960, 985, 1600, 1250, -2, 0, 'stone_pot'));
  }

  // ---------------------------------------------------------- walls with openings
  for (const w of plan.walls) {
    const [x0, y0, x1, y1] = w.rect;
    const alongX = (x1 - x0) >= (y1 - y0);
    const [a0, a1] = alongX ? [x0, x1] : [y0, y1];
    const cuts = [];
    for (const o of plan.openings) {
      const r = o.rect;
      const ix = Math.min(x1, r[2]) - Math.max(x0, r[0]), iy = Math.min(y1, r[3]) - Math.max(y0, r[1]);
      if (ix > 0.5 && iy > 0.5 && o.head > w.z0 + 0.5 && o.sill < w.z1 - 0.5) {   // must overlap in height too
        const [b0, b1] = alongX ? [r[0], r[2]] : [r[1], r[3]];
        cuts.push({ a: Math.max(a0, b0), b: Math.min(a1, b1), sill: Math.max(o.sill, w.z0), head: Math.min(o.head, w.z1) });
      }
    }
    cuts.sort((p, q) => p.a - q.a);
    // two-sided walls: each half of the thickness takes the colour of the room it
    // faces, sampled every 10 cm along the wall so long walls change finish at
    // room boundaries (stone in the spa, timber in the sauna, plaster in the living)
    const colorAt = (along, side) => {      // returns a material key
      if (w.kind === 'box') return DS.id_materials[w.id] ?? 'box_slats';
      const px = alongX ? along : (side < 0 ? x0 - 15 : x1 + 15);
      const py = alongX ? (side < 0 ? y0 - 15 : y1 + 15) : along;
      const r = roomOf(px, py, w.level);
      return r ? SM(r.style, 'wall') : null;
    };
    const mx = (x0 + x1) / 2, my = (y0 + y1) / 2;
    const half = (s0, s1, z0, z1, side, id) => {
      // sample; where a sample hits a partition (no room) inherit the nearest
      // sampled colour on the same side, so corners don't get stray exterior slivers
      const cells = [];
      for (let p = s0; p < s1 - 0.01; p += 2.5) {
        const q = Math.min(s1, p + 2.5);
        cells.push({ a: p, b: q, c: colorAt((p + q) / 2, side) });
      }
      for (let i = 0; i < cells.length; i++) if (cells[i].c == null) {
        for (let d = 1; d < cells.length; d++) {
          const n = cells[i - d]?.c ?? cells[i + d]?.c;
          if (n != null) { cells[i].c = n; break; }
        }
        cells[i].c ??= colorAt((cells[i].a + cells[i].b) / 2, -side) ?? 'plaster_greige';
      }
      const runs = [];
      for (const cl of cells) {
        if (runs.length && runs[runs.length - 1].c === cl.c) runs[runs.length - 1].b = cl.b;
        else runs.push({ ...cl });
      }
      for (const r of runs) {
        // 1 cm overlap in every direction seals hairline seams that leak sunlight
        const e = 1;
        const m = alongX ? boxMesh(r.a - e, side < 0 ? y0 - e : my, r.b + e, side < 0 ? my : y1 + e, z0 - e, z1 + e, r.c)
                         : boxMesh(side < 0 ? x0 - e : mx, r.a - e, side < 0 ? mx : x1 + e, r.b + e, z0 - e, z1 + e, r.c);
        add(id, 'wall', m);
      }
    };
    const seg = (s0, s1, z0, z1, tag) => {
      if (s1 - s0 < 0.5 || z1 - z0 < 0.5) return;
      half(s0, s1, z0, z1, -1, `${w.id}${tag}`);
      half(s0, s1, z0, z1, +1, `${w.id}${tag}`);
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
    const frameBar = (s0, s1, z0, z1, id) => pane(s0, s1, z0, z1, 8, 'bronze_frame', 'frame', id);
    const f = 6;                                                // frame width
    const outline = () => {
      frameBar(a0, a0 + f, o.sill, o.head, `${o.id}_fl`); frameBar(a1 - f, a1, o.sill, o.head, `${o.id}_fr`);
      frameBar(a0, a1, o.head - f, o.head, `${o.id}_ft`);
      if (o.type === 'window') frameBar(a0, a1, o.sill, o.sill + f, `${o.id}_fb`);
    };
    if (o.type === 'glass_partition') {          // frameless sauna glass: pane + slim top/bottom channels only
      pane(a0, a1, o.sill, o.head, 1.2, 'glass', 'glass');
      frameBar(a0, a1, o.head - 2, o.head, `${o.id}_ft`); frameBar(a0, a1, 0, 2, `${o.id}_fb`);
      if (o.hinge) pane(a1 - 3, a1 - 2, 95, 125, 4, 'black_metal', 'frame', `${o.id}_pull`);
    } else if (o.type === 'window' || o.type === 'sliding' || o.type === 'curtain') {
      pane(a0, a1, o.sill, o.head, 2, 'glass', 'glass');
      outline();
      for (const m of (o.mullions || [])) frameBar(m - 3, m + 3, o.sill, o.head, `${o.id}_m${m}`);
      if (o.transom) frameBar(a0, a1, o.transom - 4, o.transom + 4, `${o.id}_tr`);
      if (o.type === 'sliding') frameBar((a0 + a1) / 2 - 3, (a0 + a1) / 2 + 3, o.sill, o.head, `${o.id}_mid`);
    } else if (o.type === 'door') {
      pane(a0 + f, a1 - f, o.sill, o.head - f, 5, 'walnut_door', 'door');
      outline();
    } else if (o.type === 'double_door') {
      const mid = (a0 + a1) / 2;
      pane(a0 + f, a1 - f, 0, o.head - f, 2, 'glass', 'glass');
      outline(); frameBar(mid - 4, mid + 4, 0, o.head, `${o.id}_mid`);
      frameBar(a0, a1, 0, 12, `${o.id}_kick`);
    } else if (o.type === 'garage_door') {
      pane(a0, a1, o.sill, o.head, 6, 'bronze_garage_door', 'door');
      for (let z = o.sill + 50; z < o.head; z += 50) frameBar(a0, a1, z - 1, z + 1, `${o.id}_g${z}`);
    }
  }

  // ---------------------------------------------------------- furniture
  for (const f of plan.furniture) {
    if ((f.kind === 'car' || f.kind === 'car_glass') && opts.car === false) continue;
    const col = KIND_MAT(f);
    if (f.shape === 'prism') {          // extruded polygon: axis z = plan polygon (x,y) raised z0..z0+h; axis x = (y,z) polygon, x0..x1
      const sh = new THREE.Shape(f.poly.map(([u, v]) => new THREE.Vector2(u, v)));
      // axis y = (x,z) polygon extruded over plan y0..y1 (profiles that run along plan x: cars, raked glass)
      const depth = f.axis === 'x' ? f.x1 - f.x0 : f.axis === 'y' ? f.y1 - f.y0 : f.h;
      const g = new THREE.ExtrudeGeometry(sh, { depth, bevelEnabled: false });
      g.applyMatrix4(f.axis === 'x' ? new THREE.Matrix4().set(0, 0, 1, f.x0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1)
                     : f.axis === 'y' ? new THREE.Matrix4().set(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, f.y0, 0, 0, 0, 1)
                                      : new THREE.Matrix4().set(1, 0, 0, 0, 0, 0, 1, f.z0, 0, 1, 0, 0, 0, 0, 0, 1));
      const m = new THREE.Mesh(g, mat(T(col), { side: THREE.DoubleSide }));
      if (f.kind === 'glass') glassPane(m);
      add(f.id, f.kind, m, col);
      continue;
    }
    if (f.shape === 'cyl') {
      const [cx, cy] = f.center;
      if (f.kind === 'jacuzzi') {
        const outer = new THREE.Mesh(new THREE.CylinderGeometry(f.r, f.r, f.h, 64), mat(T(col)));
        outer.position.set(cx, f.z0 + f.h / 2, cy); add(f.id, f.kind, outer, col);
        const water = new THREE.Mesh(new THREE.CylinderGeometry(f.r - 14, f.r - 14, 2, 64), mat(T('water'), { roughness: 0.1 }));
        water.position.set(cx, f.z0 + f.h - 12, cy); add(`${f.id}_water`, 'water', water, 'water');
      } else {
        const m = new THREE.Mesh(new THREE.CylinderGeometry(f.r, f.r * 0.8, f.h, 40), mat(T(col)));
        m.position.set(cx, f.z0 + f.h / 2, cy); add(f.id, f.kind, m, col);
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
          B(lx, ly, lx + 3, ly + 3, z0, z0 + 42, 'black_metal', `${f.id}_leg`);
        break;
      }
      case 'stool': {
        const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2, r = (x1 - x0) / 2;
        const seat = new THREE.Mesh(new THREE.CylinderGeometry(r, r * 0.9, 6, 32), mat(T(col)));
        seat.position.set(cx, z1 - 3, cy); add(f.id, f.kind, seat, col);
        const bs = strip(back, 4); B(bs[0] + 4, bs[1], bs[2] - 4, bs[3], z1, z1 + 14, col, `${f.id}_back`);   // low back
        for (const [lx, ly] of [[x0 + 4, y0 + 4], [x1 - 7, y0 + 4], [x0 + 4, y1 - 7], [x1 - 7, y1 - 7]])
          B(lx, ly, lx + 3, ly + 3, z0, z1 - 6, 'walnut_panel', `${f.id}_leg`);
        break;
      }
      case 'table': case 'coffee_table': {
        B(x0, y0, x1, y1, z1 - 5, z1);
        if (f.kind === 'table') { B(x0 + 30, (y0 + y1) / 2 - 15, x0 + 40, (y0 + y1) / 2 + 15, z0, z1 - 5, col, `${f.id}_leg`); B(x1 - 40, (y0 + y1) / 2 - 15, x1 - 30, (y0 + y1) / 2 + 15, z0, z1 - 5, col, `${f.id}_leg`); }
        else B(x0 + 5, y0 + 5, x1 - 5, y1 - 5, z0, z1 - 5, col, `${f.id}_base`);
        break;
      }
      case 'island': {
        B(x0, y0, x1, y0 + 57 * 1.05, z0, z1 - 6, 'marble_island');            // body (to overhang line)
        B(x0, y0, x1, y1, z1 - 6, z1, 'marble_island', `${f.id}_top`);         // 6 cm top incl. overhang
        break;
      }
      case 'counter': {
        B(x0, y0, x1, y1, z0 + 10, z1 - 4); B(x0, y0, x1, y1 - 6, z0, z0 + 10, 'groove_dark', `${f.id}_plinth`);
        B(x0, y0, x1, y1, z1 - 4, z1, 'worktop_marble', `${f.id}_top`);
        break;
      }
      case 'car': {
        B(x0, y0 + 10, x1, y1 - 10, z0 + 35, z0 + 115);                          // body
        B(x0 + 12, y0 + 120, x1 - 12, y1 - 60, z0 + 115, z1, col, `${f.id}_cabin`);   // boxy cabin
        for (const yy of [y0 + 75, y1 - 75]) for (const xx of [x0 - 2, x1 - 22]) {
          const wh = new THREE.Mesh(new THREE.CylinderGeometry(40, 40, 24, 32), mat(T('black_metal')));
          wh.rotation.z = Math.PI / 2; wh.position.set(xx + 12, z0 + 40, yy); add(`${f.id}_wheel`, 'car', wh, 'black_metal');
        }
        break;
      }
      case 'glass': add(f.id, 'glass', glassPane(boxMesh(x0, y0, x1, y1, z0, z1, 'glass'))); break;
      case 'bed': {
        const im = (part, def) => DS.id_materials[`${f.id}_${part}`] ?? def;
        B(x0, y0, x1, y1, z0, z0 + 30, im('base', 'walnut_console'), `${f.id}_base`);
        B(x0 + 2, y0 + 2, x1 - 2, y1 - 2, z0 + 30, z0 + 50, im('linen', 'bed_linen'));
        const hb = { N: [x0, y1 - 8, x1, y1], S: [x0, y0, x1, y0 + 8], E: [x0, y0, x0 + 8, y1], W: [x1 - 8, y0, x1, y1] }[f.facing === 'S' ? 'S' : f.facing === 'N' ? 'N' : f.facing === 'E' ? 'E' : 'W'];
        B(hb[0], hb[1], hb[2], hb[3], z0, z0 + (f.head_h || 120), im('head', 'headboard_boucle'), `${f.id}_head`);
        const pl = f.facing === 'E' || f.facing === 'W';
        for (const k of [0.27, 0.73]) {               // two pillows near the headboard
          const cx = pl ? (f.facing === 'E' ? x0 + 30 : x1 - 30) : x0 + (x1 - x0) * k;
          const cy = pl ? y0 + (y1 - y0) * k : (f.facing === 'S' ? y0 + 30 : y1 - 30);
          B(cx - (pl ? 12 : 30), cy - (pl ? 30 : 12), cx + (pl ? 12 : 30), cy + (pl ? 30 : 12), z0 + 50, z0 + 62, im('pillow', 'pillow_white'), `${f.id}_pillow`);
        }
        const tb = pl ? (f.facing === 'E' ? [x1 - 45, y0 + 2, x1 - 2, y1 - 2] : [x0 + 2, y0 + 2, x0 + 45, y1 - 2]) : (f.facing === 'S' ? [x0 + 2, y1 - 45, x1 - 2, y1 - 2] : [x0 + 2, y0 + 2, x1 - 2, y0 + 45]);
        B(tb[0], tb[1], tb[2], tb[3], z0 + 50, z0 + 53, im('throw', 'throw_cognac'), `${f.id}_throw`);
        break;
      }
      default: B(x0, y0, x1, y1, z0, z1);
    }
  }

  // ---------------------------------------------------------- design layer (fixed decor + fittings)
  for (const d of (plan.design || [])) {
    if (opts.car === false && d.id.startsWith('D_car_')) continue;   // tyres, wheels, spare of a modelled car
    const key = d.mat, o = d.emissive ? null : {};
    const M = () => d.emissive ? new THREE.MeshBasicMaterial({ color: 0xfff2d6 }) : mat(T(key));
    let m;
    if (d.shape === 'box') {
      const [x0, y0, x1, y1] = d.rect;
      m = boxMesh(x0, y0, x1, y1, d.z[0], d.z[1], key);
      if (d.emissive) m.material = M();
    } else if (d.shape === 'cyl') {
      m = new THREE.Mesh(new THREE.CylinderGeometry(d.r, d.r, d.z[1] - d.z[0], 24), M());
      m.position.set(d.center[0], (d.z[0] + d.z[1]) / 2, d.center[1]);
    } else if (d.shape === 'sphere') {
      m = new THREE.Mesh(new THREE.SphereGeometry(d.r, 20, 14), M());
      m.position.set(d.center[0], d.center[2], d.center[1]);
    } else if (d.shape === 'torus') {     // axis = plan axis of the ring's normal: z (hanging flat), y / x (on a wall)
      m = new THREE.Mesh(new THREE.TorusGeometry(d.R, d.tube, 10, 96), new THREE.MeshBasicMaterial({ color: 0xfff6e8 }));
      const ax = d.axis || 'z';
      if (ax === 'z') m.rotation.x = Math.PI / 2; else if (ax === 'x') m.rotation.y = Math.PI / 2;
      m.position.set(d.center[0], d.center[2], d.center[1]);
    } else if (d.shape === 'disc') {      // flat round panel (mirror) facing plan axis d.axis
      m = new THREE.Mesh(new THREE.CylinderGeometry(d.r, d.r, d.t, 72), M());
      if (d.axis === 'y') m.rotation.x = Math.PI / 2; else if (d.axis === 'x') m.rotation.z = Math.PI / 2;
      m.position.set(d.center[0], d.center[2], d.center[1]);
    } else if (d.shape === 'seg') {       // thin bar between two 3D points lying on a surface with plan normal d.normal
      const a = new THREE.Vector3(d.p0[0], d.p0[2], d.p0[1]), b = new THREE.Vector3(d.p1[0], d.p1[2], d.p1[1]);
      m = new THREE.Mesh(new THREE.BoxGeometry(a.distanceTo(b), d.w, d.t), M());
      const xa = b.clone().sub(a).normalize();
      const n = { x: new THREE.Vector3(1, 0, 0), y: new THREE.Vector3(0, 0, 1), z: new THREE.Vector3(0, 1, 0) }[d.normal];
      const za = n.clone().sub(xa.clone().multiplyScalar(n.dot(xa))).normalize();
      m.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(xa, za.clone().cross(xa), za));
      m.position.copy(a).add(b).multiplyScalar(0.5);
    }
    if (d.mat === 'glass' || d.mat === 'smoked_glass') { m.material.transparent = true; m.material.opacity = d.mat === 'glass' ? 0.28 : 0.5; m.userData.glass = true; }
    if (d.kind === 'light' || d.emissive) m.castShadow = false;
    add(d.id, d.kind === 'exterior' ? 'exterior' : d.kind, m, key);
    if (d.kind === 'light' || d.emissive) m.castShadow = false;
  }

  // ---------------------------------------------------------- light (working rig)
  const dusk = opts.rig === 'dusk';      // first floor: just after sunset, interior LEDs carry the room
  if (dusk) scene.background = new THREE.Color(0xb7b4c4);
  scene.add(new THREE.HemisphereLight(dusk ? 0xc9d2e6 : 0xf6f1ea, 0x8a7663, dusk ? 2.2 : 2.4));
  scene.add(new THREE.AmbientLight(0xfff4e8, dusk ? 1.1 : 0.9));
  const sun = new THREE.DirectionalLight(dusk ? 0xffb27a : 0xffd7a8, dusk ? 1.6 : 3.4);   // golden hour, low sun from the south-west (design-system time_of_day)
  sun.position.set(-700, 800, 2500); sun.target.position.set(900, 0, 500);
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

export function renderPasses(THREEref, plan, camDef, W, H, opts, ds) {
  const out = {};
  const { scene, reg } = buildScene(plan, { ...opts, rig: camDef.rig }, ds);
  const cam = makeCamera(camDef, W, H);

  // 1. guide pass (tinted clay, real shadows) — this is what the image model sees
  const r1 = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  r1.setSize(W, H); r1.shadowMap.enabled = true; r1.shadowMap.type = THREE.PCFSoftShadowMap;
  r1.toneMapping = THREE.ACESFilmicToneMapping; r1.toneMappingExposure = camDef.exposure || 1.0;
  r1.outputColorSpace = THREE.SRGBColorSpace;
  r1.render(scene, cam);
  out.guide = r1.domElement.toDataURL('image/png');

  // 2. line pass (black structural + furniture edges, occluded)
  const white = new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1 });
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
  for (const r of reg) r.mesh.material = new THREE.MeshBasicMaterial({ color: idColor(idIndex.get(r.id)), side: THREE.DoubleSide });
  // exterior hidden; glass is transparent in reality, so it must not occlude what is behind it
  for (const r of reg) if (r.kind === 'exterior' || r.mesh.userData.glass) r.mesh.visible = false;
  r3.render(scene, cam); out.surface_ids = r3.domElement.toDataURL('image/png');

  // 4b. material-ID pass -> which locked materials this camera sees
  const mats = [...new Set(reg.map(r => r.mesh.userData.mat || 'unknown'))];
  for (const r of reg) r.mesh.material = new THREE.MeshBasicMaterial({ color: idColor(mats.indexOf(r.mesh.userData.mat || 'unknown') + 1), side: THREE.DoubleSide });
  r3.render(scene, cam); out.mat_ids = r3.domElement.toDataURL('image/png');
  out.mat_legend = mats.map((m, i) => { const c = idColor(i + 1); return { mat: m, rgb: [c.r, c.g, c.b].map(v => Math.round(v * 255)) }; });

  // 5. view-space normals + 6. linear depth (24-bit) -> true geometric edges in Python
  for (const r of reg) r.mesh.material = new THREE.MeshNormalMaterial({ side: THREE.DoubleSide });
  r3.render(scene, cam); out.normals = r3.domElement.toDataURL('image/png');
  const depthMat = new THREE.ShaderMaterial({
    side: THREE.DoubleSide,
    vertexShader: 'varying float vD; void main(){ vec4 mv = modelViewMatrix*vec4(position,1.0); vD = -mv.z; gl_Position = projectionMatrix*mv; }',
    fragmentShader: 'varying float vD; void main(){ float d = clamp(vD/8000.0,0.0,0.99999); vec3 enc = fract(d*vec3(1.0,255.0,65025.0)); enc -= enc.yzz*vec3(1.0/255.0,1.0/255.0,0.0); gl_FragColor = vec4(enc,1.0); }',
  });
  for (const r of reg) r.mesh.material = depthMat;
  r3.render(scene, cam); out.depth = r3.domElement.toDataURL('image/png');

  out.legend = ids.map(id => {
    const c = idColor(idIndex.get(id));
    const kind = reg.find(r => r.id === id).kind;
    const rr = reg.find(r => r.id === id);
    return { id, kind, mat: rr.mesh.userData.mat || null, rgb: [c.r, c.g, c.b].map(v => Math.round(v * 255)) };
  });
  out.camera = { ...camDef, W, H, projection: cam.projectionMatrix.elements, view: cam.matrixWorldInverse.elements };
  return out;
}

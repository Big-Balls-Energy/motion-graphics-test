// Motor 2.5D mínimo: rotaciones y proyección en perspectiva
export type V3 = {x: number; y: number; z: number};
export type P2 = {x: number; y: number; s: number; z: number; visible: boolean};

export const v3 = (x: number, y: number, z: number): V3 => ({x, y, z});

export const rotY = (p: V3, a: number): V3 => {
  const c = Math.cos(a);
  const s = Math.sin(a);
  return {x: p.x * c + p.z * s, y: p.y, z: -p.x * s + p.z * c};
};

export const rotX = (p: V3, a: number): V3 => {
  const c = Math.cos(a);
  const s = Math.sin(a);
  return {x: p.x, y: p.y * c - p.z * s, z: p.y * s + p.z * c};
};

export const rotZ = (p: V3, a: number): V3 => {
  const c = Math.cos(a);
  const s = Math.sin(a);
  return {x: p.x * c - p.y * s, y: p.x * s + p.y * c, z: p.z};
};

export type Cam = {fov?: number; cx?: number; cy?: number; z?: number};

export const project = (p: V3, cam: Cam = {}): P2 => {
  const fov = cam.fov ?? 1100;
  const z = p.z - (cam.z ?? 0);
  const d = fov + z;
  const visible = d > 40;
  const s = visible ? fov / d : 0;
  return {
    x: (cam.cx ?? 540) + p.x * s,
    y: (cam.cy ?? 960) + p.y * s,
    s,
    z,
    visible,
  };
};

export const lerp3 = (a: V3, b: V3, t: number): V3 => ({
  x: a.x + (b.x - a.x) * t,
  y: a.y + (b.y - a.y) * t,
  z: a.z + (b.z - a.z) * t,
});

// Distribución uniforme de puntos sobre una esfera
export const fibonacciSphere = (n: number, r: number): V3[] => {
  const pts: V3[] = [];
  const golden = Math.PI * (3 - Math.sqrt(5));
  for (let i = 0; i < n; i++) {
    const y = 1 - (i / (n - 1)) * 2;
    const rad = Math.sqrt(1 - y * y);
    const th = golden * i;
    pts.push({x: Math.cos(th) * rad * r, y: y * r, z: Math.sin(th) * rad * r});
  }
  return pts;
};

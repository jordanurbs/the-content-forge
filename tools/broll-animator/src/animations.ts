import { interpolate, Easing } from "remotion";

/**
 * Seeded PRNG (mulberry32). Takes a 32-bit seed, returns a function
 * that produces deterministic floats in [0, 1) on each call.
 */
function mulberry32(seed: number): () => number {
  let s = seed | 0;
  return () => {
    s = (s + 0x6d2b79f5) | 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Map a [0,1) float to a range */
function mapRange(v: number, min: number, max: number): number {
  return min + v * (max - min);
}

/** Pick sign: -1 or +1 */
function sign(v: number): number {
  return v < 0.5 ? -1 : 1;
}

const EASING = Easing.inOut(Easing.sin);
const CLAMP = {
  extrapolateLeft: "clamp" as const,
  extrapolateRight: "clamp" as const,
  easing: EASING,
};

/**
 * Generate a unique animation from a hash.
 *
 * Weighted heavily toward 3D perspective moves (tilt, orbit).
 * Drifts are single-axis only — horizontal OR vertical, never diagonal.
 * No rotateZ. All parameters randomized within safe ranges.
 *
 * Distribution:
 *   60% 3D perspective (tilt + orbit)
 *   20% zoom (in/out with optional single-axis drift)
 *   20% single-axis drift (horizontal or vertical based on hash)
 */
export function getAnimation(
  hash: number,
  frame: number,
  totalFrames: number
): string {
  const rng = mulberry32(hash);

  // Pick base motion class — 60% 3D, 20% zoom, 20% drift
  const motionRoll = rng();
  const motionType =
    motionRoll < 0.30
      ? 0 // 3D tilt
      : motionRoll < 0.60
        ? 1 // orbit
        : motionRoll < 0.80
          ? 2 // zoom
          : 3; // single-axis drift

  // Shared randomized parameters
  const perspective = mapRange(rng(), 700, 1100);
  const dirX = sign(rng());
  const dirY = sign(rng());
  const speedMul = mapRange(rng(), 0.7, 1.3);

  let transform: string;

  switch (motionType) {
    case 0: {
      // 3D TILT — rotateY + rotateX, with optional single-axis drift
      const ryMag = mapRange(rng(), 1.5, 4.5) * speedMul;
      const rxMag = mapRange(rng(), 1.0, 3.0) * speedMul;
      const tiltScale = mapRange(rng(), 1.08, 1.14);
      const persp = Math.min(perspective, 900);

      const ry = interpolate(
        frame,
        [0, totalFrames],
        [-ryMag * dirX, ryMag * dirX],
        CLAMP
      );
      const rx = interpolate(
        frame,
        [0, totalFrames],
        [-rxMag * dirY, rxMag * dirY],
        CLAMP
      );

      // 50% chance of a subtle horizontal drift layered on
      const addDrift = rng() > 0.5;
      const driftMag = addDrift ? mapRange(rng(), 3, 12) : 0;
      const tx = driftMag
        ? interpolate(
            frame,
            [0, totalFrames],
            [-driftMag * dirX, driftMag * dirX],
            CLAMP
          )
        : 0;

      transform = `perspective(${persp}px) scale(${tiltScale}) rotateY(${ry}deg) rotateX(${rx}deg) translateX(${tx}px)`;
      break;
    }

    case 1: {
      // ORBIT — rotateY + horizontal drift (like rotating around a vertical axis)
      const orbitMag = mapRange(rng(), 1.5, 4.0) * speedMul;
      const driftMag = mapRange(rng(), 5, 20) * speedMul;
      const orbitScale = mapRange(rng(), 1.07, 1.13);
      const persp = Math.min(perspective, 900);

      const ry = interpolate(
        frame,
        [0, totalFrames],
        [-orbitMag * dirX, orbitMag * dirX],
        CLAMP
      );
      const tx = interpolate(
        frame,
        [0, totalFrames],
        [-driftMag * dirX, driftMag * dirX],
        CLAMP
      );

      // 30% chance of subtle rotateX added
      const addTiltX = rng() > 0.7;
      const rxMag = addTiltX ? mapRange(rng(), 0.5, 1.5) : 0;
      const rx = rxMag
        ? interpolate(
            frame,
            [0, totalFrames],
            [-rxMag * dirY, rxMag * dirY],
            CLAMP
          )
        : 0;

      transform = `perspective(${persp}px) scale(${orbitScale}) rotateY(${ry}deg)${rx ? ` rotateX(${rx}deg)` : ""} translateX(${tx}px)`;
      break;
    }

    case 2: {
      // ZOOM — in or out, with optional single-axis drift
      const zoomIn = rng() > 0.5;
      const baseScale = mapRange(rng(), 1.06, 1.12);
      const zoomRange = mapRange(rng(), 0.05, 0.12) * speedMul;
      const startScale = zoomIn ? baseScale : baseScale + zoomRange;
      const endScale = zoomIn ? baseScale + zoomRange : baseScale;

      const s = interpolate(
        frame,
        [0, totalFrames],
        [startScale, endScale],
        CLAMP
      );

      // Optional single-axis drift during zoom (horizontal only)
      const addDrift = rng() > 0.5;
      const driftMag = addDrift ? mapRange(rng(), 4, 14) : 0;
      const tx = driftMag
        ? interpolate(
            frame,
            [0, totalFrames],
            [-driftMag * dirX, driftMag * dirX],
            CLAMP
          )
        : 0;

      transform = `perspective(${perspective}px) scale(${s}) translateX(${tx}px)`;
      break;
    }

    case 3: {
      // SINGLE-AXIS DRIFT — horizontal OR vertical, never both
      const baseScale = mapRange(rng(), 1.06, 1.12);
      const useHorizontal = rng() > 0.5;

      if (useHorizontal) {
        const magX = mapRange(rng(), 15, 40) * speedMul;
        const tx = interpolate(
          frame,
          [0, totalFrames],
          [-magX * dirX, magX * dirX],
          CLAMP
        );
        transform = `perspective(${perspective}px) scale(${baseScale}) translateX(${tx}px)`;
      } else {
        const magY = mapRange(rng(), 10, 25) * speedMul;
        const ty = interpolate(
          frame,
          [0, totalFrames],
          [-magY * dirY, magY * dirY],
          CLAMP
        );
        transform = `perspective(${perspective}px) scale(${baseScale}) translateY(${ty}px)`;
      }
      break;
    }

    default:
      transform = `scale(1.08)`;
  }

  return transform;
}

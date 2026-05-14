import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type { OutroCardProps } from "./card-types";

import { NAVY, GOLD, CYAN } from "./theme";
const GRID_COLOR = "rgba(0, 255, 255, 0.08)";
const GRID_LINE = "rgba(0, 255, 255, 0.15)";

const SynthGrid: React.FC = () => {
  const frame = useCurrentFrame();
  const drift = interpolate(frame, [0, 210], [0, 80], {
    extrapolateRight: "extend",
  });

  return (
    <div
      style={{
        position: "absolute",
        bottom: 0,
        left: "-50%",
        width: "200%",
        height: "55%",
        background: `
          linear-gradient(180deg, transparent 0%, ${GRID_COLOR} 100%),
          repeating-linear-gradient(90deg, ${GRID_LINE} 0px, transparent 1px, transparent 80px),
          repeating-linear-gradient(0deg, ${GRID_LINE} 0px, transparent 1px, transparent 80px)
        `,
        transform: `perspective(400px) rotateX(55deg) translateY(${drift}px)`,
        transformOrigin: "center top",
      }}
    />
  );
};

export const OutroCard: React.FC<OutroCardProps> = ({
  nextLessonTitle,
  nextLessonNumber,
  ctaText = "Subscribe to keep learning",
  brandLogo,
  brandName,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Everything fades out in the last 2 seconds (60 frames) for clean end-screen space
  const fadeOutStart = durationInFrames - 60;
  const globalFadeOut = interpolate(
    frame,
    [fadeOutStart, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Logo: fades in at top-center
  const logoSpring = spring({
    frame: frame - 5,
    fps,
    config: { damping: 18, stiffness: 80, mass: 0.7 },
  });

  const logoOpacity = interpolate(logoSpring, [0, 1], [0, 1]);
  const logoScale = interpolate(logoSpring, [0, 1], [0.8, 1]);

  // "Next Lesson:" label
  const labelSpring = spring({
    frame: frame - 25,
    fps,
    config: { damping: 16, stiffness: 100, mass: 0.5 },
  });

  const labelOpacity = interpolate(labelSpring, [0, 1], [0, 1]);
  const labelY = interpolate(labelSpring, [0, 1], [20, 0]);

  // Next lesson title
  const titleSpring = spring({
    frame: frame - 35,
    fps,
    config: { damping: 16, stiffness: 90, mass: 0.6 },
  });

  const titleOpacity = interpolate(titleSpring, [0, 1], [0, 1]);
  const titleX = interpolate(titleSpring, [0, 1], [100, 0]);

  // Next lesson number
  const numberSpring = spring({
    frame: frame - 45,
    fps,
    config: { damping: 18, stiffness: 90, mass: 0.5 },
  });

  const numberOpacity = interpolate(numberSpring, [0, 1], [0, 1]);

  // CTA text — pulses gently
  const ctaSpring = spring({
    frame: frame - 60,
    fps,
    config: { damping: 18, stiffness: 80, mass: 0.6 },
  });

  const ctaOpacity = interpolate(ctaSpring, [0, 1], [0, 1]);
  const ctaY = interpolate(ctaSpring, [0, 1], [15, 0]);

  // Subtle glow pulse on CTA after it appears
  const ctaPulse =
    frame > 70
      ? interpolate(Math.sin((frame - 70) * 0.08), [-1, 1], [0.4, 0.8])
      : 0.4;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: NAVY,
        overflow: "hidden",
        fontFamily: "'SH Pinscher', sans-serif",
      }}
    >
      <style>
        {`
          /* Custom 'SH Pinscher' display font not shipped by default. Drop SHPinscher-Regular.otf (or your own display font) into public/fonts/ and re-enable this @font-face block. The card will gracefully fall back to sans-serif. */
          @font-face {
            font-family: 'Courier Prime Code';
            src: url('${staticFile("fonts/Courier Prime Code.ttf")}') format('truetype');
            font-weight: normal;
          }
        `}
      </style>

      {/* Synthwave grid floor */}
      <SynthGrid />

      {/* Vignette */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.6) 100%)",
          pointerEvents: "none",
        }}
      />

      {/* Content container — fades out for end-screen */}
      <div style={{ opacity: globalFadeOut }}>
        {/* brand logo — top center (only rendered if brandLogo prop set) */}
        {brandLogo && (
          // @ts-expect-error Remotion v4 Img placeholder type strictness
          <Img
            src={staticFile(brandLogo)}
            style={{
              position: "absolute",
              width: 80,
              height: 80,
              left: "50%",
              top: 60,
              transform: `translateX(-50%) scale(${logoScale})`,
              opacity: logoOpacity,
            }}
          />
        )}

        {/* Center content block */}
        <div
          style={{
            position: "absolute",
            top: "28%",
            left: 120,
            right: 120,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          {/* "Next Lesson:" label */}
          <div
            style={{
              fontSize: 28,
              color: "rgba(255, 255, 255, 0.6)",
              fontFamily: "'Courier Prime Code', monospace",
              letterSpacing: 6,
              textTransform: "uppercase",
              opacity: labelOpacity,
              transform: `translateY(${labelY}px)`,
            }}
          >
            Next Lesson:
          </div>

          {/* Next lesson title */}
          <div
            style={{
              fontSize: 64,
              color: GOLD,
              fontFamily: "'SH Pinscher', sans-serif",
              textAlign: "center",
              lineHeight: 1.15,
              marginTop: 24,
              opacity: titleOpacity,
              transform: `translateX(${titleX}px)`,
              textShadow: `0 0 30px rgba(255, 215, 0, 0.4)`,
              maxWidth: 1400,
            }}
          >
            {nextLessonTitle}
          </div>

          {/* Next lesson number */}
          <div
            style={{
              fontSize: 28,
              color: CYAN,
              fontFamily: "'Courier Prime Code', monospace",
              marginTop: 16,
              opacity: numberOpacity,
              textShadow: `0 0 20px rgba(0, 255, 255, 0.5)`,
              letterSpacing: 4,
            }}
          >
            {nextLessonNumber}
          </div>

          {/* Divider line */}
          <div
            style={{
              width: 200,
              height: 1,
              background: `linear-gradient(90deg, transparent, ${CYAN}, transparent)`,
              marginTop: 48,
              opacity: ctaOpacity,
            }}
          />

          {/* CTA text */}
          <div
            style={{
              fontSize: 36,
              color: GOLD,
              fontFamily: "'SH Pinscher', sans-serif",
              marginTop: 32,
              opacity: ctaOpacity,
              transform: `translateY(${ctaY}px)`,
              textShadow: `0 0 ${ctaPulse * 40}px rgba(255, 215, 0, ${ctaPulse})`,
              letterSpacing: 2,
            }}
          >
            {ctaText}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

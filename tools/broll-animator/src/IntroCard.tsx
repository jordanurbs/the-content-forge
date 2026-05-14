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
import type { IntroCardProps } from "./card-types";

import { NAVY, GOLD, CYAN } from "./theme";
const GRID_COLOR = "rgba(0, 255, 255, 0.08)";
const GRID_LINE = "rgba(0, 255, 255, 0.15)";

/**
 * Synthwave perspective grid floor rendered as CSS.
 * Animates slowly toward camera via translateZ.
 */
const SynthGrid: React.FC = () => {
  const frame = useCurrentFrame();
  const drift = interpolate(frame, [0, 150], [0, 60], {
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

export const IntroCard: React.FC<IntroCardProps> = ({
  lessonTitle,
  moduleNumber,
  subtitle,
  brandLogo,
  brandName,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Logo: fades in at center, then scales down + moves to top-left
  const logoFadeIn = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const logoTransition = spring({
    frame: frame - 30,
    fps,
    config: { damping: 18, stiffness: 80, mass: 0.8 },
  });

  const logoScale = interpolate(logoTransition, [0, 1], [0.5, 0.12]);
  const logoX = interpolate(logoTransition, [0, 1], [960, 80]);
  const logoY = interpolate(logoTransition, [0, 1], [440, 50]);

  // Title: slides in from right after logo settles
  const titleSpring = spring({
    frame: frame - 50,
    fps,
    config: { damping: 16, stiffness: 100, mass: 0.6 },
  });

  const titleX = interpolate(titleSpring, [0, 1], [200, 0]);
  const titleOpacity = interpolate(titleSpring, [0, 1], [0, 1]);

  // Module number: fades in below title
  const moduleSpring = spring({
    frame: frame - 65,
    fps,
    config: { damping: 18, stiffness: 90, mass: 0.5 },
  });

  const moduleY = interpolate(moduleSpring, [0, 1], [20, 0]);
  const moduleOpacity = interpolate(moduleSpring, [0, 1], [0, 1]);

  // Subtitle (optional): fades in last
  const subtitleSpring = spring({
    frame: frame - 75,
    fps,
    config: { damping: 18, stiffness: 90, mass: 0.5 },
  });

  const subtitleOpacity = interpolate(subtitleSpring, [0, 1], [0, 1]);
  const subtitleY = interpolate(subtitleSpring, [0, 1], [15, 0]);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: NAVY,
        overflow: "hidden",
        fontFamily: "'SH Pinscher', sans-serif",
      }}
    >
      {/* @font-face declarations */}
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

      {/* Subtle vignette overlay */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.6) 100%)",
          pointerEvents: "none",
        }}
      />

      {/* Logo — starts centered, animates to top-left corner (skipped if no brandLogo) */}
      {brandLogo && (
        // @ts-expect-error Remotion v4 Img placeholder type strictness
        <Img
          src={staticFile(brandLogo)}
          style={{
            position: "absolute",
            width: 400,
            height: 400,
            left: logoX - 200,
            top: logoY - 200,
            transform: `scale(${logoScale})`,
            transformOrigin: "center center",
            opacity: logoFadeIn,
          }}
        />
      )}

      {/* Title block — centered in the frame */}
      <div
        style={{
          position: "absolute",
          top: "38%",
          left: 120,
          right: 120,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        {/* Lesson title */}
        <div
          style={{
            fontSize: 72,
            color: GOLD,
            fontFamily: "'SH Pinscher', sans-serif",
            fontWeight: "normal",
            textAlign: "center",
            lineHeight: 1.15,
            opacity: titleOpacity,
            transform: `translateX(${titleX}px)`,
            textShadow: `0 0 30px rgba(255, 215, 0, 0.4)`,
            maxWidth: 1400,
          }}
        >
          {lessonTitle}
        </div>

        {/* Module number */}
        <div
          style={{
            fontSize: 32,
            color: CYAN,
            fontFamily: "'Courier Prime Code', monospace",
            marginTop: 20,
            opacity: moduleOpacity,
            transform: `translateY(${moduleY}px)`,
            textShadow: `0 0 20px rgba(0, 255, 255, 0.5)`,
            letterSpacing: 4,
          }}
        >
          {moduleNumber}
        </div>

        {/* Optional subtitle */}
        {subtitle && (
          <div
            style={{
              fontSize: 28,
              color: "rgba(255, 255, 255, 0.7)",
              fontFamily: "'Courier Prime Code', monospace",
              marginTop: 16,
              opacity: subtitleOpacity,
              transform: `translateY(${subtitleY}px)`,
              letterSpacing: 2,
            }}
          >
            {subtitle}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};

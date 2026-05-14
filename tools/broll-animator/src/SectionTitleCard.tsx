import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type { SectionTitleCardProps } from "./card-types";

import { NAVY, GOLD, CYAN } from "./theme";
const GRID_COLOR = "rgba(0, 255, 255, 0.08)";
const GRID_LINE = "rgba(0, 255, 255, 0.15)";

const SynthGrid: React.FC = () => {
  const frame = useCurrentFrame();
  const drift = interpolate(frame, [0, 90], [0, 30], {
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

export const SectionTitleCard: React.FC<SectionTitleCardProps> = ({
  partLabel,
  title,
  subtitle,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Part label: fades in first
  const labelSpring = spring({
    frame: frame - 5,
    fps,
    config: { damping: 18, stiffness: 100, mass: 0.5 },
  });

  const labelOpacity = interpolate(labelSpring, [0, 1], [0, 1]);
  const labelY = interpolate(labelSpring, [0, 1], [20, 0]);

  // Title: slides in from right
  const titleSpring = spring({
    frame: frame - 15,
    fps,
    config: { damping: 16, stiffness: 90, mass: 0.6 },
  });

  const titleOpacity = interpolate(titleSpring, [0, 1], [0, 1]);
  const titleX = interpolate(titleSpring, [0, 1], [100, 0]);

  // Subtitle: fades in last
  const subtitleSpring = spring({
    frame: frame - 25,
    fps,
    config: { damping: 18, stiffness: 90, mass: 0.5 },
  });

  const subtitleOpacity = interpolate(subtitleSpring, [0, 1], [0, 1]);
  const subtitleY = interpolate(subtitleSpring, [0, 1], [15, 0]);

  // Divider line
  const dividerSpring = spring({
    frame: frame - 20,
    fps,
    config: { damping: 20, stiffness: 120, mass: 0.4 },
  });

  const dividerWidth = interpolate(dividerSpring, [0, 1], [0, 400]);
  const dividerOpacity = interpolate(dividerSpring, [0, 1], [0, 1]);

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

      {/* Center content block */}
      <div
        style={{
          position: "absolute",
          top: "30%",
          left: 120,
          right: 120,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        {/* Part label */}
        <div
          style={{
            fontSize: 32,
            color: CYAN,
            fontFamily: "'Courier Prime Code', monospace",
            letterSpacing: 6,
            textTransform: "uppercase",
            opacity: labelOpacity,
            transform: `translateY(${labelY}px)`,
            textShadow: `0 0 20px rgba(0, 255, 255, 0.5)`,
          }}
        >
          {partLabel}
        </div>

        {/* Divider line */}
        <div
          style={{
            width: dividerWidth,
            height: 2,
            background: `linear-gradient(90deg, transparent, ${GOLD}, transparent)`,
            marginTop: 20,
            marginBottom: 20,
            opacity: dividerOpacity,
          }}
        />

        {/* Title */}
        <div
          style={{
            fontSize: 72,
            color: GOLD,
            fontFamily: "'SH Pinscher', sans-serif",
            textAlign: "center",
            lineHeight: 1.15,
            opacity: titleOpacity,
            transform: `translateX(${titleX}px)`,
            textShadow: `0 0 30px rgba(255, 215, 0, 0.4)`,
            maxWidth: 1400,
          }}
        >
          {title}
        </div>

        {/* Subtitle */}
        {subtitle && (
          <div
            style={{
              fontSize: 28,
              color: "rgba(255, 255, 255, 0.7)",
              fontFamily: "'Courier Prime Code', monospace",
              marginTop: 20,
              opacity: subtitleOpacity,
              transform: `translateY(${subtitleY}px)`,
              letterSpacing: 2,
              textAlign: "center",
            }}
          >
            {subtitle}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};

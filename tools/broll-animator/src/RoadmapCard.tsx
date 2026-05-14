import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type { RoadmapCardProps } from "./card-types";

import { NAVY, GOLD, CYAN } from "./theme";
const GRID_COLOR = "rgba(0, 255, 255, 0.08)";
const GRID_LINE = "rgba(0, 255, 255, 0.15)";

const SynthGrid: React.FC = () => {
  const frame = useCurrentFrame();
  const drift = interpolate(frame, [0, 180], [0, 60], {
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

export const RoadmapCard: React.FC<RoadmapCardProps> = ({
  videoTitle,
  items,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Title: fades in first
  const titleSpring = spring({
    frame: frame - 5,
    fps,
    config: { damping: 16, stiffness: 100, mass: 0.6 },
  });

  const titleOpacity = interpolate(titleSpring, [0, 1], [0, 1]);
  const titleY = interpolate(titleSpring, [0, 1], [20, 0]);

  // Divider line
  const dividerSpring = spring({
    frame: frame - 20,
    fps,
    config: { damping: 20, stiffness: 120, mass: 0.4 },
  });

  const dividerWidth = interpolate(dividerSpring, [0, 1], [0, 500]);
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

      {/* Content container */}
      <div
        style={{
          position: "absolute",
          top: "15%",
          left: 200,
          right: 200,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        {/* Video title */}
        <div
          style={{
            fontSize: 48,
            color: GOLD,
            fontFamily: "'SH Pinscher', sans-serif",
            textAlign: "center",
            lineHeight: 1.2,
            opacity: titleOpacity,
            transform: `translateY(${titleY}px)`,
            textShadow: `0 0 30px rgba(255, 215, 0, 0.4)`,
            maxWidth: 1200,
          }}
        >
          {videoTitle}
        </div>

        {/* Divider */}
        <div
          style={{
            width: dividerWidth,
            height: 2,
            background: `linear-gradient(90deg, transparent, ${CYAN}, transparent)`,
            marginTop: 30,
            marginBottom: 40,
            opacity: dividerOpacity,
          }}
        />

        {/* Roadmap items */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 24,
            width: "100%",
            maxWidth: 1000,
          }}
        >
          {items.map((item, index) => {
            const itemDelay = 30 + index * 12;
            const itemSpring = spring({
              frame: frame - itemDelay,
              fps,
              config: { damping: 16, stiffness: 90, mass: 0.5 },
            });

            const itemOpacity = interpolate(itemSpring, [0, 1], [0, 1]);
            const itemX = interpolate(itemSpring, [0, 1], [80, 0]);

            // Subtle glow on the number
            const glowIntensity =
              frame > itemDelay + 15
                ? interpolate(
                    Math.sin((frame - itemDelay - 15) * 0.06),
                    [-1, 1],
                    [0.3, 0.6]
                  )
                : 0.3;

            return (
              <div
                key={index}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 24,
                  opacity: itemOpacity,
                  transform: `translateX(${itemX}px)`,
                }}
              >
                {/* Number badge */}
                <div
                  style={{
                    width: 52,
                    height: 52,
                    borderRadius: 12,
                    border: `2px solid ${CYAN}`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                    boxShadow: `0 0 ${glowIntensity * 30}px rgba(0, 255, 255, ${glowIntensity})`,
                  }}
                >
                  <div
                    style={{
                      fontSize: 28,
                      color: CYAN,
                      fontFamily: "'Courier Prime Code', monospace",
                      fontWeight: "bold",
                    }}
                  >
                    {index + 1}
                  </div>
                </div>

                {/* Item text */}
                <div
                  style={{
                    fontSize: 40,
                    color: "rgba(255, 255, 255, 0.9)",
                    fontFamily: "'SH Pinscher', sans-serif",
                    letterSpacing: 1,
                  }}
                >
                  {item}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

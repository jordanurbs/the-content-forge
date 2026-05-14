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
import type { YouTubeCtaCardProps } from "./card-types";

import { NAVY, GOLD, CYAN } from "./theme";
const GRID_COLOR = "rgba(0, 255, 255, 0.08)";
const GRID_LINE = "rgba(0, 255, 255, 0.15)";

const SynthGrid: React.FC = () => {
  const frame = useCurrentFrame();
  const drift = interpolate(frame, [0, 180], [0, 70], {
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

export const YouTubeCtaCard: React.FC<YouTubeCtaCardProps> = ({
  videoTitle,
  ctaText = "Watch the rest on YouTube",
  brandLogo,
  brandName,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Fade out in the last 30 frames for clean transition
  const fadeOutStart = durationInFrames - 30;
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

  // YouTube play icon: scales in
  const playSpring = spring({
    frame: frame - 20,
    fps,
    config: { damping: 14, stiffness: 120, mass: 0.5 },
  });

  const playScale = interpolate(playSpring, [0, 1], [0, 1]);
  const playOpacity = interpolate(playSpring, [0, 1], [0, 1]);

  // CTA text: slides up
  const ctaSpring = spring({
    frame: frame - 40,
    fps,
    config: { damping: 16, stiffness: 90, mass: 0.6 },
  });

  const ctaOpacity = interpolate(ctaSpring, [0, 1], [0, 1]);
  const ctaY = interpolate(ctaSpring, [0, 1], [20, 0]);

  // Video title: fades in below CTA
  const titleSpring = spring({
    frame: frame - 55,
    fps,
    config: { damping: 16, stiffness: 90, mass: 0.6 },
  });

  const titleOpacity = interpolate(titleSpring, [0, 1], [0, 1]);
  const titleY = interpolate(titleSpring, [0, 1], [15, 0]);

  // Pulsing glow on the play icon
  const playPulse =
    frame > 30
      ? interpolate(Math.sin((frame - 30) * 0.06), [-1, 1], [0.3, 0.7])
      : 0.3;

  // CTA text glow pulse
  const ctaPulse =
    frame > 50
      ? interpolate(Math.sin((frame - 50) * 0.08), [-1, 1], [0.4, 0.8])
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

      {/* Content container */}
      <div style={{ opacity: globalFadeOut }}>
        {/* brand logo -- top center (only rendered if brandLogo prop set) */}
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
            top: "25%",
            left: 120,
            right: 120,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          {/* YouTube play triangle (CSS) */}
          <div
            style={{
              width: 120,
              height: 120,
              borderRadius: 24,
              backgroundColor: "rgba(255, 0, 0, 0.9)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              transform: `scale(${playScale})`,
              opacity: playOpacity,
              boxShadow: `0 0 ${playPulse * 60}px rgba(255, 0, 0, ${playPulse})`,
            }}
          >
            {/* Play triangle */}
            <div
              style={{
                width: 0,
                height: 0,
                borderLeft: "45px solid white",
                borderTop: "28px solid transparent",
                borderBottom: "28px solid transparent",
                marginLeft: 10,
              }}
            />
          </div>

          {/* CTA text */}
          <div
            style={{
              fontSize: 52,
              color: GOLD,
              fontFamily: "'SH Pinscher', sans-serif",
              marginTop: 48,
              opacity: ctaOpacity,
              transform: `translateY(${ctaY}px)`,
              textShadow: `0 0 ${ctaPulse * 40}px rgba(255, 215, 0, ${ctaPulse})`,
              letterSpacing: 2,
              textAlign: "center",
            }}
          >
            {ctaText}
          </div>

          {/* Video title */}
          <div
            style={{
              fontSize: 32,
              color: CYAN,
              fontFamily: "'Courier Prime Code', monospace",
              marginTop: 24,
              opacity: titleOpacity,
              transform: `translateY(${titleY}px)`,
              textShadow: `0 0 20px rgba(0, 255, 255, 0.5)`,
              letterSpacing: 2,
              textAlign: "center",
              maxWidth: 1400,
            }}
          >
            {videoTitle}
          </div>

          {/* Divider line */}
          <div
            style={{
              width: 200,
              height: 1,
              background: `linear-gradient(90deg, transparent, ${CYAN}, transparent)`,
              marginTop: 40,
              opacity: titleOpacity,
            }}
          />

          {/* Subscribe hint */}
          <div
            style={{
              fontSize: 24,
              color: "rgba(255, 255, 255, 0.5)",
              fontFamily: "'Courier Prime Code', monospace",
              marginTop: 24,
              opacity: titleOpacity,
              letterSpacing: 4,
              textTransform: "uppercase",
            }}
          >
            {brandName}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

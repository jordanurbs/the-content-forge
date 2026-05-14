import React from "react";
import {
  AbsoluteFill,
  getInputProps,
  Img,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { getAnimation } from "./animations";
import type { BrollClipProps } from "./types";

const GREEN = "#00FF00";

export const BrollClip: React.FC<BrollClipProps> = (defaultProps) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const inputProps = getInputProps() as Partial<BrollClipProps>;
  const imageFile = inputProps.imageFile ?? defaultProps.imageFile;
  const hash = inputProps.hash ?? defaultProps.hash;

  const transform = getAnimation(hash, frame, durationInFrames);

  return (
    <AbsoluteFill style={{ backgroundColor: GREEN, overflow: "hidden" }}>
      <Img
        src={staticFile(imageFile)}
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: 1920,
          height: 1080,
          objectFit: "cover",
          transform,
          transformOrigin: "center center",
        }}
      />
    </AbsoluteFill>
  );
};

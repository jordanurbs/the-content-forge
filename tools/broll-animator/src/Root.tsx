import React from "react";
import { Composition, type CalculateMetadataFunction } from "remotion";
import { BrollClip } from "./BrollClip";
import { BrollClipSchema } from "./types";
import type { BrollClipProps } from "./types";
import { IntroCard } from "./IntroCard";
import { OutroCard } from "./OutroCard";
import { YouTubeCtaCard } from "./YouTubeCtaCard";
import { SectionTitleCard } from "./SectionTitleCard";
import { RoadmapCard } from "./RoadmapCard";
import { IntroCardSchema, OutroCardSchema, YouTubeCtaCardSchema, SectionTitleCardSchema, RoadmapCardSchema } from "./card-types";
import type { IntroCardProps, OutroCardProps, YouTubeCtaCardProps, SectionTitleCardProps, RoadmapCardProps } from "./card-types";

// Remotion v4: inputProps from CLI don't override defaultProps automatically.
// calculateMetadata merges them so --props works as expected.
const mergeProps = <T extends Record<string, unknown>>(): CalculateMetadataFunction<T> =>
  ({ props }) => ({ props });

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="BrollClip"
        component={BrollClip}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        schema={BrollClipSchema}
        defaultProps={
          {
            imageFile: "test.png",
            hash: 0,
          } satisfies BrollClipProps
        }
      />
      <Composition
        id="IntroCard"
        component={IntroCard}
        durationInFrames={120}
        fps={30}
        width={1920}
        height={1080}
        schema={IntroCardSchema}
        defaultProps={
          {
            lessonTitle: "Context Engineering",
            moduleNumber: "3.1.1",
          } satisfies IntroCardProps
        }
        calculateMetadata={mergeProps<IntroCardProps>()}
      />
      <Composition
        id="OutroCard"
        component={OutroCard}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
        schema={OutroCardSchema}
        defaultProps={
          {
            nextLessonTitle: "The CLAUDE.md File",
            nextLessonNumber: "3.1.2",
          } satisfies OutroCardProps
        }
        calculateMetadata={mergeProps<OutroCardProps>()}
      />
      <Composition
        id="YouTubeCtaCard"
        component={YouTubeCtaCard}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        schema={YouTubeCtaCardSchema}
        defaultProps={
          {
            videoTitle: "Watch the Full Video",
          } satisfies YouTubeCtaCardProps
        }
        calculateMetadata={mergeProps<YouTubeCtaCardProps>()}
      />
      <Composition
        id="SectionTitleCard"
        component={SectionTitleCard}
        durationInFrames={75}
        fps={30}
        width={1920}
        height={1080}
        schema={SectionTitleCardSchema}
        defaultProps={
          {
            partLabel: "Part 1",
            title: "GitHub Repo Management",
            subtitle: "Feed Your Website to OpenClaw",
          } satisfies SectionTitleCardProps
        }
        calculateMetadata={mergeProps<SectionTitleCardProps>()}
      />
      <Composition
        id="RoadmapCard"
        component={RoadmapCard}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        schema={RoadmapCardSchema}
        defaultProps={
          {
            videoTitle: "Manage Your Business with OpenClaw",
            items: [
              "GitHub Repo Management",
              "Knowledge Base Setup",
              "ACPX Protocol Installation",
              "Live Harness Demo",
            ],
          } satisfies RoadmapCardProps
        }
        calculateMetadata={mergeProps<RoadmapCardProps>()}
      />
    </>
  );
};

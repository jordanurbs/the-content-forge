import { z } from "zod";

// Common brand props all cards support. Pass `brandLogo` (filename in public/)
// to display a logo. Pass `brandName` to show a short brand label.
const brandProps = {
  brandLogo: z
    .string()
    .optional()
    .describe("Optional filename of brand logo image in public/ (e.g. 'logo.png')"),
  brandName: z
    .string()
    .optional()
    .describe("Optional short brand name displayed on the card"),
};

export const IntroCardSchema = z.object({
  lessonTitle: z.string().describe("Lesson title displayed on the intro card"),
  moduleNumber: z
    .string()
    .describe("Module/section/lesson number, e.g. '3.1.1'"),
  subtitle: z
    .string()
    .optional()
    .describe("Optional subtitle below the title"),
  ...brandProps,
});

export type IntroCardProps = z.infer<typeof IntroCardSchema>;

export const OutroCardSchema = z.object({
  nextLessonTitle: z
    .string()
    .describe("Title of the next lesson to tease"),
  nextLessonNumber: z
    .string()
    .describe("Number of the next lesson, e.g. '3.1.2'"),
  ctaText: z
    .string()
    .optional()
    .describe("Call-to-action text (defaults to 'Subscribe to keep learning')"),
  ...brandProps,
});

export type OutroCardProps = z.infer<typeof OutroCardSchema>;

export const YouTubeCtaCardSchema = z.object({
  videoTitle: z.string().describe("Video title displayed on the CTA card"),
  ctaText: z
    .string()
    .optional()
    .describe("Call-to-action text (defaults to 'Watch the rest on YouTube')"),
  ...brandProps,
});

export type YouTubeCtaCardProps = z.infer<typeof YouTubeCtaCardSchema>;

export const SectionTitleCardSchema = z.object({
  partLabel: z
    .string()
    .describe("Part label displayed above the title, e.g. 'Part 1' or 'Interlude'"),
  title: z.string().describe("Section title displayed prominently"),
  subtitle: z
    .string()
    .optional()
    .describe("Optional subtitle below the title"),
});

export type SectionTitleCardProps = z.infer<typeof SectionTitleCardSchema>;

export const RoadmapCardSchema = z.object({
  videoTitle: z.string().describe("Video title displayed at the top"),
  items: z
    .array(z.string())
    .describe("List of roadmap items (4-5 recommended)"),
});

export type RoadmapCardProps = z.infer<typeof RoadmapCardSchema>;

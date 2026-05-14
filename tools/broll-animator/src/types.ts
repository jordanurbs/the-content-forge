import { z } from "zod";

export const BrollClipSchema = z.object({
  imageFile: z.string().describe("Filename of the image in public/"),
  hash: z
    .number()
    .int()
    .min(0)
    .describe("djb2 hash of the filename — drives all randomization"),
});

export type BrollClipProps = z.infer<typeof BrollClipSchema>;

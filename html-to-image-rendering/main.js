const path = require("path");
const fs = require("fs").promises;
const HtmlConverter = require("./html_converter");

const VARIANT_DIMENSIONS = {
  variants_1: { width: 412, height: 1036 },
  variants_2: { width: 412, height: 958 },
  variants_3: { width: 412, height: 1808 },
  variants_4: { width: 412, height: 1072 },
  variants_5: { width: 412, height: 1240 },
  variants_6: { width: 412, height: 910 },
  variants_7: { width: 412, height: 983 },
};

async function processVariant(mainDir, variant, dimensions) {
  const inputDir = path.join(mainDir, variant);
  const outputDir = path.join(mainDir, "output", variant);

  try {
    await fs.access(inputDir);
    const files = await fs.readdir(inputDir);

    if (files.length === 0) {
      console.warn(`No files found in ${inputDir}. Skipping ${variant}`);
      return;
    }

    console.log(
      `Processing ${variant} with dimensions ${dimensions.width}x${dimensions.height}`
    );

    const converter = new HtmlConverter({
      inputDir,
      outputDir,
      imageFormat: "png",
      quality: 100,
      scale: 2,
      port: 3000,
    });

    await converter.initialize(dimensions.width, dimensions.height);
    await converter.processDirectory();
    console.log(`Completed processing for ${variant}`);
    await converter.close();
  } catch (error) {
    console.error(`Error processing ${variant}:`, error.message);
  }
}

async function main() {
  const mainDirectories = ["/path/to/root/directory"];
  const variants = Object.keys(VARIANT_DIMENSIONS);

  for (const mainDir of mainDirectories) {
    for (const variant of variants) {
      await processVariant(mainDir, variant, VARIANT_DIMENSIONS[variant]);
    }
  }

  console.log("All processing completed!");
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { processVariant, VARIANT_DIMENSIONS };

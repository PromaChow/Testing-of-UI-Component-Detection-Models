const express = require("express");

function createServer(options) {
  const app = express();

  app.use((req, res, next) => {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
    res.header("Access-Control-Allow-Headers", "*");
    next();
  });

  app.use((req, res, next) => {
    console.log("Request for:", req.path);
    next();
  });

  app.use(
    "/",
    express.static(options.inputDir, {
      dotfiles: "allow",
      extensions: ["html", "css", "js", "png", "jpg", "jpeg", "gif"],
      setHeaders: (res) => {
        res.set("Access-Control-Allow-Origin", "*");
      },
    })
  );

  return new Promise((resolve) => {
    const server = app.listen(options.port, () => {
      console.log(`Local server started on port ${options.port}`);
      console.log(`Serving files from: ${options.inputDir}`);
      resolve(server);
    });
  });
}

module.exports = { createServer };

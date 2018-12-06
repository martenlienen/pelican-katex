const process = require("process");

// Parse the command line arguments
let state = null;
let katex_options = {};
let katex_path = "./katex";
process.argv.forEach(function (arg) {
  if (state == "katex_path") {
    katex_path = arg;
    state = null;
  } else if (state == "katex_options") {
    try {
      katex_options = JSON.parse(arg);
    } catch (e) {
      process.stderr.write("--options is not a valid JSON object\n");
      process.exit(1);
    } finally {
      state = null;
    }
  } else {
    if (arg == "--katex") {
      state = "katex_path";
    } else if (arg == "--options") {
      state = "katex_options";
    } else {
      // Ignore unknown/unexpected arguments, for example the path to this
      // script
    }
  }
});

// Buffer the complete input
let chunks = [];
process.stdin.on("data", function (chunk) {
  chunks.push(chunk);
});

// Once all input has been read, compile it with katex
process.stdin.on("end", function () {
  const katex = require(katex_path);

  try {
    let latex = chunks.join("");
    let html = katex.renderToString(latex, katex_options);

    process.stdout.write(html);
  } catch (e) {
    process.stderr.write(e.message);
    process.exit(1);
  }
});

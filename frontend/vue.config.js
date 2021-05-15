// eslint-disable-next-line @typescript-eslint/no-var-requires
const path = require("path");

module.exports = {
  configureWebpack: {
    devServer: {
      headers: { "Access-Control-Allow-Origin": "*" },
    },
    resolve: {
      alias: {
        "@": path.resolve(__dirname),
      },
    },
  },
  devServer: {
    proxy: "http://localhost:8000",
  },
};

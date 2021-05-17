// eslint-disable-next-line @typescript-eslint/no-var-requires
const path = require("path");

module.exports = {
  chainWebpack: (config) => {
    config.plugin("html").tap((args) => {
      args[0].title = "Учёт техники ФКН";
      return args;
    });
  },
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
    proxy: {
      "^/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
};

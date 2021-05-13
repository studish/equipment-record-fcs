module.exports = {
  configureWebpack: {
    devServer: {
      headers: { "Access-Control-Allow-Origin": "*" },
    },
  },
  devServer: {
    proxy: "http://localhost:8000",
  },
};

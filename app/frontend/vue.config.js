module.exports = {
  devServer: {
    proxy: {
      '^/api': {
        target: 'http://localhost:8040',
        ws: true,
        changeOrigin: true
      },
    }
  }
}
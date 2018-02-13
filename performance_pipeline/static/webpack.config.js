var webpack = require("webpack");
module.exports = {
    entry: {
        app: "./src/index.js",
        vendor: ["angular",
                 "angular-ui-router"]
    },
    output: {
        path: __dirname + "/js",
        filename: "bundle.js"
    },
    plugins: [
         new webpack.optimize.CommonsChunkPlugin({ name: 'vendor', filename: 'vendor.bundle.js' })
    ]
};

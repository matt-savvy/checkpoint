module.exports = {
	entry: {
		'dispatch' : './app/dispatch.jsx',
		'checkpoint' : './app/checkpoint.jsx'
	},
	output: {
		path : __dirname,
		filename : './static/js/[name].js'
	},
	resolve: {
		modules: [__dirname, 'node_modules'],
		alias: {
		},
		extensions: ['*', '.js', '.jsx']
	},
	module: {
		rules: [
			{
				loader: 'babel-loader',
				query:{
					presets: ['react', 'es2015', 'stage-0']
				},
				test: /\.jsx?$/,
				exclude: /(node_modules|bower_components)/
			}
		]
	}
};
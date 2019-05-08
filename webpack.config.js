module.exports = {
  mode: 'development',
  entry: {
    company_dispatch: ['@babel/polyfill', './app/company_dispatch.jsx'],
    company_scoreboard: ['@babel/polyfill', './app/company_scoreboard.jsx'],
    dispatch_control: ['@babel/polyfill', './app/dispatch_control.jsx'],
    checkpoint: ['@babel/polyfill', './app/checkpoint.jsx'],
  },
  output: {
    path: __dirname,
    filename: './static/js/[name].js',
  },
  resolve: {
    modules: [__dirname, 'node_modules'],
    alias: {
      Message: './Message.jsx',
     Racer: './Racer.jsx',
     EnterRacer: './EnterRacer.jsx',
     Feedback: './Feedback.jsx',
     RacerSmall: './RacerSmall.jsx',
    },
    extensions: ['*', '.js', '.jsx'],
  },
  node: { fs: 'empty' },
  module: {
   rules: [
    {
     loader: 'babel-loader',
     query: {
      presets: ['@babel/preset-env', '@babel/preset-react'],
      plugins: ['@babel/plugin-proposal-class-properties'],
     },
     test: /\.jsx?$/,
     exclude: /(node_modules|bower_components)/,
    },
   ],
  },
};

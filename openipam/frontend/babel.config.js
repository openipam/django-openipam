const presets = ["@babel/preset-env", "@babel/preset-react"],

const plugins = [
	"@babel/plugin-proposal-class-properties",
	[
		'babel-plugin-import',
		{
			libraryName: '@mui/material',
			libraryDirectory: '',
			camel2DashComponentName: false,
		},
		'core',
	],
]

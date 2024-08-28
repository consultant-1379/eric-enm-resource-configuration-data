# RCD front-end details

## Project structure

```
.
├── Dockerfile
├── docs
├── index.html           Entry point of recursive dependency walking
├── jsconfig.json        Dummy file for IDEs
├── node_modules         Dependency folder (git ignored)
├── package-lock.json    Dependency details
├── package.json         Project configuration
├── public               Static files to be outputted
├── README.md
├── src
│  ├── App.vue           Main Component, contains the base layout of the site
│  ├── components        All the sub-components
│  ├── global.less       Globally applied style-sheets
│  ├── main.js           Main script, initializes Vue, component-routing, and the data-model
│  └── model             Data-model
└── vite.config.js       Bundler config
```

## Model

[`./model.md`](./model.md)


## Components

[`./components.md`](./components.md)


## Node Calculator

[`./nodecalc.md`](./nodecalc.md)

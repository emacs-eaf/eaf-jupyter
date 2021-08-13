### EAF Jupyter
<p align="center">
  <img width="800" src="./screenshot.png">
</p>

Jupyter application for the [Emacs Application Framework](https://github.com/emacs-eaf/emacs-application-framework).

### Load application

```Elisp
(add-to-list 'load-path "~/.emacs.d/site-lisp/eaf-jupyter/")
(require 'eaf-jupyter)
```

### Dependency List

| Package          | Description               |
| :--------        | :------                   |
| python-qtconsole | Provide RichJupyterWidget |

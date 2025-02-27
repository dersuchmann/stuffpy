# `stuffpy` - a library of Stuff Parts written in Python

You first need to know what **Stuff** is. Details on the `stuffpy` library in particular can be found further below.

## What is Stuff?

**Stuff** is a paradigm for organizing and transforming structured data. It is very much WIP, but I already use it effectively to organize my life.

A Stuff repo is a folder with the following structure:

```
your-folder/
 ├─ .stuff/
 │   ├─ src/
 │   ├─ stuff.yaml
 │   └─ typedefs.ytt.yaml
 ├─ .stuff-compiled/
 │   ├─ morphs/
 │   ├─ views/
 │   └─ data.json
 ├─ .stuff-static/
 ├─ .stuff-manifest.yaml
 └─ (... your original data ...)
```

The `.stuff/stuff.yaml` file should have the following structure:

```yaml
stuff: '0.1.0'
scope: a-unique-name-of-your-choosing-for-all-your-stuff-anywhere
name: a-name-for-this-particular-stuff-repo

validate: a-command-that-checks-whether-all-required-consistency-checks-hold
test: a-command-with-more-consistency-checks-for-your-morphs-and-views

morphs:
  morph-name:
    load: a-command-that-creates-a-morph-from-data.json
    save: a-command-that-saves-that-morph-back-to-data.json
  another-morph-name:
    load: a-command-that-creates-another-morph-from-data.json
    save: a-command-that-saves-that-other-morph-back-to-data.json

views:
  view-name:
    load: a-command-that-creates-a-view-from-data.json
  another-view-name:
    load: a-command-that-creates-another-view-from-data.json
```

The `.stuff/src/` directory is suggested as the place for the code necessary to run the commands that are listed in `stuff.yaml`.
The `.stuff` directory may contain arbitrary other subdirectories as well, so feel free to use Node.js, Python, Git, Nix flakes, etc. to manage your stuff repo at your leisure.
Note that when using many Stuff repos, you might want to organize the code needed for them into a single library of so called **Stuff Parts**.

(TODO: explain more)

The `.stuff-compiled/` directory contains the actual transformed data: `data.json` is the so called "canonical representation", while subfolders of `morphs/` and `views/` contain the data in other transformed formats.
**Morphs** are transformations that can be applied in both directions, while **views** are one-way (i.e. read-only) transformations.

The `.stuff-static/` directory is for data that is not transformed in any way by Stuff, but merely referenced, e.g. by file name.
Typically this is binary data such as image files.

(TODO: explain the purpose of `.stuff-manifest.yaml`)

(TODO: what else?)

## Setting up a Stuff repo

For now, you have to manually setup a Stuff repo. CLI tooling will be available in the future.

First, ensure `yq`, `ytt`, and `jtd-codegen` are available in your `PATH`.

(TODO: expand)

## What are Stuff Parts?

(TODO: expand)

## What is `stuffpy`?

(TODO: expand)


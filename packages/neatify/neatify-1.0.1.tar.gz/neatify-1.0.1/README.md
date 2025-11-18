# Neatify

A simple CLI tool to organize files in a folder by their extensions.

## Features

- Automatically organize files into folders by type (images, documents, videos, etc.)
- Manage custom extension mappings
- Add, remove, and list file extension categories
- Restore default extension mappings

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/anmoljhamb/neatify.git
cd neatify

# Install in development mode
pip install -e .
```

### Using pip

```bash
pip install neatify
```

## Getting Started

After installation, you'll need to set up your configuration file before organizing files.

1. **Generate the default configuration:**

```bash
   neatify default
```

This creates a comprehensive list of file extensions organized by categories (Images, Documents, Videos, etc.).

2. **Verify your configuration (optional):**

```bash
   neatify list
```

This shows all configured categories and their extensions.

3. **Organize your first folder:**

```bash
   neatify organise /path/to/folder
```

> **Note:** Running `neatify organise` without first running `neatify default` will fail because no configuration file exists yet.

## Usage

### Organize a Folder

```bash
neatify organise /path/to/folder
```

This will organize all files in the specified folder into subfolders based on their file types.

### List Extensions

View all configured file extension categories:

```bash
neatify list
```

### Add an Extension

Add a new extension to a category:

```bash
neatify add Image .webp
```

### Remove an Extension

Remove an extension from a category:

```bash
neatify remove Image .webp
```

### Remove a Category

Remove an entire category:

```bash
neatify rmcat oldcategory
```

### Clear All Extensions

Clear all extension mappings:

```bash
neatify clear
```

### Restore Defaults

Restore the default extension mappings:

```bash
neatify default
```

### Custom Extensions File

Use a custom extensions JSON file:

```bash
neatify --file custom_extensions.json organise /path/to/folder
```

## Examples

```bash
# Organize your Downloads folder
neatify organise ~/Downloads

# Add .svg to the image category
neatify add Image .svg

# View all extensions
neatify list

# Remove a category you don't need
neatify rmcat Audio
```

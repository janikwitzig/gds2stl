# GDS2STL

This repository provides a tool to convert GDSII files into 3D STL models. It is intended to visualize semiconductor layouts in three dimensions.

## Usage

The tool is intended to be used as a command-line application. You can specify the GDSII file to load, the configuration files for layers, and the output STL file.

First, you must install the required dependencies. You can do this using pip:

```bash
pip install -r requirements.txt
```

Then, you can run the main script with the following command:

```bash
python main.py <gds-path> --tech <tech-config> --config <user-config> -o <output-stl>
```

If you want, you can also specify a cut rectangle to only export a portion of the layout using the `--cut` option:

```bash
python main.py <gds-path> --tech <tech-config> --config <user-config> --cut xmin ymin xmax ymax -o <output-stl>
```

If you do not want to display the 3D model after generation, you can use the `--no-show` flag.

## Features

- Load GDSII files and extract the layout information into three dimensions
- Configurable layer properties such as height and color
- Support to logically combine gds layers

## Ideas for Improvement

- Add support to export layers as separate STL files
- Implement more advanced visualization options (e.g., textures, lighting)
- Optimize performance for large GDSII files

## Configuration

The configuration files are in JSON format. The files are separated according to their purpose.

### Technology Configuration

For each technology node, there is a `layers.json` configuration file that defines the gds layer and datatype mappings. The `tech.json` file defines how the layers are combined to eventually form active devices. For example, a GDS file usually specifies a p-type and n-type implant layer, which together with a diffusion layer live in the substrate.

Such that no intersecting geometries are created, the layers are logically combined. To subtract layer `diff` from layer `ptype`, use the syntax:

```json
{
  "subtract": {
    "ptype": ["diff"]
  }
}
```

Sometimes, it is desireable that one layer extends donwwards across multiple layers. Most often, this is a contact from the first metal to the diffusion layer and poly. To achieve this, use the `extend_down_to` syntax:

```json
{
{
  "extend_down_to": {
    "contact": ["poly", "diff"]
  }
}
}
```

### User Configuration

The user configuration specifies how to interpret and finally display/ouput the layers. Each layer can be assigned a color and a height in the 3D model. The colors are specified as RGBA arrays, the heights are given in micrometers. An example configuration is shown below:

```json
{
  "layers": {
    "diff": {
      "color": [255, 0, 0, 200],
      "height": 0.5
    },
    "ptype": {
      "color": [0, 0, 255, 200],
      "height": 0.5
    },
    "metal1": {
      "color": [255, 255, 0, 200],
      "height": 0.1
    }
  }
}
```

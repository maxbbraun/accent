#include <Python.h>
#include <numpy/arrayobject.h>

// Clamps a value to the range [0, 255].
#define CLAMP(x) ((x) < 0 ? 0 : (x) > 255 ? 255 : (x))

// Finds the closest matching color in the palette. `red`, `green`, and `blue`
// define the input color. `palette` is an array of size `num_colors` containing
// available RGB values. `closest_red`, `closest_green`, and `closest_blue`
// define the output color.
void find_closest(const uint8_t red, const uint8_t green, const uint8_t blue,
                  const uint8_t *palette, const uint32_t num_colors,
                  uint8_t *closest_red, uint8_t *closest_green,
                  uint8_t *closest_blue) {
  uint32_t min_distance = UINT32_MAX;

  // Compare to all colors in the palette and return the one with the shortest
  // Euclidean distance.
  for (uint32_t i = 0; i < num_colors; ++i) {
    uint8_t palette_red = palette[i * 3];
    uint8_t palette_green = palette[i * 3 + 1];
    uint8_t palette_blue = palette[i * 3 + 2];

    int32_t delta_red = (int32_t)red - palette_red;
    int32_t delta_green = (int32_t)green - palette_green;
    int32_t delta_blue = (int32_t)blue - palette_blue;
    uint32_t distance = delta_red * delta_red + delta_green * delta_green +
                        delta_blue * delta_blue;

    if (distance < min_distance) {
      *closest_red = palette_red;
      *closest_green = palette_green;
      *closest_blue = palette_blue;
      min_distance = distance;
    }
  }
}

// Runs the Floyd-Steinberg dithering algorithm on the image. `pixels` is an
// array of size `width` * `height` * 3 containing RGB values in row-major
// order. `palette` is an array of size `num_colors` containing available RGB
// values. The pixels are modified in place.
void floyd_steinberg(uint8_t *pixels, const uint32_t width,
                     const uint32_t height, const uint8_t *palette,
                     const uint32_t num_colors) {
  for (uint32_t y = 0; y < height; ++y) {
    for (uint32_t x = 0; x < width; ++x) {
      uint32_t i = (y * width + x) * 3;

      // Find the closest matching color in the palette.
      const uint8_t old_red = pixels[i];
      const uint8_t old_green = pixels[i + 1];
      const uint8_t old_blue = pixels[i + 2];
      uint8_t new_red, new_green, new_blue;
      find_closest(old_red, old_green, old_blue, palette, num_colors, &new_red,
                   &new_green, &new_blue);

      // Replace the current pixel with the closest matching color.
      pixels[i] = new_red;
      pixels[i + 1] = new_green;
      pixels[i + 2] = new_blue;

      // Calculate the residual error.
      const int32_t red_error = (int32_t)old_red - new_red;
      const int32_t green_error = (int32_t)old_green - new_green;
      const int32_t blue_error = (int32_t)old_blue - new_blue;
      int32_t red_residual, green_residual, blue_residual;

      // Propagate 7/16 of the residual error to (x + 1, y).
      if (x < width - 1) {
        i = (y * width + (x + 1)) * 3;
        red_residual = pixels[i] + red_error * 7 / 16;
        pixels[i] = CLAMP(red_residual);
        green_residual = pixels[i + 1] + green_error * 7 / 16;
        pixels[i + 1] = CLAMP(green_residual);
        blue_residual = pixels[i + 2] + blue_error * 7 / 16;
        pixels[i + 2] = CLAMP(blue_residual);
      }

      // Propagate 3/16 of the residual error to (x - 1, y + 1).
      if (x > 0 && y < height - 1) {
        i = ((y + 1) * width + (x - 1)) * 3;
        red_residual = pixels[i] + red_error * 3 / 16;
        pixels[i] = CLAMP(red_residual);
        green_residual = pixels[i + 1] + green_error * 3 / 16;
        pixels[i + 1] = CLAMP(green_residual);
        blue_residual = pixels[i + 2] + blue_error * 3 / 16;
        pixels[i + 2] = CLAMP(blue_residual);
      }

      // Propagate 5/16 of the residual error to (x, y + 1).
      if (y < height - 1) {
        i = ((y + 1) * width + x) * 3;
        red_residual = pixels[i] + red_error * 5 / 16;
        pixels[i] = CLAMP(red_residual);
        green_residual = pixels[i + 1] + green_error * 5 / 16;
        pixels[i + 1] = CLAMP(green_residual);
        blue_residual = pixels[i + 2] + blue_error * 5 / 16;
        pixels[i + 2] = CLAMP(blue_residual);
      }

      // Propagate 1/16 of the residual error to (x + 1, y + 1).
      if (x < width - 1 && y < height - 1) {
        i = ((y + 1) * width + (x + 1)) * 3;
        red_residual = pixels[i] + red_error / 16;
        pixels[i] = CLAMP(red_residual);
        green_residual = pixels[i + 1] + green_error / 16;
        pixels[i + 1] = CLAMP(green_residual);
        blue_residual = pixels[i + 2] + blue_error / 16;
        pixels[i + 2] = CLAMP(blue_residual);
      }
    }
  }
}

static PyObject *dither(PyObject *self, PyObject *args) {
  // Parse the function arguments.
  PyArrayObject *pixels, *palette;
  if (!PyArg_ParseTuple(args, "O!O!", &PyArray_Type, &pixels, &PyArray_Type,
                        &palette)) {
    return NULL;
  }

  // Verify that the inputs are of the correct shape.
  if (PyArray_NDIM(pixels) != 3 || PyArray_DIM(pixels, 2) != 3) {
    PyErr_SetString(
        PyExc_ValueError,
        "Pixels should be a numpy array of shape (height, width, 3)");
    return NULL;
  }
  if (PyArray_NDIM(palette) != 2 || PyArray_DIM(palette, 1) != 3) {
    PyErr_SetString(PyExc_ValueError,
                    "Palette should be a numpy array of shape (num_colors, 3)");
    return NULL;
  }

  // Verify that the inputs are of the correct type.
  if (PyArray_TYPE(pixels) != NPY_UINT8 || PyArray_TYPE(palette) != NPY_UINT8) {
    PyErr_SetString(PyExc_ValueError,
                    "Pixels and palette should be of type uint8");
    return NULL;
  }

  // Get the dimensions from the numpy arrays.
  uint32_t height = PyArray_DIM(pixels, 0);
  uint32_t width = PyArray_DIM(pixels, 1);
  uint32_t num_colors = PyArray_DIM(palette, 0);

  // Run the Floyd-Steinberg algorithm.
  floyd_steinberg(PyArray_DATA(pixels), width, height, PyArray_DATA(palette),
                  num_colors);

  Py_RETURN_NONE;
}

static PyMethodDef package_methods[] = {
    {"dither", dither, METH_VARARGS,
     "Dithers the image in place using the Floyd-Steinberg algorithm."},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef package_definition = {
    PyModuleDef_HEAD_INIT, "dithering", NULL, -1, package_methods};

PyMODINIT_FUNC PyInit_dithering(void) {
  Py_Initialize();
  import_array();
  return PyModule_Create(&package_definition);
}

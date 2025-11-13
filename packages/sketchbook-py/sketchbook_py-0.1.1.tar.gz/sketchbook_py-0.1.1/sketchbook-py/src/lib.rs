use pyo3::prelude::*;

#[pymodule(name = "sketchbook")]
mod sketchbook {
    use std::path::Path;

    use pyo3::prelude::*;
    use pyo3::{exceptions::PyValueError, types::PyBytes};
    use sketchbook_core::{
        Align, DrawerRegion, ImageFitPaster, PasteStyle, SketchbookError, TextFitDrawer, TextStyle,
        VAlign,
    };

    fn to_pyerr(err: SketchbookError) -> PyErr {
        PyValueError::new_err(err.to_string())
    }

    #[pyclass(name = "Align")]
    #[derive(Clone)]
    enum PyAlign {
        Left,
        Center,
        Right,
    }

    impl From<PyAlign> for Align {
        fn from(align: PyAlign) -> Self {
            match align {
                PyAlign::Left => Align::Left,
                PyAlign::Center => Align::Center,
                PyAlign::Right => Align::Right,
            }
        }
    }

    #[pyclass(name = "VAlign")]
    #[derive(Clone)]
    enum PyVAlign {
        Top,
        Middle,
        Bottom,
    }

    impl From<PyVAlign> for VAlign {
        fn from(valign: PyVAlign) -> Self {
            match valign {
                PyVAlign::Top => VAlign::Top,
                PyVAlign::Middle => VAlign::Middle,
                PyVAlign::Bottom => VAlign::Bottom,
            }
        }
    }

    #[pyclass(name = "DrawerRegion")]
    #[derive(Clone)]
    struct PyDrawerRegion {
        #[pyo3(get, set)]
        top_left_x: u32,
        #[pyo3(get, set)]
        top_left_y: u32,
        #[pyo3(get, set)]
        bottom_right_x: u32,
        #[pyo3(get, set)]
        bottom_right_y: u32,
    }

    #[pymethods]
    impl PyDrawerRegion {
        #[new]
        fn new(top_left_x: u32, top_left_y: u32, bottom_right_x: u32, bottom_right_y: u32) -> Self {
            Self {
                top_left_x,
                top_left_y,
                bottom_right_x,
                bottom_right_y,
            }
        }
    }

    impl From<PyDrawerRegion> for DrawerRegion {
        fn from(region: PyDrawerRegion) -> Self {
            DrawerRegion {
                top_left_x: region.top_left_x,
                top_left_y: region.top_left_y,
                bottom_right_x: region.bottom_right_x,
                bottom_right_y: region.bottom_right_y,
            }
        }
    }

    #[pyclass(name = "TextStyle")]
    #[derive(Clone)]
    struct PyTextStyle {
        #[pyo3(get, set)]
        color: (u8, u8, u8, u8),
        #[pyo3(get, set)]
        bracket_color: (u8, u8, u8, u8),

        #[pyo3(get, set)]
        max_font_height: Option<u32>,
        #[pyo3(get, set)]
        line_spacing: f32,

        #[pyo3(get, set)]
        align: PyAlign,
        #[pyo3(get, set)]
        valign: PyVAlign,
    }

    #[pymethods]
    impl PyTextStyle {
        #[new]
        #[pyo3(signature = (color=(0, 0, 0, 255), bracket_color=(128, 0, 128, 255), max_font_height=None, line_spacing=0.15, align=PyAlign::Center, valign=PyVAlign::Middle))]
        fn new(
            color: (u8, u8, u8, u8),
            bracket_color: (u8, u8, u8, u8),
            max_font_height: Option<u32>,
            line_spacing: f32,
            align: PyAlign,
            valign: PyVAlign,
        ) -> Self {
            Self {
                color,
                bracket_color,
                max_font_height,
                line_spacing,
                align,
                valign,
            }
        }
    }

    #[pyclass(name = "PasteStyle")]
    #[derive(Clone)]
    struct PyPasteStyle {
        #[pyo3(get, set)]
        align: PyAlign,
        #[pyo3(get, set)]
        valign: PyVAlign,

        #[pyo3(get, set)]
        padding: u32,
        #[pyo3(get, set)]
        keep_alpha: bool,
        #[pyo3(get, set)]
        allow_upscale: bool,
    }

    #[pymethods]
    impl PyPasteStyle {
        #[new]
        #[pyo3(signature = (padding=0, keep_alpha=true, allow_upscale=false, align=PyAlign::Center, valign=PyVAlign::Middle))]
        fn new(
            padding: u32,
            keep_alpha: bool,
            allow_upscale: bool,
            align: PyAlign,
            valign: PyVAlign,
        ) -> Self {
            Self {
                padding,
                keep_alpha,
                allow_upscale,
                align,
                valign,
            }
        }
    }

    #[derive(FromPyObject)]
    enum PyImageSource {
        Path(String),
        Bytes(Vec<u8>),
    }

    impl PyImageSource {
        fn load_image(&self) -> PyResult<image::DynamicImage> {
            match self {
                PyImageSource::Path(path) => image::open(path).map_err(|e| {
                    PyValueError::new_err(format!(
                        "Failed to open image from path '{}': {}",
                        path, e
                    ))
                }),
                PyImageSource::Bytes(bytes) => image::load_from_memory(bytes).map_err(|e| {
                    PyValueError::new_err(format!("Failed to load image from bytes: {}", e))
                }),
            }
        }
    }

    #[pyclass(name = "TextFitDrawer")]
    struct PyTextFitDrawer {
        drawer: TextFitDrawer,
    }

    #[pymethods]
    impl PyTextFitDrawer {
        #[new]
        #[pyo3(signature = (base_image, font, overlay_image=None, region=None))]
        fn new(
            base_image: PyImageSource,
            font: &str,
            overlay_image: Option<PyImageSource>,
            region: Option<PyDrawerRegion>,
        ) -> PyResult<Self> {
            let base_image = base_image.load_image()?;

            let overlay_image = if let Some(source) = overlay_image {
                Some(source.load_image()?)
            } else {
                None
            };

            let rust_region = region.map(|r| r.into());
            let drawer =
                TextFitDrawer::new(base_image, overlay_image, Path::new(font), rust_region)
                    .map_err(to_pyerr)?;

            Ok(Self { drawer })
        }

        #[pyo3(signature = (text, style=None))]
        fn draw(
            &self,
            py: Python,
            text: &str,
            style: Option<PyTextStyle>,
        ) -> PyResult<Py<PyBytes>> {
            let rust_style = if let Some(s) = style {
                TextStyle {
                    color: image::Rgba([s.color.0, s.color.1, s.color.2, s.color.3]),
                    bracket_color: image::Rgba([
                        s.bracket_color.0,
                        s.bracket_color.1,
                        s.bracket_color.2,
                        s.bracket_color.3,
                    ]),
                    max_font_height: s.max_font_height,
                    line_spacing: s.line_spacing,

                    align: Align::Center,
                    valign: VAlign::Middle,
                }
            } else {
                TextStyle::default()
            };

            let result = self.drawer.draw(text, &rust_style).map_err(to_pyerr)?;

            let mut bytes: Vec<u8> = Vec::new();
            result
                .write_to(
                    &mut std::io::Cursor::new(&mut bytes),
                    image::ImageFormat::Png,
                )
                .map_err(|e| PyValueError::new_err(format!("Failed to encode image: {}", e)))?;
            Ok(PyBytes::new(py, &bytes).into())
        }
    }

    #[pyclass(name = "ImageFitPaster")]
    struct PyImageFitPaster {
        paster: ImageFitPaster,
    }

    #[pymethods]
    impl PyImageFitPaster {
        #[new]
        #[pyo3(signature = (base_image, overlay_image=None, region=None))]
        fn new(
            base_image: PyImageSource,
            overlay_image: Option<PyImageSource>,
            region: Option<PyDrawerRegion>,
        ) -> PyResult<Self> {
            let base_image = base_image.load_image()?;

            let overlay_image = if let Some(source) = overlay_image {
                Some(source.load_image()?)
            } else {
                None
            };

            let rust_region = region.map(|r| r.into());
            let paster =
                ImageFitPaster::new(base_image, overlay_image, rust_region).map_err(to_pyerr)?;

            Ok(Self { paster })
        }

        #[pyo3(signature = (image, style=None))]
        fn paste(
            &self,
            py: Python,
            image: PyImageSource,
            style: Option<PyPasteStyle>,
        ) -> PyResult<Py<PyBytes>> {
            let image = image.load_image()?;

            let rust_style = if let Some(s) = style {
                PasteStyle {
                    padding: s.padding,
                    align: Align::Center,
                    valign: VAlign::Middle,
                    keep_alpha: s.keep_alpha,
                    allow_upscale: s.allow_upscale,
                }
            } else {
                PasteStyle::default()
            };

            let result = self.paster.paste(&image, &rust_style).map_err(to_pyerr)?;

            let mut bytes: Vec<u8> = Vec::new();
            result
                .write_to(
                    &mut std::io::Cursor::new(&mut bytes),
                    image::ImageFormat::Png,
                )
                .map_err(|e| PyValueError::new_err(format!("Failed to encode image: {}", e)))?;
            Ok(PyBytes::new(py, &bytes).into())
        }
    }
}

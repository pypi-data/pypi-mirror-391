use thiserror::Error;

#[derive(Error, Debug)]
pub enum SketchbookError {
    #[error("Invalid region: {0}")]
    InvalidRegion(String),

    #[error("Invalid text style: {0}")]
    InvalidTextStyle(String),

    #[error("Invalid paste style: {0}")]
    InvalidPasteStyle(String),

    #[error("Invalid image: {0}")]
    InvalidImage(String),

    #[error("Invalid font: {0}")]
    InvalidFont(#[from] ab_glyph::InvalidFont),

    #[error("Font loading failed: {0}")]
    FontLoadError(String),

    #[error("Image processing failed: {0}")]
    ImageProcessError(String),

    #[error("Text rendering failed: {0}")]
    TextRenderError(String),

    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),

    #[error("Image error: {0}")]
    ImageError(#[from] image::ImageError),
}

pub(crate) type Result<T> = std::result::Result<T, SketchbookError>;

use crate::{Result, SketchbookError};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Align {
    Left,
    Center,
    Right,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum VAlign {
    Top,
    Middle,
    Bottom,
}

pub struct DrawerRegion {
    pub top_left_x: u32,
    pub top_left_y: u32,
    pub bottom_right_x: u32,
    pub bottom_right_y: u32,
}

impl DrawerRegion {
    pub fn new(top_left_x: u32, top_left_y: u32, bottom_right_x: u32, bottom_right_y: u32) -> Self {
        Self {
            top_left_x,
            top_left_y,
            bottom_right_x,
            bottom_right_y,
        }
    }
}

impl DrawerRegion {
    pub(crate) fn width(&self) -> u32 {
        self.bottom_right_x.saturating_sub(self.top_left_x)
    }

    pub(crate) fn height(&self) -> u32 {
        self.bottom_right_y.saturating_sub(self.top_left_y)
    }

    pub(crate) fn available_size(&self, padding: u32) -> (u32, u32) {
        let w = self.width().saturating_sub(2 * padding).max(1);
        let h = self.height().saturating_sub(2 * padding).max(1);
        (w, h)
    }

    pub(crate) fn validate(&self) -> Result<()> {
        if !(self.width() == 0 || self.height() == 0) {
            return Ok(());
        }

        Err(SketchbookError::InvalidRegion(format!(
            "({}, {}) -> ({}, {})",
            self.top_left_x, self.top_left_y, self.bottom_right_x, self.bottom_right_y
        )))
    }
}

#[derive(Debug, Clone)]
pub struct TextStyle {
    pub color: image::Rgba<u8>,
    pub bracket_color: image::Rgba<u8>,

    pub max_font_height: Option<u32>,
    pub line_spacing: f32,

    pub align: Align,
    pub valign: VAlign,
}

impl Default for TextStyle {
    fn default() -> Self {
        Self {
            color: image::Rgba([0, 0, 0, 255]),
            bracket_color: image::Rgba([128, 0, 128, 255]),

            max_font_height: None,
            line_spacing: 0.15,

            align: Align::Center,
            valign: VAlign::Middle,
        }
    }
}

impl TextStyle {
    pub(crate) fn validate(&self) -> Result<()> {
        if self.line_spacing < 0.0 {
            return Err(SketchbookError::InvalidTextStyle(format!(
                "行间距不能为负数: {}",
                self.line_spacing
            )));
        }

        if self.line_spacing > 2.0 {
            return Err(SketchbookError::InvalidTextStyle(format!(
                "行间距超出合理范围 [0, 2]: {}",
                self.line_spacing
            )));
        }

        Ok(())
    }
}

#[derive(Debug, Clone)]
pub struct PasteStyle {
    pub align: Align,
    pub valign: VAlign,
    pub padding: u32,
    pub allow_upscale: bool,
    pub keep_alpha: bool,
}

impl Default for PasteStyle {
    fn default() -> Self {
        Self {
            align: Align::Center,
            valign: VAlign::Middle,
            padding: 0,
            allow_upscale: false,
            keep_alpha: true,
        }
    }
}

impl PasteStyle {
    pub fn validate(&self) -> Result<()> {
        if self.padding < 10000 {
            return Ok(());
        }

        Err(SketchbookError::InvalidPasteStyle(format!(
            "内边距超出合理范围: {}",
            self.padding
        )))
    }
}

use std::{path::Path, vec};

use ab_glyph::{Font, FontArc, PxScale, ScaleFont};
use image::DynamicImage;
use imageproc::drawing::draw_text_mut;

use crate::{Align, DrawerRegion, Result, TextStyle, VAlign};

pub struct TextFitDrawer {
    pub base_image: DynamicImage,
    pub overlay_image: Option<DynamicImage>,
    pub font: FontArc,
    pub region: DrawerRegion,
}

pub(crate) struct TextMetrics {
    width: u32,
    height: u32,
    line_height: u32,
}

pub(crate) struct ColorSegment {
    text: String,
    color: image::Rgba<u8>,
}

impl TextFitDrawer {
    pub fn new(
        base_image: DynamicImage,
        overlay_image: Option<DynamicImage>,
        font_path: &Path,
        region: Option<DrawerRegion>,
    ) -> Result<Self> {
        let region = region.unwrap_or(DrawerRegion {
            top_left_x: 0,
            top_left_y: 0,
            bottom_right_x: base_image.width(),
            bottom_right_y: base_image.height(),
        });
        region.validate()?;

        let font = FontArc::try_from_vec(std::fs::read(font_path)?)?;
        Ok(Self {
            base_image,
            overlay_image,
            font,
            region,
        })
    }
}

impl TextFitDrawer {
    pub fn draw(&self, text: &str, style: &TextStyle) -> Result<DynamicImage> {
        style.validate()?;
        let mut image = self.base_image.to_rgba8();

        let (best_size, best_lines, line_height, block_height) =
            self.find_best_size(text, style)?;

        let scale = PxScale::from(best_size as f32);
        let y_start = self.calc_vertical_position(block_height, style.valign);

        self.draw_text_lines(&mut image, &best_lines, scale, y_start, line_height, style)?;

        if let Some(overlay) = &self.overlay_image {
            image::imageops::overlay(&mut image, &overlay.to_rgba8(), 0, 0);
        }

        Ok(image.into())
    }

    fn draw_text_lines(
        &self,
        image: &mut image::RgbaImage,
        lines: &[String],
        scale: PxScale,
        y_start: u32,
        line_height: u32,
        style: &TextStyle,
    ) -> Result<()> {
        let mut in_bracket = false;
        for (i, line) in lines.iter().enumerate() {
            let y = y_start + i as u32 * line_height;
            if y.saturating_sub(y_start) >= self.region.height() {
                break;
            }

            let x_start = self.calc_horizontal_position(line, scale, style.align);

            let (segments, new_in_bracket) = self.parse_color_segments(line, style, in_bracket);
            in_bracket = new_in_bracket;

            let mut x = x_start;
            for segment in segments {
                draw_text_mut(
                    image,
                    segment.color,
                    x as i32,
                    y as i32,
                    scale,
                    &self.font,
                    &segment.text,
                );
                let width = self.measure_text_width(&segment.text, scale) as u32;
                x += width;
            }
        }
        Ok(())
    }
}

impl TextFitDrawer {
    fn calc_vertical_position(&self, block_height: u32, valign: VAlign) -> u32 {
        match valign {
            VAlign::Top => self.region.top_left_y,
            VAlign::Middle => {
                self.region.top_left_y + (self.region.height().saturating_sub(block_height)) / 2
            }
            VAlign::Bottom => self.region.bottom_right_y.saturating_sub(block_height),
        }
    }

    fn calc_horizontal_position(&self, line: &str, scale: PxScale, align: Align) -> u32 {
        let line_width = self.measure_text_width(line, scale) as u32;
        match align {
            Align::Left => self.region.top_left_x,
            Align::Center => {
                self.region.top_left_x + (self.region.width().saturating_sub(line_width)) / 2
            }
            Align::Right => self.region.bottom_right_x.saturating_sub(line_width),
        }
    }
}

impl TextFitDrawer {
    fn find_best_size(
        &self,
        text: &str,
        style: &TextStyle,
    ) -> Result<(u32, Vec<String>, u32, u32)> {
        let mut upper_bound = style
            .max_font_height
            .map(|max| max.min(self.region.height()))
            .unwrap_or(self.region.height());

        let mut lower_bound = 1;
        let mut best_size = 1;
        let mut best_lines = Vec::new();
        let mut best_line_height = 0;
        let mut best_total_height = 0;

        while lower_bound <= upper_bound {
            let mid_size = (lower_bound + upper_bound) / 2;
            let scale = PxScale::from(mid_size as f32);

            let lines = self.wrap_lines(text, scale);
            let metrics = self.measure_text_block(&lines, scale, style.line_spacing);

            if metrics.width <= self.region.width() && metrics.height <= self.region.height() {
                best_size = mid_size;
                best_lines = lines;
                best_line_height = metrics.line_height;
                best_total_height = metrics.height;
                lower_bound = mid_size + 1;
            } else {
                upper_bound = mid_size - 1;
            }
        }

        if best_size == 0 {
            best_size = 1;
            let scale = PxScale::from(1.0);
            best_lines = self.wrap_lines(text, scale);
            let metrics = self.measure_text_block(&best_lines, scale, style.line_spacing);
            best_line_height = metrics.line_height;
            best_total_height = metrics.height;
        }

        Ok((best_size, best_lines, best_line_height, best_total_height))
    }
}

impl TextFitDrawer {
    fn wrap_lines(&self, text: &str, scale: PxScale) -> Vec<String> {
        let lines: Vec<String> = text
            .lines()
            .flat_map(|paragraph| {
                if paragraph.is_empty() {
                    itertools::Either::Left(std::iter::once(String::new()))
                } else {
                    itertools::Either::Right(self.wrap_paragraph(paragraph, scale).into_iter())
                }
            })
            .collect();

        if lines.is_empty() {
            vec![String::new()]
        } else {
            lines
        }
    }

    fn wrap_paragraph(&self, paragraph: &str, scale: PxScale) -> Vec<String> {
        let has_space = paragraph.contains(' ');

        if has_space {
            self.wrap_by_words(paragraph, scale)
        } else {
            self.wrap_by_chars(paragraph, scale)
        }
    }

    fn wrap_by_chars(&self, paragraph: &str, scale: PxScale) -> Vec<String> {
        let chars: Vec<char> = paragraph.chars().collect();
        let mut lines = Vec::new();
        let mut current_line = String::new();

        for ch in chars {
            let test_line = format!("{}{}", current_line, ch);
            let width = self.measure_text_width(&test_line, scale);

            if width <= self.region.width() as f32 {
                current_line = test_line;
            } else {
                if !current_line.is_empty() {
                    lines.push(current_line);
                }
                current_line = ch.to_string();
            }
        }

        if !current_line.is_empty() {
            lines.push(current_line);
        }

        lines
    }

    fn wrap_by_words(&self, paragraph: &str, scale: PxScale) -> Vec<String> {
        let words: Vec<&str> = paragraph.split_whitespace().collect();
        let mut lines = Vec::new();
        let mut current_line = String::new();

        for word in words {
            let test_line = if current_line.is_empty() {
                word.to_string()
            } else {
                format!("{} {}", current_line, word)
            };

            let width = self.measure_text_width(&test_line, scale);

            if width <= self.region.width() as f32 {
                current_line = test_line;
            } else {
                if !current_line.is_empty() {
                    lines.push(current_line);
                }
                if self.measure_text_width(word, scale) > self.region.width() as f32 {
                    current_line = self.wrap_long_word(word, scale, &mut lines);
                } else {
                    current_line = word.to_string();
                }
            }
        }

        if !current_line.is_empty() {
            lines.push(current_line);
        }

        lines
    }

    fn wrap_long_word(&self, word: &str, scale: PxScale, lines: &mut Vec<String>) -> String {
        let mut current_line = String::new();

        for c in word.chars() {
            let test_line = format!("{}{}", current_line, c);
            let width = self.measure_text_width(&test_line, scale);

            if width <= self.region.width() as f32 {
                current_line = test_line;
            } else {
                if !current_line.is_empty() {
                    lines.push(current_line);
                }
                current_line = c.to_string();
            }
        }

        current_line
    }
}

impl TextFitDrawer {
    fn measure_text_block(
        &self,
        lines: &[String],
        scale: PxScale,
        line_spacing: f32,
    ) -> TextMetrics {
        let scaled_font = self.font.as_scaled(scale);

        let v_metrics = scaled_font.height();
        let line_height = (v_metrics * (1.0 + line_spacing)) as u32;

        let max_width = lines
            .iter()
            .map(|line| self.measure_text_width(line, scale) as u32)
            .max()
            .unwrap_or(0);

        let total_height = line_height * lines.len().max(1) as u32;

        TextMetrics {
            width: max_width,
            height: total_height,
            line_height,
        }
    }

    fn measure_text_width(&self, line: &str, scale: PxScale) -> f32 {
        let scaled_font = self.font.as_scaled(scale);
        line.chars()
            .filter_map(|c| {
                let glyph = scaled_font.scaled_glyph(c);
                Some(scaled_font.h_advance(glyph.id))
            })
            .sum()
    }
}

impl TextFitDrawer {
    fn parse_color_segments(
        &self,
        text: &str,
        style: &TextStyle,
        in_bracket: bool,
    ) -> (Vec<ColorSegment>, bool) {
        let mut segments = Vec::new();
        let mut buffer = String::new();
        let mut current_in_bracket = in_bracket;

        for ch in text.chars() {
            match ch {
                '[' | '【' => {
                    if !buffer.is_empty() {
                        segments.push(ColorSegment {
                            text: buffer.clone(),
                            color: if current_in_bracket {
                                style.bracket_color
                            } else {
                                style.color
                            },
                        });
                        buffer.clear();
                    }
                    segments.push(ColorSegment {
                        text: ch.to_string(),
                        color: style.bracket_color,
                    });
                    current_in_bracket = true;
                }
                ']' | '】' => {
                    if !buffer.is_empty() {
                        segments.push(ColorSegment {
                            text: buffer.clone(),
                            color: style.bracket_color,
                        });
                        buffer.clear();
                    }
                    segments.push(ColorSegment {
                        text: ch.to_string(),
                        color: style.bracket_color,
                    });
                    current_in_bracket = false;
                }
                _ => {
                    buffer.push(ch);
                }
            }
        }

        if !buffer.is_empty() {
            segments.push(ColorSegment {
                text: buffer,
                color: if current_in_bracket {
                    style.bracket_color
                } else {
                    style.color
                },
            });
        }

        (segments, current_in_bracket)
    }
}

#[cfg(test)]
mod tests {
    use std::time::Instant;

    use super::*;

    #[test]
    fn test_text_fit_drawer() {
        let base_image = image::open("../img/base.png").unwrap();
        let overlay_image = image::open("../img/base_overlay.png").unwrap();

        let region = DrawerRegion {
            top_left_x: 119,
            top_left_y: 450,
            bottom_right_x: 398,
            bottom_right_y: 625,
        };

        let drawer = TextFitDrawer::new(
            base_image,
            Some(overlay_image),
            Path::new("../font/font.ttf"),
            Some(region),
        )
        .unwrap();

        let start_time = Instant::now();
        let a = drawer.draw("这就是 Pyo3", &TextStyle::default()).unwrap();
        println!("Text 处理时间: {:?}", start_time.elapsed());
        a.save("../text_output.png").unwrap();
    }
}

use image::{DynamicImage, GenericImageView, Rgba};

use crate::{DrawerRegion, PasteStyle, Result, SketchbookError};

pub struct ImageFitPaster {
    pub base_image: DynamicImage,
    pub overlay_image: Option<DynamicImage>,
    pub region: DrawerRegion,
}

impl ImageFitPaster {
    pub fn new(
        base_image: DynamicImage,
        overlay_image: Option<DynamicImage>,
        region: Option<DrawerRegion>,
    ) -> Result<Self> {
        let region = region.unwrap_or(DrawerRegion {
            top_left_x: 0,
            top_left_y: 0,
            bottom_right_x: base_image.width(),
            bottom_right_y: base_image.height(),
        });

        region.validate()?;

        Ok(Self {
            base_image,
            region,
            overlay_image,
        })
    }
}

impl ImageFitPaster {
    pub fn paste(&self, image: &DynamicImage, style: &PasteStyle) -> Result<DynamicImage> {
        style.validate()?;

        let (image_w, image_h) = image.dimensions();
        if image_w == 0 || image_h == 0 {
            return Err(SketchbookError::InvalidImage("输入图片尺寸无效".into()));
        }

        let (region_w, region_h) = self.region.available_size(style.padding);
        let scale = self.calculate_scale(image_w, image_h, region_w, region_h, style.allow_upscale);

        let new_w = ((image_w as f32 * scale).round() as u32).max(1);
        let new_h = ((image_h as f32 * scale).round() as u32).max(1);

        let resized_image = image
            .resize_exact(new_w, new_h, image::imageops::FilterType::Lanczos3)
            .to_rgba8();
        let paste_x = self.calc_horizontal_position(region_w, new_w, style.padding, style.align);
        let paste_y = self.calc_vertical_position(region_h, new_h, style.padding, style.valign);

        let mut base_image = self.base_image.to_rgba8();
        if style.keep_alpha {
            self.paste_with_alpha(&mut base_image, &resized_image, paste_x, paste_y);
        } else {
            image::imageops::overlay(
                &mut base_image,
                &resized_image,
                paste_x as i64,
                paste_y as i64,
            );
        }

        if let Some(overlay) = &self.overlay_image {
            image::imageops::overlay(&mut base_image, &overlay.to_rgba8(), 0, 0);
        }

        Ok(base_image.into())
    }
}

impl ImageFitPaster {
    fn calculate_scale(
        &self,
        image_w: u32,
        image_h: u32,
        region_w: u32,
        region_h: u32,
        allow_upscale: bool,
    ) -> f32 {
        let scale_w = region_w as f32 / image_w as f32;
        let scale_h = region_h as f32 / image_h as f32;
        let scale = scale_w.min(scale_h);

        if !allow_upscale && scale > 1.0 {
            1.0
        } else {
            scale
        }
    }

    fn calc_horizontal_position(
        &self,
        region_w: u32,
        new_w: u32,
        padding: u32,
        align: crate::Align,
    ) -> u32 {
        match align {
            crate::Align::Left => self.region.top_left_x + padding,
            crate::Align::Center => {
                self.region.top_left_x
                    + padding
                    + (region_w.saturating_sub(new_w + 2 * padding)) / 2
            }
            crate::Align::Right => self
                .region
                .bottom_right_x
                .saturating_sub(padding)
                .saturating_sub(new_w),
        }
    }

    fn calc_vertical_position(
        &self,
        region_h: u32,
        new_h: u32,
        padding: u32,
        valign: crate::VAlign,
    ) -> u32 {
        match valign {
            crate::VAlign::Top => self.region.top_left_y + padding,
            crate::VAlign::Middle => {
                self.region.top_left_y
                    + padding
                    + (region_h.saturating_sub(new_h + 2 * padding)) / 2
            }
            crate::VAlign::Bottom => self
                .region
                .bottom_right_y
                .saturating_sub(padding)
                .saturating_sub(new_h),
        }
    }

    fn paste_with_alpha(
        &self,
        base_image: &mut image::ImageBuffer<Rgba<u8>, Vec<u8>>,
        overlay_image: &image::ImageBuffer<Rgba<u8>, Vec<u8>>,
        paste_x: u32,
        paste_y: u32,
    ) {
        for (overlay_image_x, overlay_image_y, pixel) in overlay_image.enumerate_pixels() {
            let base_image_x = paste_x + overlay_image_x;
            let base_image_y = paste_y + overlay_image_y;

            if base_image_x < base_image.width() && base_image_y < base_image.height() {
                let base_pixel = base_image.get_pixel(base_image_x, base_image_y);
                let blended_pixel = self.blend_pixels(*base_pixel, *pixel);
                base_image.put_pixel(base_image_x, base_image_y, blended_pixel);
            }
        }
    }

    fn blend_pixels(&self, base: Rgba<u8>, overlay: Rgba<u8>) -> Rgba<u8> {
        let alpha = overlay[3] as f32 / 255.0;
        let inv_alpha = 1.0 - alpha;

        Rgba([
            ((overlay[0] as f32 * alpha) + (base[0] as f32 * inv_alpha)) as u8,
            ((overlay[1] as f32 * alpha) + (base[1] as f32 * inv_alpha)) as u8,
            ((overlay[2] as f32 * alpha) + (base[2] as f32 * inv_alpha)) as u8,
            ((overlay[3] as f32 * alpha) + (base[3] as f32 * inv_alpha)) as u8,
        ])
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::Instant;

    #[test]
    fn test_image_fit_paster() {
        let base_image = image::open("../img/base.png").unwrap();
        let overlay_image = image::open("../img/base_overlay.png").unwrap();
        let region = DrawerRegion {
            top_left_x: 119,
            top_left_y: 450,
            bottom_right_x: 398,
            bottom_right_y: 625,
        };

        let paster = ImageFitPaster::new(base_image, Some(overlay_image), Some(region)).unwrap();
        let start_time = Instant::now();
        let result = paster
            .paste(
                &image::open("../output.png").unwrap(),
                &PasteStyle::default(),
            )
            .unwrap();
        let duration = start_time.elapsed();
        println!("处理时间: {:?}", duration);

        result.save("../result.png").unwrap();
    }
}

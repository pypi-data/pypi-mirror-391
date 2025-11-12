use image::{DynamicImage, GenericImageView};
//use pyo3::exceptions::PyIOError;
use numpy::ndarray::{Array1, Array4};
use numpy::IntoPyArray;
use pyo3::exceptions::PyIOError;
use pyo3::{prelude::*, IntoPyObjectExt};
use rand::seq::SliceRandom;
use rand::thread_rng;
use rayon::prelude::*;
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use walkdir::WalkDir; //for recursively finding image files

// CIFAR10: MEAN AND STDEV FOR NORMALIZATION:
const CIFAR10_CHANNEL_MEAN_R: f32 = 0.4914;
const CIFAR10_CHANNEL_MEAN_G: f32 = 0.4822;
const CIFAR10_CHANNEL_MEAN_B: f32 = 0.4465;
const CIFAR10_CHANNEL_SDEV_R: f32 = 0.2023;
const CIFAR10_CHANNEL_SDEV_G: f32 = 0.1994;
const CIFAR10_CHANNEL_SDEV_B: f32 = 0.2010;
//these const calculations removed division from the hotpath and shaved 20% off eager load time
const NORM_SCALE_R: f32 = 1.0 / (255.0 * CIFAR10_CHANNEL_SDEV_R);
const NORM_OFFSET_R: f32 = CIFAR10_CHANNEL_MEAN_R / CIFAR10_CHANNEL_SDEV_R;
const NORM_SCALE_G: f32 = 1.0 / (255.0 * CIFAR10_CHANNEL_SDEV_G);
const NORM_OFFSET_G: f32 = CIFAR10_CHANNEL_MEAN_G / CIFAR10_CHANNEL_SDEV_G;
const NORM_SCALE_B: f32 = 1.0 / (255.0 * CIFAR10_CHANNEL_SDEV_B);
const NORM_OFFSET_B: f32 = CIFAR10_CHANNEL_MEAN_B / CIFAR10_CHANNEL_SDEV_B;

//////////////////// FOR PYTHON ////////////////////
/// IMPORTANT - this assumes atm that all images have the same dimensions (ok for CIFAR-10)
fn _convert_images_to_buffer(
    images_with_labels: Vec<(DynamicImage, u32)>,
) -> (Vec<f32>, (usize, usize, usize, usize), Vec<u32>) {
    if images_with_labels.is_empty() {
        return (Vec::new(), (0, 0, 0, 0), Vec::new());
    }

    // Shape from first image
    let (width, height) = images_with_labels[0].0.dimensions();
    let (w, h, c) = (width as usize, height as usize, 3usize);
    let per_image = c * h * w;
    let n = images_with_labels.len();

    // Each worker builds one image chunk in NCHW layout: [RR..][GG..][BB..]
    let (chunks, labels): (Vec<Vec<f32>>, Vec<u32>) = images_with_labels
        .into_par_iter()
        .map(|(img, label)| {
            let mut chunk = vec![0f32; per_image];
            let (r_off, g_off, b_off) = (0, h * w, 2 * h * w);

            let mut write_rgb = |x: u32, y: u32, r: u8, g: u8, b: u8| {
                let idx = (y as usize) * w + (x as usize);
                chunk[r_off + idx] = (r as f32) * NORM_SCALE_R - NORM_OFFSET_R;
                chunk[g_off + idx] = (g as f32) * NORM_SCALE_G - NORM_OFFSET_G;
                chunk[b_off + idx] = (b as f32) * NORM_SCALE_B - NORM_OFFSET_B;
            };

            match img {
                DynamicImage::ImageRgb8(rgb) => {
                    for y in 0..height {
                        for x in 0..width {
                            let [r, g, b] = rgb.get_pixel(x, y).0;
                            write_rgb(x, y, r, g, b);
                        }
                    }
                }
                DynamicImage::ImageRgba8(rgba) => {
                    for y in 0..height {
                        for x in 0..width {
                            let p = rgba.get_pixel(x, y).0;
                            write_rgb(x, y, p[0], p[1], p[2]);
                        }
                    }
                }
                DynamicImage::ImageLuma8(luma) => {
                    for y in 0..height {
                        for x in 0..width {
                            let v = luma.get_pixel(x, y).0[0];
                            write_rgb(x, y, v, v, v);
                        }
                    }
                }
                other => {
                    let rgb = other.to_rgb8(); // fallback conversion
                    for y in 0..height {
                        for x in 0..width {
                            let [r, g, b] = rgb.get_pixel(x, y).0;
                            write_rgb(x, y, r, g, b);
                        }
                    }
                }
            }

            (chunk, label)
        })
        .unzip();

    // Concatenate per-image chunks into (N*C*H*W)
    let mut buffer = Vec::with_capacity(n * per_image);
    for ch in chunks {
        buffer.extend(ch);
    }

    let shape = (n, c, h, w); // NCHW
    (buffer, shape, labels)
}
// fn _convert_images_to_buffer(
//     images_with_labels: Vec<(DynamicImage, u32)>,
// ) -> (Vec<f32>, (usize, usize, usize, usize), Vec<u32>) {
//     if images_with_labels.is_empty() {
//         return (Vec::new(), (0, 0, 0, 0), Vec::new());
//     }
//     // get shape from the first image
//     let (width, height) = images_with_labels[0].0.dimensions();
//     let n_channels = 3; // RGB8
//     let num_images = images_with_labels.len();
//     let chunk_size = (width as usize) * (height as usize) * n_channels;
//     //let mut buffer: Vec<f32> =
//     //Vec::with_capacity(num_images * (width as usize) * (height as usize) * n_channels);
//     //let mut labels: Vec<u32> = Vec::with_capacity(num_images); //these two removed, par_iter will take care of them

//     // multithreaded NCHW packing of buffer chunks, collected by .into_par_iter().map().unzip()
//     let (buffer_chunks, labels): (Vec<Vec<f32>>, Vec<u32>) = images_with_labels
//         .into_par_iter()
//         .map(|(img, label)| {
//             let mut buffer_chunk: Vec<f32> = Vec::with_capacity(chunk_size);
//             match img {
//                 image::DynamicImage::ImageRgb8(rgb_img) => {
//                     for pixel in rgb_img.pixels() {
//                         //refactor loop - here and in other formats
//                         buffer_chunk.push((pixel.0[0] as f32) * NORM_SCALE_R - NORM_OFFSET_R);
//                         buffer_chunk.push((pixel.0[1] as f32) * NORM_SCALE_G - NORM_OFFSET_G);
//                         buffer_chunk.push((pixel.0[2] as f32) * NORM_SCALE_B - NORM_OFFSET_B);
//                     }
//                 }
//                 image::DynamicImage::ImageRgba8(rgba_img) => {
//                     for pixel in rgba_img.pixels() {
//                         buffer_chunk.push((pixel.0[0] as f32) * NORM_SCALE_R - NORM_OFFSET_R);
//                         buffer_chunk.push((pixel.0[1] as f32) * NORM_SCALE_G - NORM_OFFSET_G);
//                         buffer_chunk.push((pixel.0[2] as f32) * NORM_SCALE_B - NORM_OFFSET_B);
//                     }
//                 }
//                 image::DynamicImage::ImageLuma8(luma_img) => {
//                     for pixel in luma_img.pixels() {
//                         let singval = pixel.0[0] as f32;
//                         buffer_chunk.push(singval * NORM_SCALE_R - NORM_OFFSET_R);
//                         buffer_chunk.push(singval * NORM_SCALE_G - NORM_OFFSET_G);
//                         buffer_chunk.push(singval * NORM_SCALE_B - NORM_OFFSET_B);
//                     }
//                 }
//                 _ => {
//                     let rgb_img = img.to_rgb8(); //REMEMBER: allocates and copies
//                     for pixel in rgb_img.pixels() {
//                         buffer_chunk.push((pixel.0[0] as f32) * NORM_SCALE_R - NORM_OFFSET_R);
//                         buffer_chunk.push((pixel.0[1] as f32) * NORM_SCALE_G - NORM_OFFSET_G);
//                         buffer_chunk.push((pixel.0[2] as f32) * NORM_SCALE_B - NORM_OFFSET_B);
//                     }
//                 }
//             }
//             (buffer_chunk, label)
//         })
//         .unzip();

//     // assembling the buffer from buffer chunks
//     let mut buffer: Vec<f32> = Vec::with_capacity(num_images * chunk_size);
//     for chunk in buffer_chunks {
//         buffer.extend(chunk);
//     }

//     let shape = (num_images, height as usize, width as usize, n_channels); //shape tuple -
//     (buffer, shape, labels)
// }

#[pyclass]
struct BimbLoader {
    paths_with_labels: Vec<(PathBuf, u32)>,
    class_map: HashMap<String, u32>,
    index: usize,
}
#[pymethods]
impl BimbLoader {
    #[new]
    fn new(path: String) -> PyResult<Self> {
        let dir = PathBuf::from(path);
        let (paths, map) = _gather_image_paths_and_labels(&dir);
        Ok(BimbLoader {
            paths_with_labels: paths,
            class_map: map,
            index: 0,
        })
    }
    fn get_next_batch(
        &mut self,
        py: Python,
        batch_size: usize,
    ) -> PyResult<Option<(Py<PyAny>, Vec<u32>)>> {
        // check whether terminal condition reached
        if self.index >= self.paths_with_labels.len() {
            return Ok(None);
        }
        let end_index = (self.index + batch_size).min(self.paths_with_labels.len());
        let batch_slice = &self.paths_with_labels[self.index..end_index];
        let images_with_labels = _load_images_and_labels(batch_slice);
        let (buffer_f32, shape_tuple, labels) = _convert_images_to_buffer(images_with_labels);
        let buffer_array_1d: Array1<f32> = Array1::from_vec(buffer_f32);
        let buffer_array_4d: Array4<f32> = buffer_array_1d
            .into_shape_with_order(shape_tuple)
            .map_err(|e| PyIOError::new_err(e.to_string()))?;
        self.index = end_index;
        let py_obj = buffer_array_4d
            .into_pyarray(py)
            .into_py_any(py)
            .map_err(|e| PyIOError::new_err(e.to_string()))?;
        Ok(Some((py_obj, labels)))
    }

    //shuffles dataset for new epoch, resets index
    fn shuffle(&mut self) {
        let mut rng = thread_rng();
        self.paths_with_labels.shuffle(&mut rng);
        self.index = 0;
    }

    fn reset(&mut self) {
        self.index = 0;
    }

    // returns n(samples) in dataset
    fn __len__(&self) -> usize {
        self.paths_with_labels.len()
    }

    // access class map
    #[getter]
    fn class_map(&self) -> HashMap<String, u32> {
        self.class_map.clone()
    }
}
#[pymodule]
fn bimb(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<BimbLoader>()?;
    Ok(())
}

// /// Load a whole folder of images → **NCHW** NumPy array (zero copy after the Vec)
// #[pyfunction]
// fn load_images(
//     py: Python,
//     path: String,
// ) -> PyResult<(Py<PyAny>, Vec<usize>, Vec<u32>, HashMap<String, u32>)> {
//     let dir = PathBuf::from(path);
//     let (paths_with_labels, class_map) = _gather_image_paths_and_labels(&dir);
//     let images_with_labels = _load_images_and_labels(&paths_with_labels);
//     let (buffer_f32, shape, labels) = _convert_images_to_buffer(images_with_labels);
//     let py_obj = buffer_f32.into_pyarray(py).into_py_any(py).unwrap();
//     Ok((py_obj, shape, labels, class_map))
// }

// PREP - NORMALIZATION //

//TODO fn normalize_cifar10_image(img: DynamicImage) -> &[f32] {}

//////////////////// PATHFINDING ////////////////////

/// Finds all image files recursively in a directory.
fn _gather_image_paths_and_labels(dir: &Path) -> (Vec<(PathBuf, u32)>, HashMap<String, u32>) {
    let supported_extensions = ["jpg", "jpeg", "png", "gif", "bmp"];
    let mut class_map = HashMap::new();
    let mut curr_class_id = 0u32;

    let paths_and_labels: Vec<(PathBuf, u32)> = WalkDir::new(dir)
        .into_iter()
        .filter_map(|entry_result| entry_result.ok()) // Ignore read errors
        .filter_map(|entry| {
            let path = entry.path();
            // Filter out non-files
            if !entry.file_type().is_file() {
                return None;
            }
            // Check the extension
            let extension_valid = path
                .extension()
                .and_then(|ext| ext.to_str())
                .map_or(false, |ext_str| {
                    supported_extensions.contains(&ext_str.to_lowercase().as_str())
                });
            if !extension_valid {
                return None;
            }

            let label_str = path
                .parent()? // -> Option<&Path>
                .file_name()? // -> Option<&OsStr>
                .to_str()?; // -> Option<&str>
                            // TODO improve error handling probably
            let class_id = *class_map.entry(label_str.to_string()).or_insert_with(|| {
                let id = curr_class_id;
                curr_class_id += 1;
                id
            });

            Some((path.to_path_buf(), class_id))
        })
        .collect();

    (paths_and_labels, class_map)
}

//////////////////// IMAGELOADING FROM (PATH, LABEL) ////////////////////

fn _load_images_and_labels(paths_with_labels: &[(PathBuf, u32)]) -> Vec<(DynamicImage, u32)> {
    paths_with_labels
        .par_iter()
        .filter_map(|(path, label)| image::open(path).ok().map(|img| (img, *label)))
        .collect()
}

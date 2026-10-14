# Image Classifier RFHOG Docs

A small local Home Assistant App that compares a current image with a stored reference image.

## First start
The default configuration uses the complete image, so no ROI setup is required.

Default options:

```yaml
current_image: /media/current_mailbox.jpg
reference_image: /data/reference.jpg
roi_x: 0
roi_y: 0
roi_width: 0
roi_height: 0
pixel_noise_threshold: 15
changed_pixel_threshold_percent: 8.0
```

When `roi_width` or `roi_height` is `0`, Image Compare processes the entire image.
To crop later, enter pixel coordinates and non-zero width/height.

## Basic test
1. Ensure `/media/current_mailbox.jpg` exists.
2. Open the App Web UI.
3. With the mailbox empty, click **Set current as reference**.
4. Take another snapshot to the same current-image path.
5. Click **Compare now**.

The App reports mean image difference, changed-pixel percentage, SSIM-style similarity, and a `CHANGED` / `UNCHANGED` result.

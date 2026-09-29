# Mailbox Classifier HOG

A lightweight, fully local image-classification project for detecting whether a smart mailbox is **empty** or **occupied**.

The classifier combines **Histogram of Oriented Gradients (HOG)** with color and image-statistics features and a **Random Forest classifier**. Training and evaluation are done in a Jupyter notebook, and the trained model can be deployed as a local **Home Assistant App** and called directly from Home Assistant automations.

The project was built as part of a larger Smart Mailbox system using an ESP32-CAM, Home Assistant, Frigate, a Synology NAS, and Apple HomeKit. Those components are optional: the classifier itself only needs images, a trained model, and a Python runtime.

---

## What it does

A camera mounted inside the mailbox captures an image whenever mail may have been delivered. The classifier predicts one of two classes:

- `empty`
- `occupied`

When deployed in Home Assistant, the result can be used to:

- send a photo notification
- switch on a mailbox status LED
- update a dashboard
- trigger another automation
- archive images for future retraining

Typical flow:

```text
Mailbox door / mail slot closes
              │
              ▼
     Home Assistant snapshot
              │
              ▼
      Mailbox Classifier App
              │
              ▼
       HOG + color features
              │
              ▼
         Random Forest
              │
              ▼
      empty / occupied
              │
       ┌──────┴──────┐
       ▼             ▼
 Notification     Status LED
```

---

## Why HOG + Random Forest?

The mailbox is a relatively controlled environment:

- the camera position is fixed
- the viewing angle is fixed
- the background changes relatively little
- the classification task is binary

This makes traditional computer-vision features a good fit.

**HOG** captures local edges and shape changes. Color histograms and global image statistics add information about brightness and color distribution.

The **Random Forest** combines those features to distinguish an empty mailbox from letters, newspapers, parcels, and other objects.

This approach is lightweight, fast, fully local, and does not require cloud inference or a GPU.

---

# Repository structure

```text
mailbox-classifier-hog/
│
├── training/
│   └── mailbox_random_forest_training.ipynb
│
├── data/
│   ├── empty/
│   └── occupied/
│
├── models/
│   └── mailbox_rf.joblib        # created after training; usually not committed
│
├── home-assistant-app/
│   └── mailbox-classifier/
│       ├── config.yaml
│       ├── Dockerfile
│       ├── app.py
│       ├── run.sh
│       └── requirements.txt
│
├── requirements.txt
├── .gitignore
└── README.md
```

The important separation is:

- `training/` contains the training pipeline
- `data/` contains labeled training images
- `models/` contains trained model artifacts
- `home-assistant-app/` contains the runtime service used inside Home Assistant

---

# 1. Development setup

## Requirements

For training:

- Python 3
- Jupyter Notebook or JupyterLab
- NumPy
- Pillow
- scikit-image
- scikit-learn
- joblib
- pandas
- matplotlib

For Home Assistant deployment:

- Home Assistant OS or another installation that supports local Apps/add-ons
- the App files from `home-assistant-app/mailbox-classifier/`

Optional:

- Home Assistant Samba Share for convenient file access
- NAS/network storage
- Frigate
- ESP32-CAM or another camera source

---

## Create a virtual environment

Clone the repository:

```bash
git clone <YOUR-REPOSITORY-URL>
cd mailbox-classifier-hog
```

Create and activate a virtual environment:

```bash
python3 -m venv mailbox_classifier_venv
source mailbox_classifier_venv/bin/activate
```

On Windows:

```powershell
mailbox_classifier_venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

The virtual environment itself should not be committed to Git.

---

# 2. Prepare the dataset

Place training images into two class folders:

```text
data/
├── empty/
│   ├── empty_001.jpg
│   ├── empty_002.jpg
│   └── ...
│
└── occupied/
    ├── letter_001.jpg
    ├── parcel_001.jpg
    ├── newspaper_001.jpg
    └── ...
```

`empty/` contains images where nothing is inside the mailbox.

`occupied/` contains images with letters, newspapers, parcels, or other delivered objects.

For a useful real-world model, collect varied examples:

- large and small parcels
- white and colored envelopes
- newspapers
- objects in different positions
- different daylight conditions
- LED illumination
- shadows and reflections

Difficult examples are especially valuable. For example, a white envelope on a bright mailbox floor may be much harder to detect than a large brown parcel.

Try to keep both classes reasonably balanced.

---

# 3. Train the classifier

Training is performed in:

```text
train/mailbox_random_forest_training.ipynb
```

Start Jupyter from the repository root:

```bash
jupyter notebook
```

Open:

```text
train/mailbox_random_forest_training.ipynb
```

and run the cells in sequence.

The notebook performs the complete training pipeline:

1. load labeled mailbox images
2. preprocess the images
3. extract HOG features
4. extract color and image-statistics features
5. train a Random Forest classifier
6. evaluate the classifier
7. inspect classification errors
8. save the trained model

For this use case, the most important error is a **false empty**:

> The mailbox contains something, but the classifier predicts `empty`.

For that reason, do not rely on training accuracy alone. Cross-validation, the confusion matrix, occupied-class recall, and the false-empty count are more useful.

---

# 4. Feature pipeline

The training notebook and deployed classifier must use **exactly the same feature extraction pipeline**.

The current pipeline includes:

## Color and image statistics

- RGB histograms
- HSV histograms
- grayscale histogram
- RGB mean and standard deviation
- grayscale mean and standard deviation
- simple edge-density measurement

## HOG

Typical parameters:

```text
HOG image:        160 × 120
Orientations:     9
Pixels per cell:  8 × 8
Cells per block:  2 × 2
Normalization:    L2-Hys
```

If you change feature extraction during training, make the same change in the Home Assistant App before deploying the newly trained model.

---

# 5. Save the trained model

After training, the notebook creates:

```text
mailbox_rf.joblib
```

For local development, place it in:

```text
models/mailbox_rf.joblib
```

The `.joblib` file contains the trained Random Forest model used for inference.

Model training and App deployment are intentionally separated. You can retrain and replace the model without rebuilding the App, as long as the feature pipeline remains compatible.

---

# 6. Home Assistant deployment

The classifier can run as a local Home Assistant App.

There are two useful deployment options.

## Option A — Simple setup

Store the model in the App's persistent `/data` directory:

```text
Home Assistant
│
├── Mailbox Classifier App
└── /data/mailbox_rf.joblib
```

Use:

```yaml
options:
  model_path: "/data/mailbox_rf.joblib"
```

This is the simplest setup and does not require a NAS.

---

## Option B — NAS / network storage

In the Smart Mailbox installation that inspired this project, the App runs in Home Assistant while the trained model lives on a Synology NAS:

```text
Home Assistant
/addons/mailbox-classifier/
        │
        │ loads model
        ▼
/media/frigate/mailbox_rf.joblib
        │
        │ network storage
        ▼
Synology NAS
```

This architecture keeps two concerns separate:

### Application code

The Home Assistant App:

- exposes the `/classify` endpoint
- reads the requested image
- extracts HOG/color features
- loads the Random Forest model
- returns a prediction and probability

### Trained model

The `.joblib` model can live on external storage and be replaced after retraining.

That means retraining does **not** require rebuilding the Home Assistant App.

---

# 7. Mount NAS storage in Home Assistant

This section is only required for Option B.

Mount the NAS share as Home Assistant network storage so that it appears under `/media`.

Example:

```text
Synology NAS share
        │
        ▼
Home Assistant network storage
        │
        ▼
/media/frigate
```

The trained model is then available to the App as:

```text
/media/frigate/mailbox_rf.joblib
```

On a Mac where the same NAS share is mounted, the file might appear as:

```text
/Volumes/frigate/mailbox_rf.joblib
```

These are simply two views of the same file:

```text
macOS
/Volumes/frigate/mailbox_rf.joblib
              │
              │ same NAS file
              ▼
Home Assistant
/media/frigate/mailbox_rf.joblib
```

`/Volumes/frigate` is only an example macOS mount point. It is not required by the project.

---

# 8. Install the local Home Assistant App

Copy this repository folder:

```text
home-assistant-app/mailbox-classifier/
```

to Home Assistant:

```text
/addons/mailbox-classifier/
```

The result should be:

```text
/addons/mailbox-classifier/
├── config.yaml
├── Dockerfile
├── app.py
├── run.sh
└── requirements.txt
```

Do not copy only `app.py`. Home Assistant needs the complete directory in order to build and run the App.

---

## Access `/addons` from macOS with Samba

A convenient method is the Home Assistant **Samba Share** App.

In Finder:

1. press **⌘ K**
2. enter:

```text
smb://<HOME_ASSISTANT_IP>
```

3. authenticate with the credentials configured in Samba Share
4. open the `addons` share
5. copy the `mailbox-classifier` folder into it

Example only:

```text
smb://192.168.0.182
```

Replace that address with the IP address of your own Home Assistant installation.

---

# 9. Configure the App

For a model stored on NAS/network storage:

```yaml
options:
  model_path: "/media/frigate/mailbox_rf.joblib"
  default_image: "/media/current_mailbox.jpg"
```

The App also needs access to Home Assistant's media directory:

```yaml
map:
  - media:rw
```

For the simple `/data` deployment:

```yaml
options:
  model_path: "/data/mailbox_rf.joblib"
  default_image: "/media/current_mailbox.jpg"
```

---

# 10. Install and start the App

After copying the App directory:

1. open Home Assistant
2. go to **Settings → Apps → App Store**
3. reload or refresh the App Store
4. find **Mailbox Classifier**
5. install it
6. start it

The first build may take a little longer because Python packages such as NumPy, scikit-learn, and scikit-image must be installed.

---

# 11. Verify the classifier

Open the Mailbox Classifier App.

The status page should report that the model was loaded successfully.

For example:

```text
Model: /media/frigate/mailbox_rf.joblib
Status: model loaded
```

The App also exposes:

```text
GET /health
```

A successful response looks similar to:

```json
{
  "ok": true,
  "classifier": "hog_color_random_forest",
  "model_loaded": true,
  "model_path": "/media/frigate/mailbox_rf.joblib"
}
```

---

# 12. Classifier API

The main endpoint is:

```text
POST /classify
```

Request:

```json
{
  "image": "/media/current_mailbox.jpg"
}
```

Typical response:

```json
{
  "ok": true,
  "classifier": "hog_color_random_forest",
  "prediction": "occupied",
  "occupied_probability": 0.94,
  "empty_probability": 0.06
}
```

The App also supports:

```text
GET /health
POST /reload
```

`POST /reload` reloads the model from disk without rebuilding the App.

---

# 13. Connect the App to Home Assistant

Add a REST command to Home Assistant's `configuration.yaml`:

```yaml
rest_command:
  mailbox_classifier:
    url: "http://local-mailbox-classifier:8098/classify"
    method: POST
    content_type: "application/json"
    payload: >
      {
        "image": "{{ image }}"
      }
```

If `configuration.yaml` already contains a `rest_command:` section, add `mailbox_classifier:` below the existing commands instead of creating a second `rest_command:` section.

Restart Home Assistant after changing `configuration.yaml`.

> Depending on how the local App is named in your Home Assistant installation, the internal hostname may differ. If the request cannot connect, check the App hostname/network information and use that hostname instead.

---

# 14. Call the classifier from an automation

Take a snapshot first:

```yaml
- variables:
    timestamp: "{{ now().strftime('%Y%m%d_%H%M%S') }}"
    current_image: "/media/frigate/mailbox_dataset/current/mailbox_{{ timestamp }}.jpg"

- action: camera.snapshot
  target:
    entity_id: camera.your_mailbox_camera
  data:
    filename: "{{ current_image }}"
```

Then classify the exact same image:

```yaml
- action: rest_command.mailbox_classifier
  data:
    image: "{{ current_image }}"
  response_variable: classifier_result
```

Extract the result:

```yaml
- variables:
    rf_prediction: "{{ classifier_result.content.prediction }}"
    rf_occupied_probability: >-
      {{ classifier_result.content.occupied_probability | float }}
    rf_occupied_percent: >-
      {{ (classifier_result.content.occupied_probability | float * 100) | round(1) }}
```

You can now react to:

```text
empty
```

or:

```text
occupied
```

Example:

```yaml
- choose:
    - conditions:
        - condition: template
          value_template: "{{ rf_prediction == 'occupied' }}"
      sequence:
        - action: notify.notify
          data:
            title: "Mailbox"
            message: >
              Mailbox occupied probability:
              {{ rf_occupied_percent }} %
```

---

# 15. Archive classified images

Keeping classified images is useful because they become new training data.

For example:

```text
mailbox_dataset/
├── current/
├── empty/
└── occupied/
```

A Home Assistant automation can archive each image into the predicted class.

Later, incorrect classifications can be moved to the correct folder before retraining.

This creates a practical feedback loop:

```text
Run classifier
      ↓
Archive image
      ↓
Review difficult / wrong examples
      ↓
Correct labels
      ↓
Retrain
      ↓
Deploy improved model
```

---

# 16. Updating the model after retraining

One of the main benefits of this architecture is that retraining does not require rebuilding the App.

Train a new model and replace the existing `.joblib`.

For example, on a Mac with the NAS mounted:

```text
/Volumes/frigate/mailbox_rf.joblib
```

Home Assistant sees the same file as:

```text
/media/frigate/mailbox_rf.joblib
```

Then either restart the Mailbox Classifier App or call:

```text
POST /reload
```

The new model becomes active immediately.

In short:

```text
Change Python/App code
        ↓
Rebuild/update Home Assistant App

Retrain Random Forest
        ↓
Replace mailbox_rf.joblib
        ↓
Reload model
```

---

# 17. Troubleshooting

## App does not appear in Home Assistant

Check that the directory is exactly:

```text
/addons/mailbox-classifier/
```

and contains at least:

```text
config.yaml
Dockerfile
app.py
run.sh
requirements.txt
```

Then reload the App Store.

---

## Model not found

Check the configured model path:

```yaml
model_path: "/media/frigate/mailbox_rf.joblib"
```

or:

```yaml
model_path: "/data/mailbox_rf.joblib"
```

Then call:

```text
GET /health
```

and inspect the App logs.

---

## Image not found

The path passed to `/classify` must be visible **inside the App container**.

For images stored under Home Assistant media storage, make sure the App has:

```yaml
map:
  - media:rw
```

and pass a path such as:

```text
/media/current_mailbox.jpg
```

or:

```text
/media/frigate/mailbox_dataset/current/mailbox_20260917_120000.jpg
```

---

## Model loads but classification fails

The most common cause is a mismatch between the feature pipeline used during training and the feature pipeline used by the App.

The following must match:

- image preprocessing
- resize dimensions
- histogram settings
- HOG parameters
- feature order
- number of features

The safest approach is to keep the training and inference `extract_features()` implementation identical.

---

# 18. Security and privacy

All classification can run locally.

No mailbox images need to be uploaded to a cloud service.

Depending on your Home Assistant setup, images, model files, and predictions can stay entirely within your local network.

---

# 19. Ideas for further development

Possible extensions include:

- probability-threshold tuning
- HOG-only vs. HOG+color comparison
- automatic hard-example collection
- model versioning
- confidence logging
- MobileNetV3Small comparison
- per-class performance dashboards
- Home Assistant sensors for classifier confidence
- automatic retraining pipelines
- multi-camera support

---

# License

Add the license that best fits your project, for example MIT.

If you choose MIT, include a `LICENSE` file in the repository.

---

# Acknowledgements

Built as part of a DIY Smart Mailbox project combining embedded hardware, local computer vision, Home Assistant automation, and edge-friendly machine learning.

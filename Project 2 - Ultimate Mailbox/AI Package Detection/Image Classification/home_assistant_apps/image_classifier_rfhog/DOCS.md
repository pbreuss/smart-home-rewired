# Image Classifier RFHOG — Setup and training guide
by Smart Home Rewired
 
Train your own image classifier and use it locally in Home Assistant automations. This guide uses a smart mailbox as the example: a camera takes a photo, the classifier predicts `empty` or `occupied`, and Home Assistant sends a notification when mail is detected.

The tutorial is intentionally basic, so you can train an AI model and learn how it works with little or no programming experience.

Training runs on your computer. The trained model runs in the Home Assistant App. Images do not need to be sent to a cloud AI service.

## Before you begin

You need:

- **Home Assistant OS**, with your camera and door or mail-slot sensor already working.
- The **Home Assistant Companion app** on your phone if you want photo notifications.
- A computer with **Python 3.12** and **Git** installed. Python 3.12 matches the App’s current runtime.
- The **Samba Share** App for the file-transfer method used in this guide, and **File editor** to edit Home Assistant configuration.

Install the Home Assistant Apps under **Settings → Apps → Install App**. Configure Samba Share with a username and password, then start it. Home Assistant’s **Developer tools** are built in; they do not require a separate App. Depending on your version, they may appear as **Settings → Tools**.

This guide covers Home Assistant OS. Home Assistant Container requires running the classifier as a separate container; that setup is outside this guide.

A NAS, Frigate, and Apple HomeKit are optional. They are part of the original mailbox project, but are not required by the classifier.

## 1. Prepare the folders
 
Connect to Home Assistant’s Samba shares from your computer:

- **macOS:** Finder → Go → Connect to Server, then enter `smb://HOME_ASSISTANT_IP`.
- **Windows:** enter `\\HOME_ASSISTANT_IP` in File Explorer’s address bar.

Replace `HOME_ASSISTANT_IP` with your Home Assistant IP address and sign in with your Samba credentials. Open the **media** share.

Create these folders. Paths in this table are how Home Assistant sees them; the `media` share itself corresponds to `/media`.

| Home Assistant path | Purpose |
| --- | --- |
| `/media/image_classifier_rfhog/` | The trained model and its metadata |
| `/media/image_classifier_rfhog/reference_image/` | Images for testing the installed App |
| `/media/mailbox_dataset/current/` | Original camera snapshots |
| `/media/mailbox_dataset/empty/` | Labeled images of an empty mailbox |
| `/media/mailbox_dataset/occupied/` | Labeled images containing mail or packages |

The file `mailbox_rfhog.joblib` will be created during training. Do not create an empty file with that name.

Samba is used here to access your files. The classifier itself will be installed directly from GitHub, so you do not need to copy its source code into `/addons`.

## 2. Collect and label training images

First, make the mailbox work without AI.

1. Open **Settings → Automations & scenes → Create automation** and create an empty automation.
2. Open its menu and choose **Edit in YAML**.
3. Paste the contents of [postbox-closes-automation-no-ai.yaml](https://github.com/pbreuss/smart-home-rewired/blob/main/Project%202%20-%20Ultimate%20Mailbox/Home%20Assistant%20Configuration/postbox-closes-automation-no-ai.yaml).
4. Replace the example door/mail-slot sensors, camera, illumination switch, and mobile notification action with your own.
5. Save the automation and test it by opening and closing the mailbox.

The example assumes sensors report `on` when open and `off` when closed. Adjust the trigger if your sensors behave differently. If your mailbox has no controllable illumination, remove the illumination actions.

Each run should save a photo in `/media/mailbox_dataset/current/` and send a photo notification. Check that the image is clear and shows the mailbox contents. If it is dark or black, fix the lighting or camera exposure before collecting training images.

Collect both empty and occupied examples over several days. Include different envelopes, newspapers, small and large parcels, object positions, lighting conditions, shadows, and reflections. Difficult examples—such as a white envelope against a bright floor—are particularly useful. Keep the two classes reasonably balanced.

Manually copy each usable image into the correct folder:

- **`empty`:** no mail or package is present.
- **`occupied`:** mail, a newspaper, or a package is present.

This is **labeling**: the folder name tells the model the correct answer. Keep each labeled image in only one class folder. Originals can remain in `current`; the notebook reads only `empty` and `occupied`.

Avoid collecting many nearly identical images of the same delivery. Variety matters more than repeated photos of one scene.

## 3. Set up the training tools

On your computer, open Terminal or PowerShell in a folder where you want to download the project:

```bash
git clone https://github.com/pbreuss/smart-home-rewired.git
cd "smart-home-rewired/Project 2 - Ultimate Mailbox/AI Package Detection/Image Classification/training/image_classifier_rfhog_training"
```

Create a virtual environment to keep the training packages separate from other Python software.

**macOS / Linux** — with Python 3.12 installed:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell:**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt in the same folder and run `.venv\Scripts\activate.bat` instead.

With the environment active, install the training packages and open JupyterLab:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-training.txt
python -m jupyterlab
```

JupyterLab opens in your browser. Open `image_classifier_rfhog_training.ipynb` there. This route does not require Visual Studio Code.

## 4. Train and evaluate your model

In the notebook, find the cell containing `DATASET_DIR`, `MODEL_OUT`, and `METADATA_OUT`. Set these to paths **your computer can access**.

For example, on a Mac where the Home Assistant media share is mounted at `/Volumes/media`:

```python
DATASET_DIR = Path("/Volumes/media/mailbox_dataset")
MODEL_OUT = Path("/Volumes/media/image_classifier_rfhog/mailbox_rfhog.joblib")
METADATA_OUT = Path("/Volumes/media/image_classifier_rfhog/mailbox_rfhog_metadata.json")
```

On Windows, if the media share is mapped to drive `M:`:

```python
DATASET_DIR = Path("M:/mailbox_dataset")
MODEL_OUT = Path("M:/image_classifier_rfhog/mailbox_rfhog.joblib")
METADATA_OUT = Path("M:/image_classifier_rfhog/mailbox_rfhog_metadata.json")
```

Use your actual mount location or drive letter. If you train from a local copy instead, set local paths and copy the resulting model into Home Assistant’s media share afterward. Make sure the output folder exists before running the save cell.

Run the notebook cells from top to bottom. The notebook:

1. Loads labeled images and extracts edge, color, and image-statistics features.
2. Splits the images into **80% for training** and **20% for testing**.
3. Trains a Random Forest on the training images.
4. Evaluates predictions on the test images and displays mistakes.
5. Saves the trained model and a metadata file.

Pay particular attention to a **false empty**: mail is present, but the model predicts `empty`. Review the confusion matrix, occupied-class recall, and the displayed mistakes rather than relying on accuracy alone.

The split is made by image. Almost identical photos from the same delivery can therefore end up in both sets and make results look better than they are. Also test with new deliveries photographed after training. The model’s probability is a useful score, not a guarantee that the prediction is correct.

After saving, confirm this file exists in Home Assistant’s media share:

```text
/media/image_classifier_rfhog/mailbox_rfhog.joblib
```

The metadata JSON records training information; the App loads the `.joblib` file.

You can explore the included `mailbox_dataset_demo` first, but train on images from your own camera before using the classifier for your mailbox.

## 5. Install and configure the Home Assistant App

1. In Home Assistant, open **Settings → Apps → Install App**.
2. Open **⋮ → Repositories** and add:

   ```text
   https://github.com/pbreuss/smart-home-rewired
   ```

3. Close the dialog, find **Image Classifier RFHOG** under **Smart Home Rewired**, and select **Install**.
4. Note the App’s displayed hostname for the REST commands in the next step.

Copy one occupied photo and one empty photo into `reference_image`, naming them `ref_image_occupied.jpg` and `ref_image_empty.jpg`. Use actual JPEG images for these filenames.

In the installed App’s **Configuration** tab, enter:

```yaml
model_path: "/media/image_classifier_rfhog/mailbox_rfhog.joblib"
default_image: "/media/image_classifier_rfhog/reference_image/ref_image_occupied.jpg"
```

These are Home Assistant paths, not your computer’s `/Volumes/...` or `M:/...` paths. If the Configuration tab shows separate fields, enter each value in its corresponding field. In its YAML editor, use the example above without an `options:` wrapper.

Save and start the App. Open its web UI and check that it reports **model loaded**. Enable **Start on boot** if you want the classifier available after a reboot.

The App already includes access to Home Assistant’s `/media` directory. You do not need to add a `map:` entry to its Configuration tab.

## 6. Connect Home Assistant to the classifier

Use File editor to open Home Assistant’s `configuration.yaml`. Add:
 
```yaml
rest_command:
  # Classify the requested image, or use the default image if none is supplied.
  image_classifier_rfhog:
    url: "http://32878c6d-image-classifier-rfhog:8098/classify"
    method: POST
    content_type: "application/json"
    payload: >-
      {{ {"image": image | default("")} | to_json }}

  # Load a replacement model after retraining.
  image_classifier_rfhog_reload:
    url: "http://32878c6d-image-classifier-rfhog:8098/reload"
    method: POST

shell_command:
  # Keep the original photo and copy it into the predicted class folder.
  mailbox_archive: 'cp "{{ source }}" "{{ destination }}"'
```

The hostname above is for this repository installation. If your App displays a different hostname, replace it in **both** URLs. These are internal addresses used by Home Assistant, not addresses to open in your computer’s browser.

If you already have a `rest_command:` or `shell_command:` section, merge the new commands into that section. Do not create duplicate top-level sections or replace your existing configuration.

Check the configuration under **Developer tools → YAML** (or **Settings → Tools → YAML**), then restart Home Assistant to load the new commands.

## 7. Test the classifier before enabling AI automation

Open **Developer tools → Actions**, switch to YAML mode, and run:

```yaml
action: rest_command.image_classifier_rfhog
data: {}
```

This uses the configured reference image. A successful response should contain values similar to these; your probabilities will differ:

```yaml
content:
  ok: true
  prediction: occupied
  occupied_probability: 0.9025
  empty_probability: 0.0975
status: 200
```

Next, explicitly test the empty reference image:

```yaml
action: rest_command.image_classifier_rfhog
data:
  image: "/media/image_classifier_rfhog/reference_image/ref_image_empty.jpg"
```

Check that both predictions match what is actually in the images. The reference images are for convenient testing; they do not train or calibrate the model. For a stronger check, also test images that were not used during training.

## 8. Enable classification in your automation

Open the **existing** mailbox-closes automation from Step 2. Replace its YAML with [postbox-closes-automation-ai.yaml](https://github.com/pbreuss/smart-home-rewired/blob/main/Project%202%20-%20Ultimate%20Mailbox/Home%20Assistant%20Configuration/postbox-closes-automation-ai.yaml), then adjust the entity IDs again.

The AI example also uses an exterior indicator light. Replace that entity with yours, or remove those light actions if you do not have one. Its notification title contains a sensor-ID comparison; update that ID too, or use a fixed title.

Keep only one mailbox-closes automation enabled to avoid duplicate runs.

The example takes a snapshot, calls `rest_command.image_classifier_rfhog`, and reads the returned `prediction` and `occupied_probability`. It then:

- **Empty:** copies the image into `empty` and turns off the exterior indicator.
- **Occupied:** copies the image into `occupied`, sends a photo notification, and turns on the indicator.

The original remains in `current` because the archive command uses `cp`.

For photo notifications, distinguish the file path from the URL:

| Use | Example |
| --- | --- |
| Camera snapshot and classifier input | `/media/mailbox_dataset/current/mailbox_20261016_120000.jpg` |
| Notification image URL | `/media/local/mailbox_dataset/current/mailbox_20261016_120000.jpg` |

`local` is part of the URL Home Assistant uses to serve the image. Do not create a folder named `local`.

Test with an empty mailbox and then with mail inside. Trigger each test by opening and closing the actual door or mail slot: the example notification template uses information from that trigger. It sends a notification on every occupied classification, including when previously detected mail is still present.

## 9. Improve the model over time

The archived images provide more training material, but their folder names initially reflect the **model’s predictions**, which can be wrong.

Before retraining, review the images and move incorrect examples into the correct class folder. Exclude unusable images and avoid adding duplicate copies of the same photo.

Then:

1. Run the training notebook again and review its test results.
2. Back up the current model and replace it with the new `mailbox_rfhog.joblib` after saving completes.
3. Run this action:

   ```yaml
   action: rest_command.image_classifier_rfhog_reload
   data: {}
   ```

4. Test both reference images and some new images again.

Restarting the classifier App also loads the replacement model. Retraining does not require rebuilding the App when the feature pipeline and package versions remain compatible. Keep the notebook’s feature extraction consistent with the App’s implementation.

Snapshots and archived copies accumulate over time. Periodically remove images you no longer need, keeping photos available long enough for notification attachments to load.

## Troubleshooting

| Problem | What to check |
| --- | --- |
| App is missing from the store | Add the repository root URL from Step 5 and refresh the store. |
| Model not found | Confirm the file exists and `model_path` exactly matches its Home Assistant path, including `rfhog` in the filename. |
| Image not found | Confirm the image exists under `/media` and use its file path, without the notification URL’s extra `/local`. |
| Cannot connect to the classifier | Check that the App is running and both REST commands use its hostname and port `8098`. |
| Action is missing | Check the YAML and restart Home Assistant after adding the commands. |
| Snapshot fails | Check the camera entity, the existing destination folder, and write permissions. |
| Model loads but classification fails | Read the App logs. Check matching training/runtime dependency versions and identical feature extraction settings. |
| Notification has no image | Check the `/media/local/...` URL, confirm the photo still exists, and verify your phone can reach Home Assistant. |
| Predictions are poor | Inspect lighting, labels, image variety, and false-empty examples. Collect new representative images and retrain. |

For classifier errors, open **Settings → Apps → Image Classifier RFHOG → Logs**. For automation failures, inspect the automation’s **Traces** to see which action failed. The example’s default branch is not an error handler: a failed classifier request can stop the automation before later actions run.

## Further reading

- [Project overview and technical reference](https://github.com/pbreuss/smart-home-rewired/tree/main/Project%202%20-%20Ultimate%20Mailbox/AI%20Package%20Detection/Image%20Classification)
- [Mailbox Home Assistant configuration examples](https://github.com/pbreuss/smart-home-rewired/tree/main/Project%202%20-%20Ultimate%20Mailbox/Home%20Assistant%20Configuration)
- [Home Assistant RESTful Command documentation](https://www.home-assistant.io/integrations/rest_command/)
- [Home Assistant Companion notification attachments](https://companion.home-assistant.io/docs/notifications/notification-attachments/)

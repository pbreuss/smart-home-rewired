# Image Classifier RFHOG
by Smart Home Rewired, Oct 2026

**A lightweight, fully local image-classification Home Assistant App, that can be used to classify images from within an automation.**

In this sample use case the classifier is used to evaluate images taken inside a mailbox triggered by an Home Assistant automation, to determine if the mailbox contains mail.

The classifier combines **Histogram of Oriented Gradients (HOG)** with color and image-statistics features and a **Random Forest classifier (RF)**. 

Training and evaluation is done in a Jupyter notebook (see [training/image_classifier_rfhog_training/image_classifier_rfhog_training.ipynb](training/image_classifier_rfhog_training/image_classifier_rfhog_training.ipynb)), and the trained model can be deployed as a local **Home Assistant App** and called directly from Home Assistant automations.

The project was built as part of a larger Smart Mailbox system using ESP32-CAM components, Home Assistant, Frigate, a Synology NAS, and Apple HomeKit. (see ▶️ [see the Youtube Series "Ultimate Smart Mailbox" part 1, 2, 3](https://www.youtube.com/channel/UChWTRp5MhretkMP-LKyA5-A))

![Smart Mailbox automation](images/mail_automations_status_flow.gif)

This animation shows the flow of two Home Assistant mailbox automations: ‘Door opens’ and ‘Door closes.’ The complete YAML files are available in the [Home Assistant Configuration](../../Home%20Assistant%20Configuration/) folder.

---

## What it does

A camera mounted inside the mailbox captures an image whenever mail may have been delivered (triggered by the mailbox door being closed). The classifier predicts one of two classes:

- `empty`
- `occupied`

When deployed in Home Assistant, the result can be used to:

- send a photo notification
- switch on a mailbox status LED
- update a dashboard
- trigger another automation
- archive images for future retraining

Typical flow Automation "Mail door opens":

```text
Mailbox door / mail slot opens
              │
              ▼
     Turn mailbox LED on
```


Typical flow Automation "Mail door closes":

```text
Mailbox door / mail slot closes
              │
              ▼
     Turn mailbox LED on
              │
              ▼
     Home Assistant snapshot
              │
              ▼
     Turn mailbox LED off
              │
              ▼
      Image Classifier RFHOG App
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

This approach is lightweight, fast, fully local, and does not require cloud inference or a GPU or lots of RAM.

---

# Repository structure

```text
smart-home-rewired / Project 2 - Ultimate Mailbox/AI Package Detection / Image Classification /
│
├── training/image_classifier_rfhog_training/
│   └── image_classifier_rfhog_training.ipynb # use this script to train your model based on your own images
│   └── requirements-training.txt # use this environment for training
│
├── models/
│   └── mailbox_rfhog.joblib        # created after training
│   └── mailbox_rfhog_metadata.json # auto generated, based on the last training run
│
├── home_assistant_apps/
│   └── image_classifier_rfhog/   # this is the app to be installed in Home Assistant
│       ├── config.yaml
│       ├── Dockerfile
│       ├── app.py
│       ├── run.sh
│       └── requirements.txt
│       └── README.md
│       └── DOCS.md
│       ├── images/
│       │   └── mailalgo_final_updated.gif # animated gif to show flow within automations for sample use case
│
└── README.md
```

The important separation is:

- `training/` contains the training pipeline
- DATASET_DIR contains labeled training images (to be setup in the training script)
- `home_assistant_apps/image_classifier_rfhog/` contains the runtime service used inside Home Assistant

---

# Development setup & training

See [Image Classifier RFHOG — Setup and training guide](https://github.com/pbreuss/smart-home-rewired/blob/18cd86a0531d858194b239e884886b42d94c3d2d/Project%202%20-%20Ultimate%20Mailbox/AI%20Package%20Detection/Image%20Classification/home_assistant_apps/image_classifier_rfhog/DOCS.md)



# Security and privacy

All classification can run locally.

No mailbox images need to be uploaded to a cloud service.

Depending on your Home Assistant setup, images, model files, and predictions can stay entirely within your local network.

---

# Ideas for further development

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

The original code and configuration files in this repository are
licensed under the MIT License.

You are welcome to use, modify, and share them for your own projects,
including commercial projects. Please retain the copyright and
license notice.

The software is provided without warranty. Third-party software,
logos, and other assets remain subject to their respective licenses.

---

# Acknowledgements

Built as part of a DIY Smart Mailbox project combining embedded hardware, local computer vision, Home Assistant automation, and edge-friendly machine learning.

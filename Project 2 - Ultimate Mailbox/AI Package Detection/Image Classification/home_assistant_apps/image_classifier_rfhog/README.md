# Image Classifier RFHOG
by Smart Home Rewired, Oct 2026

**A lightweight, fully local image-classification Home Assistant App, that can be used to classify images from within an automation.**

## How it works

The github .. contains instructions and a training ipynb file, that can be used to train your own classifier model based on your own images.

After training according to the instructions (see Docs) copy the trained model to your /media directory in your Home Assistant OS installation (you might need Samba share to get access to the directory of your HA installation).

Setup the path to the model in the config page of this Home Assistant app.

And then, after testing, you can use this classifier in your automations.

Please find detailed setup instructions here.

## Example Use Case

This classifier has been initially developed for a smart mailbox use case (TODO add link) to evaluate images taken inside a mailbox triggered by an Home Assistant automation, to determine if the mailbox contains mail.

It worked so well, such that the developer (Smart Home Rewired) to share its code for others to use it.

## AI theory used in this classifier

The classifier combines **Histogram of Oriented Gradients (HOG)** with color and image-statistics features and a **Random Forest classifier (RF)**. 

Training and evaluation is done in a Jupyter notebook (see [training/image_classifier_rfhog_training/image_classifier_rfhog_training.ipynb](training/image_classifier_rfhog_training/image_classifier_rfhog_training.ipynb)), and the trained model can be deployed as a local **Home Assistant App** and called directly from Home Assistant automations.

The classifier itself only needs images, a trained model, and a Python runtime. Instructions how to install and use this classifier with Home Assistant are below.

The project was built as part of a larger Smxart Mailbox system using ESP32-CAM components, Home Assistant, Frigate, a Synology NAS, and Apple HomeKit. (see ▶️ [see the Youtube Series "Ultimate Smart Mailbox" part 1, 2, 3](https://www.youtube.com/channel/UChWTRp5MhretkMP-LKyA5-A))

---

## Requirements

Currently supports Home Assistant OS


---

## Why HOG + Random Forest?

For many use cases, like checking the content of a mailbox, HOG + Random Forest work perfectly:

A mailbox is a relatively controlled environment:

- the camera position is fixed
- the viewing angle is fixed
- the background changes relatively little
- the classification task is binary

This makes traditional computer-vision features a good fit.

**HOG** captures local edges and shape changes. Color histograms and global image statistics add information about brightness and color distribution.

The **Random Forest** combines those features to distinguish an empty mailbox from letters, newspapers, parcels, and other objects.

This approach is lightweight, fast, fully local, and does not require cloud inference or a GPU or lots of RAM.

---

If you need a more advanced classifier, get in touch with us, and we might develp one.
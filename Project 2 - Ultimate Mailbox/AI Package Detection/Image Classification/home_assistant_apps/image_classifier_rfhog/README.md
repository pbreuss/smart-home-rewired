# Image Classifier RFHOG
by Smart Home Rewired, Oct 2026

**A lightweight, fully local image-classification Home Assistant App, that can be used to classify images from within a Home Assistant.**

---

## How it works

The github linked above contains instructions and a training ipynb file, that can be used to train your own classifier model based on your own images.

After training, copy the trained model to your /media directory in your Home Assistant OS installation.

Setup the path to the model in the Configuration tab of this Home Assistant app.

Then you can use this classifier in Home Assistant, for example inside an automations, when a camera takes a picture, you can classify the image, and take an action based on the result of the classification.

Detailed step-by-step instructions on how to install, train and use this classifier with Home Assistant see the Documentation or the README in the github directory linked above.

---

## Example Use Case - Why you would do this

This classifier has been initially developed for a [smart mailbox use case](https://github.com/pbreuss/smart-home-rewired/tree/main/Project%202%20-%20Ultimate%20Mailbox) to evaluate images taken by a camera inside a mailbox. If the classifier determines that the image contains mail, a notification is sent.

This method worked so well, such that the Smart Home Rewired team decided to share this code, such that other developers can use it as well.

The project was built as part of a larger Smart Mailbox system using ESP32-CAM components, Home Assistant, Frigate, a Synology NAS, and Apple HomeKit. (see ▶️ [see the Youtube Series "Ultimate Smart Mailbox" part 1, 2, 3](https://www.youtube.com/channel/UChWTRp5MhretkMP-LKyA5-A))

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

![Smart Mailbox automation](https://github.com/pbreuss/smart-home-rewired/blob/68c884425924a280dae7160e5a8a10860fce268f/Project%202%20-%20Ultimate%20Mailbox/AI%20Package%20Detection/Image%20Classification/images/mail_automations_status_flow.gif?raw=true)

This animation shows the flow of two Home Assistant mailbox automations: ‘Door opens’ and ‘Door closes.’ The complete YAML files are available in the [Home Assistant Configuration](https://github.com/pbreuss/smart-home-rewired/tree/68c884425924a280dae7160e5a8a10860fce268f/Project%202%20-%20Ultimate%20Mailbox/Home%20Assistant%20Configuration) folder.

---



## Why HOG + Random Forest? AI theory used in this classifier

The classifier combines **Histogram of Oriented Gradients (HOG)** with color and image-statistics features and a **Random Forest classifier (RF)**. Both are standard Machine Learning techniques. Also, this is where "RFHOG" in the name comes from.

For many use cases, like checking the content of a mailbox, HOG + Random Forest work perfectly:

A mailbox is a relatively controlled environment:

- the camera position is fixed
- the viewing angle is fixed
- the background changes relatively little
- the classification task is binary

This makes traditional computer-vision features a good fit.

**HOG** captures local edges and shape changes. Color histograms and global image statistics add information about brightness and color distribution.

The **Random Forest** combines those features to distinguish an empty mailbox from letters, newspapers, parcels, and other objects.

This approach is lightweight, fast, fully local, and does not require cloud inference or a GPU nor lots of RAM.

---

## Requirements

These instructions are for **Home Assistant OS**. If you use **Home Assistant Container**, you’ll need to run the classifier as a separate Docker container. That setup is not covered in this guide.

---

If you need a more advanced classifier, get in touch with us, and we might develop one for you.
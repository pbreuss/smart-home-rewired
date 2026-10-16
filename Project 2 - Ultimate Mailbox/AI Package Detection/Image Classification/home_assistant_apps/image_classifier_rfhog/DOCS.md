# Image Classifier RFHOG - Documentation
by Smart Home Rewired, Oct 2026

**A lightweight, fully local image-classification Home Assistant App based on Random Forest and HOG, that can be used to classify images from within a Home Assistant.**

**This documention describes how you can use Image Classifier RFHOG for your own projects based on the mailbox use case.**

This tutorial is intentionally simple, so you can train your own AI model and learn how it works—even with little or no programming experience. If you get stuck, the way to get support is to ask AI (Google Gemini, ChatGPT, Claude).

Also the Youtube video "Ultimate Smart Mailbox - Part 3 - How to add AI" contains a step-by-step walk-through.

## Prerequisites:

These instructions are for **Home Assistant OS**. If you use **Home Assistant Container**, you’ll need to run the classifier as a separate Docker container. That setup is not covered in this guide.

## STEP 0 - Install necessary apps
Home Assistant --> Services --> Apps --> Install Apps: 
- Samba Share
- File Editor

Home Assistant
[Developer Tools](https://www.home-assistant.io/docs/tools/dev-tools/) are optional, but very useful for debugging

On your Mac or Windows PC, install Visual Studio Code and Python 3.

1. Open a terminal app/Powershell (on your system of choice, Mac, Windows, Linux), cd to a directory of your choice, type 
<code>git clone https://github.com/pbreuss/smart-home-rewired.git</code>
This will download the code to your local machine.

## STEP 1 - Setup the directories for training

As described in the beginning of this [Home Assistant tutorial](https://developers.home-assistant.io/docs/apps/tutorial), use Samba Share to access the directory of your Home Assistant installation. In the Finder (Mac OS) or File Explorer (Windows), find the directory /media. Create the following subdirectories within /media.

```text
/media/
├── image_classifier_rfhog/
│   ├── mailbox_rfhog.joblib   # This will be your trained classifier model
│   └── reference_image/       # Test images: at least one empty and one occupied
│
└── mailbox_dataset/
    ├── current/               # All snapshots are initially saved here
    ├── empty/                 # Images classified as an empty mailbox
    └── occupied/              # Images classified as containing mail or a package
```

## STEP 2 - Setup the Home Assistant automation to collect training images

Go to Settings --> Automations --> Create new automation and name it "Maildoor closes", go to 3 dots on the top right, Edit in Yaml, and then copy [postbox-closes-automation-no-ai.yaml](https://github.com/pbreuss/smart-home-rewired/tree/main/Project%202%20-%20Ultimate%20Mailbox/Home%20Assistant%20Configuration) into this editor.

You will have to adjust this automation such that it is triggered by your own hardware (REED sensor, camera, ..).

The idea is, that based on your triggers, the yaml script postbox-closes-automation-no-ai.yaml saves each new image to the directory named "current".

With this automation, the mailbox is already useful: it sends a notification with an image to your smartphone and also saves each camera image each time the mailbox closes. Each image with mail, and each image with an empty mailbox will later be use for training the classifier.

You can now wait a few of days to collect training images.

After a couple of days, copy all the images with mail to /media/mailbox_dataset/occupied and all the empty images, where you see the empty mailbox to /media/mailbox_dataset/empty. This is called the "labeling step in the training process", because by manually copying each image to the correct directry, you're essentially "assigning a label to each image". 

## STEP 3 - Training a model

1. Open the Terminal/Powershell app, navigate to the directory Project 2 - Ultimate Mailbox/AI Package Detection/Image Classification/training/image_classifier_rfhog_training.

2. Create a virtual environment. A virtual environment keeps the training tools separate from other Python packages on your computer. 

```text
python -m venv image-classifier-rfhog-venv
source image-classifier-rfhog-venv/bin/activate
```

Type into the terminal the following to install packages 
```text
python -m pip install --upgrade pip
python -m pip install -r requirements-training.txt
```

3. code . (This opens VSC)
4. open image_classifier_rfhog_training.ipynb
5. Adjust the path in 
```text
DATASET_DIR = Path("/Volumes/media/mailbox_dataset")
MODEL_OUT = Path("/Volumes/media/image_classifier_rfhog/mailbox_rfhog.joblib")
METADATA_OUT = Path("/Volumes/media/image_classifier_rfhog/mailbox_rfhog_metadata.json")
```
6. Go through all the cells to train model - see the youtube video linked above.

If all goes well, the model in the image_classifier_rfhog has been updated based on your training images.
If you want to test training without your own training images, there is a mailbox_dataset_demo dataset in training/image_classifier_rfhog_training you can use. 


## STEP 4 - Install the Image Classification RFHOG classifier as Home Assistent App

1. In Home Assistant, go to Settings —> Apps —> Install App —> 3 dots —> repositories —> add GitHub url: https://github.com/pbreuss/smart-home-rewired.git
2. Klick the back arrow on the top left, scroll down, find Image Classifier RFHOG under Smart Home Rewired
3. Click on it, and then click install, wait, notice the Hostname and note it down
4. When done, click on Configure, and enter the path to your newly trained model /media/image_classifier_rfhog/mailbox_rfhog.joblib and the path to one of the reference images: /media/image_classifier_rfhog/reference_image/ref_image_occupied.jpg. Make sure that a reference image is in this directory.
5. Go to File Editor and open configuration.yaml - Note: Hostname must match the hostname from above

```text
rest_command:

  ## this is our api call to the image classifier rfhog
  image_classifier_rfhog:
    url: "http://32878c6d-image-classifier-rfhog:8098/classify"
    method: POST
    content_type: "application/json"
    payload: >
      {
        "image": "{{ image }}"
      }

      
shell_command:
  # this command copies the new image from current to either occupied or empty
  mailbox_archive: 'cp "{{ source }}" "{{ destination }}"'

```

6. Restart Home Assistant: In Home Assistant go to Settings --> Tools --> Tab YAML --> click "Check Configuration" --> then click Restart

7. Wait for Home Assistant to be restarted


## STEP 5 - Test your integration

 Test the Image Classifier RFHOG HA app
 1. Go back to Settings —> Apps —> Image Classifier RFHOG —> Click Start
 2. Go to Settings —> Tools —> Actions —> choose action „image_classifier_rfhog“, and copy this to action: „action: rest_command.image_classifier_rfhog“, click perform action

This test calls the imge_classifier_rfhog endpoint with the default image that you supplied in the Configuration tab in the Home Assistant app "Image Classification RFHOG".

 Response should look like this:

```text
content:
  classifier: hog_color_random_forest
  empty_probability: 0.0975
  feature_count: 9809
  image: /media/image_classifier_rfhog/reference_image/ref_image_occupied.jpg
  model_path: /media/image_classifier_rfhog/mailbox_rfhog.joblib
  occupied_probability: 0.9025
  ok: true
  prediction: occupied
  probabilities:
    empty: 0.0975
    occupied: 0.9025
status: 200
headers:
  Server: Werkzeug/3.1.9 Python/3.12.15
  Date: Fri, 16 Oct 2026 07:12:47 GMT
  Content-Type: application/json
  Content-Length: '346'
  Connection: close
```

If not, check log in the Home Assistant app "Image Classification RFHOG".


## STEP 6 - Update your Mail Door Closes automation to use the image classifier

Go to Settings --> Automations --> Choose your "Maildoor closes" automation, go to 3 dots on the top right, Edit in Yaml, and then copy [postbox-closes-automation-ai.yaml](https://github.com/pbreuss/smart-home-rewired/tree/main/Project%202%20-%20Ultimate%20Mailbox/Home%20Assistant%20Configuration) into this editor.


Now you're done! If everything works, when you close the mailbox, you should reive a notification only when the mailbox contains mail, and not after removing the mail.

If you have problems, there is another [README](https://github.com/pbreuss/smart-home-rewired/tree/main/Project%202%20-%20Ultimate%20Mailbox/AI%20Package%20Detection/Image%20Classification) in the github of this project with a Trouble Shooting section at the end.

---




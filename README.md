# Smart Home Rewired

**Build it. Connect it. Make it smart.**

Practical DIY smart home projects combining custom hardware, Home Assistant, ESPHome, and AI. Created by Philipp Breuss-Schneeweis, this project brings together software engineering and hands-on making—from CNC milling and 3D printing to camera integration and machine learning.

The goal is to share how the pieces fit together, explain the decisions behind them, and help you adapt the ideas to your own home.

## Project highlights

### 🪟 Project 1: Wired Windows Alarm System with a Shelly Plus Uni

[![Watch the tutorial on YouTube](https://img.youtube.com/vi/Z5pvdCxU6XdX9ljr/hqdefault.jpg)](https://youtu.be/4L2JkF9nJzo?si=Z5pvdCxU6XdX9ljr)

▶️ [Watch the full tutorial on YouTube](https://youtu.be/4L2JkF9nJzo?si=Z5pvdCxU6XdX9ljr)

### 📬 Project 2: Smart Mailbox

A custom-built mailbox that connects physical deliveries to your smart home.

- CNC-milled wooden construction and 3D-printed camera enclosures.
- ESP32-CAM cameras for viewing the mailbox and capturing its contents.
- Reed sensors for detecting door and mail-slot activity.
- Interior LED lighting for photographs and an exterior indicator for mail.
- Home Assistant automations for snapshots and delivery notifications.
- Camera integration with Frigate, go2rtc, and Apple HomeKit.
- AI classification to distinguish an empty mailbox from one containing mail, using Histogram of Oriented Gradients (HOG) features and a Random Forest classifier.

The accompanying YouTube series covers three parts:

1. Part 1: **Build the mailbox:** CNC milling, 3D printing, and assembly.
2. Part 2: **Make it smart:** sensors, cameras, ESPHome, Home Assistant, and HomeKit integration.
3. Part 3: **Add AI:** training and integrating mailbox content detection. (Coming soon)

### 🔓 Project 3: Fingerprint-controlled garage (coming soon)

Exploring garage access with an ESP32, a UART fingerprint sensor, and a smart garage controller such as iSmartgate. Home Assistant connects fingerprint recognition to garage-door automations.

## Tools and technologies

| Area | Technologies |
| --- | --- |
| Home automation | Home Assistant, ESPHome |
| Hardware | ESP32, ESP32-CAM, reed sensors, LEDs, fingerprint sensors |
| Video | Frigate, go2rtc, RTSP, HomeKit Bridge |
| AI and software | Python, Jupyter notebooks, HOG features, Random Forest |
| Design and fabrication | Autodesk Fusion 360, VCarve, CNC milling, 3D printing |
| Infrastructure | Synology NAS |

## Getting started

Choose the project you want to build and start with its own documentation. Hardware, dependencies, wiring, and configuration vary between projects; there is no single installation command for the whole collection.

For Home Assistant and ESPHome examples:

1. Check the required hardware and pin assignments against your exact board.
2. Adapt entity IDs, network addresses, stream URLs, and credentials to your setup.
3. Keep passwords, API keys, and other credentials out of Git; use `secrets.yaml` where supported.
4. Validate configurations before installing them and test individual components before enabling complete automations.

For the mailbox classifier, start with the classifier project's README and training notebook. Camera position, lighting, and mailbox contents affect results, so train and evaluate with images from your own setup.

## A work in progress

Smart Home Rewired grows alongside the builds and tutorials. Project descriptions show the broader scope; check the files and individual documentation for what is currently available in this repository.

## Contributing

Questions, bug reports, and improvements are welcome. Open an issue with the project name, relevant hardware, software versions, and steps to reproduce the problem. Remove credentials and personal information from logs and configuration files before sharing them.

## Safety

Use suitable power supplies and verify wiring before powering hardware. Work involving mains voltage must be carried out by a qualified electrician. When automating a garage door, retain its safety mechanisms and consider how accidental activation will be prevented.

## Acknowledgements

Thanks to Pioniergarage Salzburg and its community for supporting the Smart Mailbox build with machine training, access to CNC milling and 3D printing, and practical advice.

## Author

**Philipp Breuss-Schneeweis**

Software engineer, AI enthusiast, and maker.

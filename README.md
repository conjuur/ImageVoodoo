<!-- PROJECT SHIELDS -->
<!--
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/conjuur/ImageVoodoo">
    <img src="images\logo_small.jpg" alt="Logo" width="120" height="120">
  </a>

  <h3 align="center">Image Voodoo</h3>

  <p align="center">
    Blender Add-on for Reference Image Manipulation
    <br />
    <a href="https://github.com/conjuur/ImageVoodoo"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://www.youtube.com/channel/UCqTtIrT0I4rDrRZL7wV1tzQ">View Demo</a>
    ·
    <a href="https://github.com/conjuur/ImageVoodoo/issues">Report Bug</a>
    ·
    <a href="https://github.com/conjuur/ImageVoodoo/issues">Request Feature</a>
  </p>
</p>

<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#about-the-project)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)
* [Acknowledgements](#acknowledgements)



<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://www.youtube.com/channel/UCqTtIrT0I4rDrRZL7wV1tzQ)

This program makes it easy to place and scale reference images when importing them 
into a Blender modeling file.

* Please watch the Youtube videos for a step by step starter guide by clicking on the lion above.

<!-- GETTING STARTED -->
## Getting Started

Please make sure Blender is installed.  If you do not have a current installation, please see the link below.  Also, visit the [Installation](#installation) section for directions on how to install Python dependent libraries for use in the Blender environment.

### Prerequisites

Blender is required to run this software.  The link below will take you to the organization's home page.
* [Blender](https://www.blender.org/)
* [OpenCV](https://pypi.org/project/opencv-python/)
* [Pillow](https://pypi.org/project/Pillow/)

###  Installation

1. Create a virtual environment.
2. Activate the environment and install requirements.txt file.
```sh
pip install -r requirements.txt
```
3. Copy the site-packages from the environment into the Blender site-packages folder.
```sh
Blender Foundation -> Blender (version #) -> (version #) -> python -> lib -> site-packages
```

#### Add-On Installation inside of Blender
1. Download ZIP -> [Image Voodoo ZIP](https://github.com/conjuur/ImageVoodoo/archive/main.zip)
2. Extract image-voodoo.py
3. Open Blender session and navigate as below:
```sh
EDIT -> PREFERENCES -> ADD-ONS -> INSTALL
```
4. Select image-voodoo.py and enable it.
5. Add-on will appear on right window bar (also activated by 'n').


<!-- USAGE EXAMPLES -->
## Usage

<br />
<p align="center">
  <a href="https://www.youtube.com/channel/UCqTtIrT0I4rDrRZL7wV1tzQ">
    <img src="images\cla250.jpg" alt="car" width="831" height="446">
  </a>

 - Image placement and scaling as shown above.


<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/conjuur/ImageVoodoo/issues) for a list of proposed features (and known issues).



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.


<!-- LICENSE -->
## License

Distributed under the GNU General Public License v3.0 License. See `LICENSE` for more information.



<!-- CONTACT -->
## Contact

Matt Myers - [@conjuur](https://twitter.com/conjuur) - conjuur@gmail.com

Project Link: [https://github.com/conjuur](https://github.com/conjuur)



<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

Best-README-Template
* [othneildrew](https://github.com/othneildrew/Best-README-Template)






<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=flat-square&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/matt-myers-826a2b


[product-screenshot]: images/lion_demo.jpg
[product-screenshot2]: images/cla250.jpg

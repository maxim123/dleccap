# dleccap
Download CAEN and LSA-ISS Lecture recordings

## Installation

* Download `dleccap.py` or clone the repository with

  ```
  git clone https://github.com/maxim123/dleccap.git
  ```


* Install dependencies

  ```
  pip install requests
  pip install wget
  pip install beautifulsoup4
  ```

## Usage

* Run with

  ```
  python dleccap.py
  ```

* When asked to input the URL of the recordings site, enter the URL of the Lecture Recordings page on CTools if the access to recordings is restricted to a CTools site. The URL should look like

  ```
  https://ctools.umich.edu/portal/site/123/page/456
  ```
  
* Otherwise, enter the URL of *any* recording in the series, or the URL of the recordings site, in any of these formats:

  ```
  https://leccap.engin.umich.edu/leccap/site/123 or
  https://leccap.engin.umich.edu/leccap/viewer/r/123 or
  https://leccap.engin.umich.edu/leccap/viewer/s/123
  ```

* Support for recordings published to Canvas sites coming in the future!

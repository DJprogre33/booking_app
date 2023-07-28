<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/DJprogre33/booking_app">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">Hotel booking API</h3>

  <p align="center">
    High perfomance booking web service
    <br />
    <a href="https://github.com/DJprogre33/booking_app"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/DJprogre33/booking_app">View Demo</a>
    ·
    <a href="https://github.com/DJprogre33/booking_app/issues">Report Bug</a>
    ·
    <a href="https://github.com/DJprogre33/booking_app/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

![Product Name Screen Shot][product-screenshot]

Welcome to the Hotel Booking API repository!

The Hotel Booking API is a high-performance web service designed to provide a convenient and reliable way to book hotels. The API offers a variety of methods for searching, viewing, and booking hotels, as well as managing customer and booking data.

Key Features:
* Hotel Search: Easily search for hotels based on various criteria such as city, check-in and check-out dates, number of guests, and more.
* Hotel Information: Access detailed information about each hotel, including room prices, available amenities, and customer reviews.
* Booking Management: Book hotels by providing customer details, stay period, and other relevant information.
* Booking Modification: Modify or cancel existing bookings as per your requirements.
* Authentication and Authorization: Securely authenticate and authorize users for specific actions.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With


* [![Python][Python.org]][Python-url]
* [![FastAPI][Fastapi.com]][Fastapi-url]
* [![Sqlalchemy][Sqlalchemy.com]][Sqlalchemy-url]
* [![Postgresql][Postgresql.org]][Postgresql-url]
* [![Redis][Redis.io]][Redis-url]
* [![Celery][Celery.dev]][Celery-url]
* [![Docker][Docker.com]][Docker-url]
* [![Prometheus][Prometheus.io]][Prometheus-url]
* [![Grafana][Grafana.io]][Grafana-url]


<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

This repository contains a project that can be deployed using Docker for easy and portable environment management. This guide will show you how to run the project using Docker.
To get a local copy up and running follow these simple example steps.

### Prerequisites

Before getting started, make sure you have the following components installed:

* Docker: Install Docker on your system by following the instructions at https://docs.docker.com/get-docker/.
* Docker Compose: If you don't have it already, install Docker Compose by following the instructions at https://docs.docker.com/compose/install/.

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/DJprogre33/booking_app.git
   cd your-repo
   ```
2. Create an .env file with the required environment variables:
   ```sh
   cp .env.example .env
   ```
3. Build and start the containers using Docker Compose:
   ```sh
   docker-compose up -d --build
   ```
   This command will build all the containers and run them in the background. If all configurations are correct, you should see your application running and ready to use.

4. Open your web browser and navigate to http://localhost:9000 (depending on the docker compose file settings). You should see your application up and running in the browser.
5. Visit http://localhost:9000/docs to access Swagger documentation
6. If you want to stop and remove the containers, run the following command:
   ```sh
   docker-compose down
   ```
<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- ROADMAP -->
## Roadmap

- [X] Add monitoring with Prometheus and Grafana
- [ ] Add endpoint to upload data in csv format
- [ ] Add a more detailed description of Swagger documentation
- [ ] Add custom admin panel

See the [open issues](https://github.com/DJprogre33/booking_app/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Nikita - smirnovniki119@gmail.com

Project Link: [https://github.com/DJprogre33/booking_app](https://github.com/DJprogre33/booking_app)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[product-screenshot]: images/screenshot.png
[Python.org]: https://img.shields.io/badge/Python-000000?style=for-the-badge&logo=Python&logoColor=white
[Python-url]: https://www.python.org/
[Fastapi.com]: https://img.shields.io/badge/fastapi-20232A?style=for-the-badge&logo=fastapi&logoColor=white
[Fastapi-url]: https://fastapi.tiangolo.com/
[Sqlalchemy.com]: https://img.shields.io/badge/SQLALCHEMY-35495E?style=for-the-badge&logoColor=white
[Sqlalchemy-url]: https://www.sqlalchemy.org/
[Postgresql.org]: https://img.shields.io/badge/postgresql-DD0031?style=for-the-badge&logo=postgresql&logoColor=white
[Postgresql-url]: https://www.postgresql.org/
[Redis.io]: https://img.shields.io/badge/redis-4A4A55?style=for-the-badge&logo=redis&logoColor=white
[Redis-url]: https://redis.io/
[Celery.dev]: https://img.shields.io/badge/celery-FF2D20?style=for-the-badge&logo=celery&logoColor=white
[Celery-url]: https://docs.celeryq.dev/en/stable/
[Docker.com]: https://img.shields.io/badge/docker-563D7C?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/
[Prometheus.io]: https://img.shields.io/badge/prometheus-3884FF?style=for-the-badge&logo=prometheus&logoColor=white
[Prometheus-url]: https://prometheus.io/
[Grafana.io]: https://img.shields.io/badge/grafana-2450B2?style=for-the-badge&logo=grafana&logoColor=white
[Grafana-url]: https://grafana.com/